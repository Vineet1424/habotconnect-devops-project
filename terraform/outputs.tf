output "raw_landing_bucket_url" {
  value       = google_storage_bucket.raw_landing.url
  description = "URL of the D0 Raw Landing bucket"
}

output "staged_dataset_id" {
  value       = google_bigquery_dataset.staged_enforced.dataset_id
  description = "BigQuery dataset ID for D1 Staged/Enforced data"
}

output "ingestion_service_account" {
  value       = google_service_account.ingestion_sa.email
  description = "Service account permitted to write to the raw landing bucket"
}
