# EV4 Validation Strategy

This document defines validation strategy for EV4 Project Gate.

The active implementation includes the deterministic Python foundation, Stage Evidence Bundle envelope validation, and the first narrow synthetic-verified transition: `ev4-architect-to-ce-transition@1.0.0`.

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
- Architect-to-CE transition-result schema enforcement;
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

## Architect-to-CE Transition Validation

The first active transition is:

```text
ev4-architect-to-ce-transition@1.0.0
```

It validates:

- source Stage Evidence Bundle envelope;
- exact source stage and payload identity;
- pinned external contract file hashes;
- Architect payload schema from the Architect repository;
- deterministic Architect-to-CE mapping without semantic derivation;
- CE intake schema from the CE repository;
- target CE Stage Evidence Bundle envelope;
- Architect-to-CE transition result schema;
- official Architect validator and official CE intake validator in CLI/CI.

Required pinned local checkouts:

```text
rezahh107/EV4-Architect-Repo@b0651668b97f682bb17f66840c8e8c503fd3935d
rezahh107/EV4-Constructability-Engineer-Repo@d3aadff91d9b6fcb38e2f5d3f4cbc2870484b0f7
```

## Local Schema Validation

The active schemas in this repository are Project Gate envelope/result schemas only:

```text
schemas/stage-bundle/stage-bundle.v1.schema.json
schemas/transition-result/transition-result.v1.schema.json
schemas/architect-to-ce-transition-result/architect-to-ce-transition-result.v1.schema.json
```

They are not copied specialist-domain schemas and must not be treated as canonical Architect, CE, Builder, or Responsive contracts.

## Cross-Repo Fixture Validation

Transition PRs must validate against fixtures from the relevant producer and consumer repositories.

Positive fixtures must prove accepted behavior. Negative fixtures must prove boundary rejection.

For Architect-to-CE v1:

```yaml
real_cross_repository_validation: not_available
verification_state: verified_by_synthetic_fixture
```

No real EV4 fixture validation is claimed by this transition.

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

At minimum, transition CI must prove:

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
