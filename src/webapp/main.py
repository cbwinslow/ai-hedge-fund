from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import yfinance as yf

from database import SessionLocal, engine
from db_models import Base, Price, Trade

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Hedge Fund API")


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


class TradeSchema(BaseModel):
    ticker: str
    action: str
    quantity: int
    price: float


@app.get("/")
async def root():
    return {"message": "AI Hedge Fund API"}


@app.get("/prices/{ticker}", response_model=List[PriceSchema])
async def read_prices(ticker: str, db: Session = Depends(get_db)):
    prices = db.query(Price).filter(Price.ticker == ticker).all()
    if not prices:
        data = yf.download(ticker, period="1mo", interval="1d")
        if data.empty:
            raise HTTPException(status_code=404, detail="Ticker not found")
        for idx, row in data.iterrows():
            price = Price(
                ticker=ticker,
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


@app.post("/backtest")
async def run_backtest(tickers: List[str]):
    # Placeholder endpoint
    return {"tickers": tickers}

