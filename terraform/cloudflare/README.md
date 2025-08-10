# Cloudflare Terraform Module

This Terraform configuration demonstrates how to provision a DNS record on Cloudflare.

## Usage

```sh
export TF_VAR_cloudflare_api_token="<token>"
export TF_VAR_cloudflare_zone_id="<zone_id>"
export TF_VAR_record_name="openbb"
export TF_VAR_record_content="example.com"
terraform init
terraform apply
```
