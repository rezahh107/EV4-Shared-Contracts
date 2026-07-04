# EV4 Project Gate Diagnostic Codes

Status: `PROMPT-01` baseline registry for Project Gate-owned diagnostics.

## Schema

Diagnostics are validated by:

```text
schemas/diagnostic/diagnostic.v1.schema.json
```

Required fields:

```yaml
code: UPPERCASE_SNAKE_CASE
severity: error | warning | info | insufficient_evidence
message: non-empty human-readable text
path: JSON path-like location
details: optional object
```

## Core diagnostics

| Code | Severity | Owner | Meaning |
|---|---|---|---|
| `INPUT_NOT_OBJECT` | `error` | Project Gate | Stage Evidence Bundle input is not a JSON object. |
| `MALFORMED_JSON` | `error` | Project Gate | Input file is not valid JSON. |
| `FILE_READ_ERROR` | `error` | Project Gate | Input file could not be read. |
| `SCHEMA_VALIDATION_FAILED` | `error` | Project Gate | Project Gate-owned envelope/result schema validation failed. |
| `NON_FINITE_NUMBER` | `error` | Project Gate | NaN or Infinity was found and rejected. |
| `REQUIRED_EVIDENCE_MISSING` | `insufficient_evidence` | Project Gate | Required evidence id is absent. |
| `BUNDLE_INSUFFICIENT_EVIDENCE` | `insufficient_evidence` | Project Gate | Bundle explicitly declares unresolved or insufficient evidence. |
| `PG_LOCK_SCHEMA_VERSION_MISSING` | `error` | Project Gate | Lock manifest has no schema version. |
| `PG_LOCK_SCHEMA_VERSION_UNKNOWN` | `error` | Project Gate | Lock manifest schema version is unsupported. |
| `PG_LOCK_FILES_NOT_ARRAY` | `error` | Project Gate | Lock manifest `files` is not an array. |
| `PG_LOCK_ENTRY_NOT_OBJECT` | `error` | Project Gate | Lock file entry is not an object. |
| `PG_LOCK_ROLE_INVALID` | `error` | Project Gate | Lock entry role is missing or invalid. |
| `PG_LOCK_ROLE_DUPLICATE` | `error` | Project Gate | Lock manifest contains duplicate roles. |
| `PG_LOCK_FIELD_INVALID` | `error` | Project Gate | Required lock entry field is missing or invalid. |
| `PG_LOCK_HASH_NOT_LOWERCASE` | `error` | Project Gate | Lock file-byte hash is not lowercase hex. |

Architect→CE-specific `PG_A2C_*` diagnostics remain scoped to the existing Architect→CE transition and are not generalized to CE→Builder or Builder→Responsive.
