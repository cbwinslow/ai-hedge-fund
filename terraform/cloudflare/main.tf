resource "cloudflare_record" "openbb" {
  zone_id = var.cloudflare_zone_id
  name    = var.record_name
  value   = var.record_content
  type    = "CNAME"
  ttl     = 3600
  proxied = true
}
