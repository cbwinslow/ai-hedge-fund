resource "cloudflare_record" "openbb" {
  zone_id = var.cloudflare_zone_id
  name    = var.record_name
  value   = var.record_content
variable "record_type" {
  description = "The type of DNS record to create (e.g. A, AAAA, CNAME, TXT, etc.)"
  type        = string
  default     = "CNAME"
}

resource "cloudflare_record" "openbb" {
  zone_id = var.cloudflare_zone_id
  name    = var.record_name
  value   = var.record_content
  type    = var.record_type
  ttl     = 3600
  proxied = true
  ttl     = var.record_ttl
  proxied = true
}


variable "record_ttl" {
  description = "The TTL value for the DNS record."
  type        = number
  default     = 3600
  proxied = var.cloudflare_record_proxied
}


variable "cloudflare_record_proxied" {
  description = "Whether the Cloudflare DNS record should be proxied (orange cloud)."
  type        = bool
  default     = true
}
