# Project Gate common-contract vendoring

Producer adoption is pending. A Producer may adopt only after this pull request is merged and the exact merged commit SHA and contract file SHA-256 are recorded.

The lock uses `project-gate-common-contract-lock.v1`. It pins `rezahh107/EV4-Project-Gate`, the exact canonical path, a lowercase 40-character commit SHA, and SHA-256 over exact file bytes. The local copy is non-authoritative. Byte equality is required; moving-default-branch comparison is forbidden. The deterministic verifier reads local files only and never normalizes or repairs them.

A future public caller must use the merged immutable SHA:

```yaml
jobs:
  verify-project-gate-contract:
    uses: rezahh107/EV4-Project-Gate/.github/workflows/verify-vendored-common-contract.yml@<IMMUTABLE_MERGED_COMMIT_SHA>
    with:
      lock_path: contracts/project-gate/producer-gate-export.v1.lock.json
```

Public read-only checkout uses `contents: read` and needs no repository write credential. Cross-repository write or dispatch is outside Prompt 0.
