# EV4 Project Gate Diagnostic Codes

Status: `PROMPT-05` adds Builder→Responsive and Final Gate diagnostics. Codes are deterministic and sorted by path/severity/code in emitted results.

## Existing families

- `SCHEMA_VALIDATION_FAILED`
- `MALFORMED_JSON`
- `REQUIRED_EVIDENCE_MISSING`
- `BUNDLE_INSUFFICIENT_EVIDENCE`
- `PG.C2B.*`

## Builder → Responsive: `PG.B2R.*`

| Code | Severity | Meaning |
|---|---|---|
| `PG.B2R.LOCK_NOT_OBJECT` | `error` | Lock manifest is not an object. |
| `PG.B2R.LOCK_VERSION_MISMATCH` | `error` | Lock schema version is missing or unexpected. |
| `PG.B2R.LOCK_TRANSITION_ID_MISMATCH` | `error` | Lock transition id does not match `ev4-builder-to-responsive-transition@1.0.0`. |
| `PG.B2R.LOCK_FILES_NOT_ARRAY` | `error` | Lock `files` is missing or not an array. |
| `PG.B2R.LOCK_ENTRY_NOT_OBJECT` | `error` | A lock entry is not an object. |
| `PG.B2R.LOCK_ROLE_UNEXPECTED` | `error` | Lock contains an unknown role. |
| `PG.B2R.LOCK_ROLE_DUPLICATE` | `error` | Lock contains a duplicate role. |
| `PG.B2R.LOCK_ROLE_MISSING` | `error` | Required lock role is missing. |
| `PG.B2R.LOCK_REPOSITORY_MISMATCH` | `error` | Lock repository differs from expected owner repository. |
| `PG.B2R.LOCK_COMMIT_MISMATCH` | `error` | Lock commit/ref differs from expected owner pin. |
| `PG.B2R.LOCK_PATH_MISMATCH` | `error` | Lock path differs from expected owner path. |
| `PG.B2R.LOCK_IDENTITY_MISMATCH` | `error` | Lock contract/schema id differs from expected identity. |
| `PG.B2R.OWNER_FILE_READ_FAILED` | `insufficient_evidence` | Pinned owner file could not be read from checkout. |
| `PG.B2R.EXTERNAL_HASH_MISMATCH` | `error` | Owner file byte hash differs from lock. |
| `PG.B2R.EXTERNAL_IDENTITY_MISMATCH` | `error` | Expected identity marker is absent from owner file. |
| `PG.B2R.INPUT_NOT_OBJECT` | `error` | Transition input is not an object. |
| `PG.B2R.RESPONSIVE_INPUT_MISSING` | `insufficient_evidence` | Responsive input packet is absent. |
| `PG.B2R.RESPONSIVE_SCHEMA_UNAVAILABLE` | `insufficient_evidence` | Responsive-owned input schema cannot be read. |
| `PG.B2R.RESPONSIVE_SCHEMA_VALIDATION_FAILED` | `error` | Responsive-owned input schema rejects the packet. |
| `PG.B2R.RESPONSIVE_VALIDATOR_MISSING` | `insufficient_evidence` | Official Responsive boundary validator cannot be run. |
| `PG.B2R.RESPONSIVE_VALIDATOR_FAILED` | `insufficient_evidence` | Official Responsive boundary validator exits non-zero. |
| `PG.B2R.BUILDER_EVIDENCE_MISSING` | `insufficient_evidence` | Required Builder evidence refs are missing. |
| `PG.B2R.VIEWPORT_EVIDENCE_MISSING` | `insufficient_evidence` | Desktop/tablet/mobile viewport evidence refs are incomplete. |
| `PG.B2R.RAW_SCREENSHOT_CORRECTNESS_CLAIM` | `insufficient_evidence` | Raw screenshots alone are not correctness evidence. |
| `PG.B2R.CI_FRONTEND_CORRECTNESS_CLAIM` | `error` | CI success is being used as frontend correctness evidence. |
| `PG.B2R.FORBIDDEN_CLAIM` | `error` | Forbidden readiness/correctness claim was found. |
| `PG.B2R.SYNTHETIC_ONLY_EVIDENCE` | `insufficient_evidence` | Synthetic fixture evidence is being used as real evidence. |
| `PG.B2R.ACCEPTED_REQUIRES_MISSING` | `insufficient_evidence` | At least one accepted requirement is false. |

