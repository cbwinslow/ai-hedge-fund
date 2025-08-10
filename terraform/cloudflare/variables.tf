variable "cloudflare_api_token" {
  type        = string
  description = "Cloudflare API token"
  sensitive   = true
}

variable "cloudflare_zone_id" {
  type        = string
  description = "Cloudflare zone identifier"
}

variable "record_name" {
  type        = string
  description = "DNS record name"
}

variable "record_content" {
  type        = string
  description = "DNS record content"
}
