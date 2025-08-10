output "record_id" {
  description = "ID of the created DNS record"
  value       = cloudflare_record.openbb.id
}
