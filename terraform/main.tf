terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# Service Accounts (Least Privilege: separate identity per pipeline stage)
# ---------------------------------------------------------------------------
resource "google_service_account" "ingestion_sa" {
  account_id   = "d0-ingestion-sa"
  display_name = "D0 Raw Landing Ingestion Service Account"
  project      = var.project_id
}

resource "google_service_account" "pipeline_sa" {
  account_id   = "d1-pipeline-sa"
  display_name = "D1 Staging Pipeline Service Account"
  project      = var.project_id
}

# ---------------------------------------------------------------------------
# KMS key for customer-managed encryption of raw landing data
# ---------------------------------------------------------------------------
resource "google_kms_key_ring" "staging_keyring" {
  name     = "staging-keyring"
  location = var.region
  project  = var.project_id
}

resource "google_kms_crypto_key" "raw_landing_key" {
  name            = "raw-landing-key"
  key_ring        = google_kms_key_ring.staging_keyring.id
  rotation_period = "7776000s" # 90 days
}

# ---------------------------------------------------------------------------
# D0 Raw Landing Bucket — untouched incoming data, tightly locked down
# ---------------------------------------------------------------------------
resource "google_storage_bucket" "raw_landing" {
  name                        = var.raw_landing_bucket_name
  location                    = upper(var.region)
  project                     = var.project_id
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.raw_landing_key.id
  }

  public_access_prevention = "enforced"
}

# Only the ingestion identity may write; only the pipeline identity may read.
# No human/user account is granted direct access (Least Privilege).
resource "google_storage_bucket_iam_member" "raw_landing_writer" {
  bucket = google_storage_bucket.raw_landing.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.ingestion_sa.email}"
}

resource "google_storage_bucket_iam_member" "raw_landing_reader" {
  bucket = google_storage_bucket.raw_landing.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# ---------------------------------------------------------------------------
# D1 Staged/Enforced BigQuery Dataset — cleaned, schema-validated data
# ---------------------------------------------------------------------------
resource "google_bigquery_dataset" "staged_enforced" {
  dataset_id                  = var.staging_dataset_id
  project                     = var.project_id
  location                    = upper(var.region)
  delete_contents_on_destroy  = false

  access {
    role          = "OWNER"
    user_by_email = google_service_account.pipeline_sa.email
  }

  # No broad "allUsers"/"allAuthenticatedUsers" access — RBAC only.
  access {
    role           = "READER"
    group_by_email = var.authorized_analyst_group
  }
}

resource "google_bigquery_table" "student_onboarding" {
  dataset_id           = google_bigquery_dataset.staged_enforced.dataset_id
  table_id             = "student_onboarding"
  project              = var.project_id
  deletion_protection  = true

  schema = file("${path.module}/schema/student_onboarding_schema.json")
}

# Row-Level Security: an analyst only sees rows explicitly assigned to them,
# enforced at the database layer (not left to application-code discipline).
resource "google_bigquery_row_access_policy" "region_rls" {
  project               = var.project_id
  dataset_id            = google_bigquery_dataset.staged_enforced.dataset_id
  table_id              = google_bigquery_table.student_onboarding.table_id
  row_access_policy_id  = "assigned_analyst_scoped_access"

  filter_predicate = "assigned_analyst_email = SESSION_USER()"

  grantees = [
    "group:${var.authorized_analyst_group}",
  ]
}
