# EV4 Project Gate Governance

Active governance now centers on deterministic stage transitions, structured diagnostics, canonical JSON, and evidence provenance.

This repository no longer governs shared-contract promotion. Older promotion or migration material is historical unless a later PR rewrites it for the Project Gate role.

## Active rules

- Python is the primary runtime.
- Transition definitions are versioned under `transitions/`.
- Stage Evidence bundles are validated before transition.
- `insufficient_evidence` is a first-class status.
- The engine must not invent evidence.
- Output JSON must be deterministic and hashable.
