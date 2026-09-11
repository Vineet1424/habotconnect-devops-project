variable "project_id" {
  type        = string
  description = "GCP project ID for the staging environment"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region for resource provisioning"
}

variable "raw_landing_bucket_name" {
  type        = string
  description = "Globally unique name for the D0 Raw Landing GCS bucket"
}

variable "staging_dataset_id" {
  type        = string
  default     = "d1_staged_enforced"
  description = "BigQuery dataset ID for D1 Staged/Enforced data"
}

variable "authorized_analyst_group" {
  type        = string
  description = "Google Group email authorized for row-scoped read access to staged data"
}
