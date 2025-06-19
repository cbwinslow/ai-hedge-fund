from fastapi import FastAPI, Depends, HTTPException
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import yfinance as yf

from database import SessionLocal, engine
from db_models import Base, Price, Trade, Instrument

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Hedge Fund API")


@app.on_event("startup")
@repeat_every(seconds=60 * 60)
def scheduled_price_fetch() -> None:
    db = SessionLocal()
    try:
        instruments = db.query(Instrument).all()
        for inst in instruments:
            data = yf.download(inst.ticker, period="1d", interval="1d")
            if data.empty:
                continue
            for idx, row in data.iterrows():
                exists = db.query(Price).filter(Price.ticker == inst.ticker, Price.timestamp == idx.to_pydatetime()).first()
                if exists:
                    continue
                price = Price(
                    ticker=inst.ticker,
                    instrument_id=inst.id,
                    timestamp=idx.to_pydatetime(),
                    open=row["Open"],
                    close=row["Close"],
                    high=row["High"],
                    low=row["Low"],
                    volume=int(row["Volume"]),
                )
                db.add(price)
        db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PriceSchema(BaseModel):
    ticker: str
    timestamp: str
    open: float
    close: float
    high: float
    low: float
    volume: int

    class Config:
        orm_mode = True


class InstrumentSchema(BaseModel):
    ticker: str
    type: str
    description: str | None = None
    contract_details: str | None = None

    class Config:
        orm_mode = True


class TradeSchema(BaseModel):
    ticker: str
    action: str
    quantity: int
    price: float


@app.get("/")
async def root():
    return {"message": "AI Hedge Fund API"}


@app.get("/prices/{instrument_type}/{ticker}", response_model=List[PriceSchema])
async def read_prices(instrument_type: str, ticker: str, db: Session = Depends(get_db)):
    instrument = db.query(Instrument).filter(Instrument.ticker == ticker).first()
    if not instrument:
        instrument = Instrument(ticker=ticker, type=instrument_type)
        db.add(instrument)
        db.commit()
        db.refresh(instrument)

    prices = db.query(Price).filter(Price.ticker == ticker).all()
    if not prices:
        data = yf.download(ticker, period="1mo", interval="1d")
        if data.empty:
            raise HTTPException(status_code=404, detail="Ticker not found")
        for idx, row in data.iterrows():
            price = Price(
                ticker=ticker,
                instrument_id=instrument.id,
                timestamp=idx.to_pydatetime(),
                open=row["Open"],
                close=row["Close"],
                high=row["High"],
                low=row["Low"],
                volume=int(row["Volume"]),
            )
            db.add(price)
        db.commit()
        prices = db.query(Price).filter(Price.ticker == ticker).all()
    return prices


@app.post("/trade")
async def place_trade(trade: TradeSchema, db: Session = Depends(get_db)):
    db_trade = Trade(**trade.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return {"status": "ok", "trade_id": db_trade.id}


@app.post("/instruments", response_model=InstrumentSchema)
async def create_instrument(instrument: InstrumentSchema, db: Session = Depends(get_db)):
    db_inst = db.query(Instrument).filter(Instrument.ticker == instrument.ticker).first()
    if db_inst:
        return db_inst
    db_inst = Instrument(**instrument.dict())
    db.add(db_inst)
    db.commit()
    db.refresh(db_inst)
    return db_inst


@app.get("/instruments", response_model=List[InstrumentSchema])
async def list_instruments(db: Session = Depends(get_db)):
    return db.query(Instrument).all()


@app.post("/backtest")
async def run_backtest(tickers: List[str]):
    # Placeholder endpoint
    return {"tickers": tickers}
