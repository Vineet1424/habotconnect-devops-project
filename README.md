# HabotConnect — Junior Cloud & DevOps Engineer Hiring Project
Submitted by:Vineet Tiwari

## Scenario recap
A junior developer pushed unencrypted API credentials and caused a schema
mismatch that broke downstream analytics. This submission restores system
integrity across three layers: infrastructure, pipeline, and data contract.

## Task 1 — Terraform Secure Staging Provisioning
File: `terraform/main.tf`, `variables.tf`, `outputs.tf`, `schema/`

- **D0 Raw Landing** (`google_storage_bucket.raw_landing`): uniform bucket-level
  access, public access blocked, customer-managed KMS encryption, versioning
  and a 30-day lifecycle rule.
- **D1 Staged/Enforced** (`google_bigquery_dataset.staged_enforced`): no
  `allUsers`/`allAuthenticatedUsers` access; access is scoped to a named
  service account (write) and an analyst group (read).
- **IAM**: two dedicated service accounts (`d0-ingestion-sa`, `d1-pipeline-sa`)
  so no single identity has both raw-write and staged-read power — Least
  Privilege by separation of duties, not just narrow roles.
- **Row-Level Security**: `google_bigquery_row_access_policy` restricts each
  analyst to rows where `assigned_analyst_email = SESSION_USER()`, enforced
  by BigQuery itself — not by application-layer trust.

## Task 2 — Poka-Yoke CI/CD Build Gate
File: `ci/pipeline.yml`, `ci/.gitleaks.toml`

Three sequential checks — format (Black), lint (Flake8), secret scan
(Gitleaks) — all inside one `build-gate` job. The key "fail-closed" design
choice: **`deploy` only runs `if: needs.build-gate.result == 'success'`**.
There's no default-allow path — if the gate result is anything other than an
explicit success (including a skipped or errored job), deployment is blocked
by default. A separate `quarantine` job fires on failure so the block is
visible in the Actions UI rather than silently disappearing.

## Task 3 — Schema Mapping & DCYN Validation
File: `django/dcyn/validators.py`, `django/serializers.py`, `django/models.py`

- **DCYN library** (`dcyn/validators.py`): DRF's default `BooleanField`
  leniently accepts `"yes"`, `"Y"`, `1`, `"true"`, etc. `DCYNField` overrides
  that to accept *only* the literal JSON booleans `true`/`false` — every
  other representation is rejected, so no human has to interpret intent
  later in the pipeline.
- **Exact field limits**: every field in `StudentOnboardingSerializer` has an
  explicit `max_length`/`min_length`/regex/choice set — nothing relies on
  Django's implicit defaults, and a placeholder-name check
  (`"test"`, `"n/a"`, `"tbd"`, etc.) blocks garbage data at the edge.
- **Cross-field rule**: a specific combination of flags is routed to manual
  review rather than silently accepted — encoding a business judgment call
  as code instead of leaving it to whoever processes the row later.

## How this maps to the "Golden Rules" theme
Each task removes one category of human judgment from the pipeline:
Terraform removes manual console clicks (and the drift/mistakes that come
with them), the CI gate removes "I'll remember to run the linter," and DCYN
removes "I'll interpret what the parent meant by this field."

## Suggested slide outline (max 15 slides)
1. Title + scenario recap
2. Architecture diagram (D0 → D1 → BigQuery, with SAs and IAM boundaries)
3–4. Task 1: Terraform decisions (encryption, IAM, RLS)
5–6. Task 2: pipeline diagram + a screenshot of a deliberately-failing run
7–8. Task 3: DCYN before/after example with a messy payload
9. Cross-field business rule example
10. Trade-offs / what you'd do differently with more time
11. Links to full code repo