## Final Gate: `PG.FINAL.*`

| Code | Severity | Meaning |
|---|---|---|
| `PG.FINAL.LOCK_NOT_OBJECT` | `error` | Final gate lock manifest is not an object. |
| `PG.FINAL.LOCK_VERSION_MISMATCH` | `error` | Final gate lock schema version is missing or unexpected. |
| `PG.FINAL.LOCK_TRANSITION_ID_MISMATCH` | `error` | Lock gate id does not match `ev4-final-evidence-gate@1.0.0`. |
| `PG.FINAL.LOCK_FILES_NOT_ARRAY` | `error` | Lock `files` is missing or not an array. |
| `PG.FINAL.LOCK_ENTRY_NOT_OBJECT` | `error` | A lock entry is not an object. |
| `PG.FINAL.LOCK_ROLE_UNEXPECTED` | `error` | Lock contains an unknown role. |
| `PG.FINAL.LOCK_ROLE_MISSING` | `error` | Required final gate role is missing. |
| `PG.FINAL.LOCK_REPOSITORY_MISMATCH` | `error` | Lock repository differs from expected owner repository. |
| `PG.FINAL.LOCK_COMMIT_MISMATCH` | `error` | Lock commit/ref differs from expected owner pin. |
| `PG.FINAL.LOCK_PATH_MISMATCH` | `error` | Lock path differs from expected owner path. |
| `PG.FINAL.LOCK_IDENTITY_MISMATCH` | `error` | Lock contract/schema id differs from expected identity. |
| `PG.FINAL.OWNER_FILE_READ_FAILED` | `insufficient_evidence` | Pinned owner file could not be read from checkout. |
| `PG.FINAL.EXTERNAL_HASH_MISMATCH` | `error` | Owner file byte hash differs from lock. |
| `PG.FINAL.EXTERNAL_IDENTITY_MISMATCH` | `error` | Expected identity marker is absent from owner file. |
| `PG.FINAL.INPUT_NOT_OBJECT` | `error` | Final gate input is not an object. |
| `PG.FINAL.RESPONSIVE_OUTPUT_MISSING` | `insufficient_evidence` | Responsive output/evidence packet is absent. |
| `PG.FINAL.RESPONSIVE_SCHEMA_UNAVAILABLE` | `insufficient_evidence` | Responsive-owned output schema cannot be read. |
| `PG.FINAL.RESPONSIVE_SCHEMA_VALIDATION_FAILED` | `error` | Responsive-owned output schema rejects the packet. |
| `PG.FINAL.RESPONSIVE_VALIDATOR_MISSING` | `insufficient_evidence` | Official Responsive output validator cannot be run. |
| `PG.FINAL.RESPONSIVE_VALIDATOR_FAILED` | `insufficient_evidence` | Official Responsive output validator exits non-zero. |
| `PG.FINAL.REAL_EVIDENCE_MISSING` | `insufficient_evidence` | Final real non-synthetic evidence is absent. |
| `PG.FINAL.SYNTHETIC_ONLY_EVIDENCE` | `insufficient_evidence` | Synthetic fixture evidence is being used as final evidence. |
| `PG.FINAL.FORBIDDEN_CLAIM` | `error` | Forbidden readiness/correctness claim was found. |
| `PG.FINAL.CI_FRONTEND_CORRECTNESS_CLAIM` | `error` | CI success is being used as frontend correctness evidence. |
| `PG.FINAL.ACCEPTED_REQUIRES_MISSING` | `insufficient_evidence` | At least one final gate accepted requirement is false. |
