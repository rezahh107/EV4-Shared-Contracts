# EV4 Validation Strategy

This document defines validation strategy for EV4 Project Gate.

The current active implementation is limited to the deterministic Python foundation and Stage Evidence Bundle envelope validation. It does not validate real EV4 stage transitions or cross-repository semantic compatibility yet.

## Active Foundation Validation

Current Python checks validate:

- canonical JSON v1 behavior;
- stable SHA-256 over canonical UTF-8 JSON;
- NaN and infinity rejection;
- structured diagnostics;
- malformed JSON values without crashes;
- Stage Evidence Bundle envelope structure;
- explicit `insufficient_evidence`;
- provenance preservation;
- validation-result schema enforcement;
- minimal CLI JSON and Persian output.

Current commands:

```bash
python -m pip install -e '.[dev]'
pytest
ev4-transition validate fixtures/valid/architect-stage-bundle.v1.json
ev4-transition validate fixtures/invalid/array-input.v1.json
ev4-transition validate fixtures/insufficient-evidence/architect-stage-bundle.v1.json --format persian
```

Existing Node skeleton checks remain temporarily available:

```bash
npm run status
npm run validate
```

## Local Schema Validation

The active schemas in this repository are Project Gate envelope/result schemas only:

```text
schemas/stage-bundle/stage-bundle.v1.schema.json
schemas/transition-result/transition-result.v1.schema.json
```

They are not copied specialist-domain schemas and must not be treated as canonical Architect, CE, Builder, or Responsive contracts.

## Cross-Repo Fixture Validation

Future transition PRs must validate against fixtures from the relevant producer and consumer repositories.

Positive fixtures must prove accepted behavior. Negative fixtures must prove boundary rejection.

No real EV4 fixture validation is claimed by the current foundation.

## Contract Compatibility Matrix

A compatibility matrix must define, for each future transition contract:

- owner repo
- producer
- consumer
- schema version
- allowed compatibility path
- blocked compatibility path
- deprecation behavior
- migration status

## Producer/Consumer Contract Tests

No real transition is accepted without at least one producer-side fixture and one consumer-side fixture.

Producer tests must prove the owning repo can emit or carry the contract correctly.
Consumer tests must prove the downstream repo accepts valid input and rejects invalid or premature input.

## CI Requirement

CI evidence is required before schema promotion or transition activation.

At minimum, future transition CI must prove:

- Python package installs
- unit tests pass
- CLI smoke tests pass
- schema files parse
- positive fixtures pass
- negative fixtures fail as expected
- producer validation passes
- consumer validation passes
- cross-repo compatibility tests pass when that transition claims cross-repo compatibility

## Dependency Boundary

No runtime dependency from existing specialist repos until promotion is approved.

Existing EV4 repositories must not import from this repository until an explicit ADR, migration plan, validation evidence, compatibility policy, and rollback guidance are approved.
