# AGENTS.md

## Scope

These instructions apply to the entire repository unless a closer nested `AGENTS.md` or `AGENTS.override.md` provides more specific guidance.

## Repository Role

`EV4-Project-Gate` is the planned cross-repository workflow and compatibility control center for:

```text
EV4-Architect-Repo
EV4-Constructability-Engineer-Repo
EV4-Builder-Assistant-Repo
EV4-Responsive-Architect
```

The specialist repositories remain authoritative for their own schemas, validators, adapters, fixtures, and domain behavior.

This repository owns cross-repository verification orchestration, gate configuration, report and evidence formats, package container formats, the user-facing stage state, Project Gate CI, and now the initial deterministic Python foundation for Stage Evidence Bundle validation.

## Current Status

```yaml
python_deterministic_core: implemented_initial_v1
stage_bundle_validation: implemented_initial_v1
structured_diagnostics: implemented_initial_v1
canonical_json_sha256: implemented_initial_v1
real_stage_transitions: not_implemented
cross_repository_validation: not_implemented
user_interface: not_implemented
canonical_schema_owner: false
runtime_dependency_of_specialist_repos: false
node_skeleton: preserved_temporarily
```

Do not describe planned transitions, real cross-repository validation, or UI behavior as implemented behavior.

## Read First

1. `README.md`
2. `docs/ROLE_BOUNDARY_MAP.md`
3. `docs/CONTRACT_INVENTORY.md`
4. `docs/COMPATIBILITY_MAP.md`
5. `docs/VALIDATION_STRATEGY.md`
6. `schemas/stage-bundle/stage-bundle.v1.schema.json`
7. `schemas/transition-result/transition-result.v1.schema.json`
8. `src/ev4_transition/*`
9. `tests/*`
10. the exact producer and consumer contracts in the owning repositories, when reviewing future transition PRs

Older documents about canonical promotion or the previous shared-contract skeleton are historical when they conflict with `README.md` or this file.

## Planned Workflow

```text
Architect output
→ Gate
→ CE output
→ Gate
→ Builder output and build evidence
→ Gate
→ Responsive output and viewport evidence
→ final Gate
```

Each gate eventually produces either:

- an accepted next-stage package built only from validated evidence; or
- a repair package based on confirmed diagnostics.

Repair ownership remains unresolved unless contracts and evidence establish it.

## Hard Boundaries

Do not:

- copy specialist schemas into this repository as competing canonical contracts;
- invent missing fields, identifiers, units, breakpoints, values, relationships, or evidence;
- auto-repair specialist outputs;
- select a winning schema or architectural authority;
- silently normalize undocumented differences;
- mark a stage accepted without executed evidence;
- hide known incompatibilities because a decision record exists;
- claim real EV4 transition compatibility from the foundation validator alone;
- remove or disable the legacy Node skeleton until a dedicated retirement PR proves parity.

When a conclusion cannot be established, use:

```yaml
status: insufficient_evidence
missing_evidence: explicit
repair_owner: unresolved
```

## Python Implementation Rules

- Preserve public contracts unless a breaking change is explicitly approved.
- Isolate repository/network access behind mockable interfaces.
- Use stable ordering and versioned canonical JSON.
- Use SHA-256 over canonical UTF-8 content.
- Reject NaN and infinities.
- Do not inject live timestamps in deterministic core logic.
- If timestamps are accepted, require explicit RFC3339 UTC input.
- Use deterministic diagnostic codes, ordering, and paths.
- Validate every emitted validation-result object against its schema.
- Add stable fixtures and tests for every implemented rule.
- Label synthetic fixtures as synthetic.
- Do not implement future transition features unless explicitly requested.

## Validation

Current Python foundation checks:

```bash
python -m pip install -e '.[dev]'
pytest
ev4-transition validate fixtures/valid/architect-stage-bundle.v1.json
ev4-transition validate fixtures/invalid/array-input.v1.json
ev4-transition validate fixtures/insufficient-evidence/architect-stage-bundle.v1.json --format persian
```

Existing Node skeleton checks remain available temporarily:

```bash
npm run status
npm run validate
```

The GitHub workflow must keep both the existing skeleton health checks and the Python foundation checks until Node retirement is handled in a later PR.

## User Experience Boundary

The normal user is non-technical. The primary interaction is planned as upload, check, and download.

User-facing summaries are Persian and must clearly distinguish accepted, repair-needed, and insufficient-evidence states. Meaning must not depend on color alone. Technical identifiers and evidence remain available as optional details.

## Evidence States

Use explicit states:

```text
observed
exported
validated
resolved
derived
proposed
unverified
insufficient_evidence
```

Every factual compatibility conclusion must trace to explicit input, pinned repository refs, exact paths, official validators/adapters, fixtures, deterministic rule results, or retained execution evidence.

## Pull Requests

A PR must state:

- required change versus optional recommendation;
- repositories and contract boundaries affected;
- compatibility and versioning impact;
- tests and checks actually executed;
- fixtures or reports added or changed;
- remaining unverified behavior or missing evidence.

Avoid unrelated refactoring and never claim validation without executed evidence.
