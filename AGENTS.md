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

This repository owns only cross-repository verification orchestration, gate configuration, report and evidence formats, package container formats, the user-facing stage state, and Project Gate CI.

## Current Status

```yaml
python_engine: not_implemented
user_interface: not_implemented
stage_gates: planned
canonical_schema_owner: false
runtime_dependency_of_specialist_repos: false
```

Do not describe planned behavior as implemented behavior.

## Read First

1. `README.md`
2. `docs/ROLE_BOUNDARY_MAP.md`
3. `docs/CONTRACT_INVENTORY.md`
4. `docs/COMPATIBILITY_MAP.md`
5. `docs/VALIDATION_STRATEGY.md`
6. the exact producer and consumer contracts in the owning repositories
7. generated reports and evidence bundles, when present

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

Each gate produces either:

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
- hide known incompatibilities because a decision record exists.

When a conclusion cannot be established, use:

```yaml
status: insufficient_evidence
missing_evidence: explicit
repair_owner: unresolved
```

## Implementation Rules

For the future Python verifier:

- preserve public contracts unless a breaking change is explicitly approved;
- isolate repository/network access behind mockable interfaces;
- use stable ordering and versioned canonical JSON;
- use SHA-256 over canonical UTF-8 content;
- reject NaN and infinities;
- use explicit timezone and encoding handling;
- retain subprocess command, exit code, stdout, and stderr evidence;
- use deterministic diagnostic IDs and tie-breakers;
- add stable fixtures and tests for every implemented rule;
- label synthetic fixtures as synthetic.

Do not implement future Phase 2 features unless explicitly requested.

## Validation

Current repository checks:

```bash
npm run status
npm run validate
```

The GitHub workflow also verifies required documentation, package metadata, and that this repository does not contain canonical schema files.

After the Python implementation begins, update this section with the exact install, test, coverage, CLI, and packaging commands. Do not claim Python validation before those commands exist and pass.

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
