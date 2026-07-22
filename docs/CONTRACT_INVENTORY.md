# EV4 Contract Inventory

This inventory describes active boundaries; it does not promote specialist contracts into shared canonical authority.

| Project Gate surface | Owner | External authority consumed | Validation role |
|---|---|---|---|
| Stage Evidence Bundle v1 | Project Gate | Specialist payload schema identified in the bundle | Canonical envelope, provenance, evidence and source-stage validation |
| `ev4-architect-to-ce-transition@1.0.0` | Project Gate | Architect payload/validator; CE mapping/intake/validator | Deterministic Architect → CE projection and result validation |
| `ev4-ce-to-builder-transition@1.0.0` | Project Gate | CE package validator; Builder contract gate, adapter, schema and output validator | Deterministic CE → Builder orchestration, publication and receipt |
| Builder → Responsive transition | Project Gate orchestration | Builder and Responsive pinned contracts; Responsive official validators | Deterministic transition and result validation |
| Final Evidence Gate | Project Gate | Responsive evidence and prior lock chain | Final result, insufficient-evidence and decision receipt validation |
| `ev4-project-gate-kernel-decision-intake@1.0.0` | Project Gate carrier/binding | Pinned `EV4-Decision-Kernel` toolchain and semantics | Intake schema, semantic lock, official Kernel execution and result binding |
| Producer Gate Export v1 | Project Gate common contract | Producer-emitted artifact and producer validator | Exact artifact identity, adoption registry, target routing and dispatch |
| Runtime handoff receipts | Project Gate | Validated transition execution | Source/output binding, publication identity and post-write evidence |
| Capability status v1 | Project Gate | None | Single machine-readable capability truth |

Active lock files under `contracts/locks/` pin exact repositories, commits, paths and relevant file-byte SHA-256 values. The reusable external verifier remains `.github/workflows/verify-vendored-common-contract.yml` and must retain its public `workflow_call` contract.

Historical prompt plans, merge ledgers, CI source archives and manual behavioral-coverage declarations are not active contracts.
