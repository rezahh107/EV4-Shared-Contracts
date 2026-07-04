# EV4 Compatibility Map

This document records current compatibility boundaries only. It does not promote any schema or contract into shared canonical status.

## Architect → CE

Implemented Project Gate transition:

```text
ev4-architect-to-ce-transition@1.0.0
```

Allowed path:

```text
ev4-architect-stage-payload@1.0.0
→ ev4-ce-architect-stage-intake@1.1.0
```

The transition uses the CE-owned mapping contract:

```text
ev4-architect-stage-to-ce-intake-mapping@1.1.0
```

Historical compatibility-only path:

```text
ev4-ce-architect-stage-intake@1.0.0
ev4-architect-stage-to-ce-intake-mapping@1.0.0
```

Blocked paths:

```text
ev4-architect-output-contract@1.0.0
/builder-feed-export
Builder-ready claims before CE processing
```

Validation state:

```yaml
verification_state: synthetic_fixture_only
real_cross_repository_validation: not_available
```

## CE → Builder

Planned Project Gate transition:

```text
ev4-ce-to-builder-transition@1.0.0
```

Implementation status:

```yaml
implemented: false
freeze_matrix: docs/CE_TO_BUILDER_FREEZE_MATRIX.md
```

Allowed future route:

```text
ev4-builder-executable-package@1.0.0
→ Builder CE→Builder Contract Gate
→ Builder CE→Builder adapter
→ ev4-builder-context-package@1.0.0
```

Project Gate later coordinates file-byte pins, hashes, official validators, official adapters, provenance, diagnostics, and handoff packaging for this route. CE and Builder remain the owners of their specialist behavior.

## Builder → Responsive

Planned Project Gate transition:

```text
ev4-builder-to-responsive-transition@1.0.0
```

Implementation status:

```yaml
implemented: false
freeze_matrix: docs/BUILDER_TO_RESPONSIVE_FREEZE_MATRIX.md
builder_formal_responsive_export: not_implemented
responsive_builder_specific_input_schema: not_implemented
```

Allowed future route:

```text
Builder output and build evidence
→ Project Gate file-byte pin/hash and validator orchestration
→ Responsive input boundary
→ Responsive output and viewport evidence
```

The future Project Gate transition may be implemented as a fail-closed verifier. It must not claim an accepted Builder→Responsive handoff until Builder-owned output/evidence artifacts and Responsive-owned input requirements exist and pass the official validators.

## Architect

`ev4-builder-context-package@1.0.0` is deprecated compatibility wrapper only.

`ev4-architect-builder-feed-export@1.0.0` is CE intake / non-executable handoff.

Architect-owned outputs are not Builder-executable output by default.

## Constructability Engineer

`EV4 Builder Executable Package` is the current CE → Builder adapter-side executable handoff.

It is not yet a shared canonical contract.

CE owns constructability review, execution-strategy gate, Builder Executable Package issuance, and execution prerequisites.

## Builder

Builder runtime intake remains local-authoritative inside Builder repo.

CE executable packages are normalized by Builder adapter before runtime use.

Builder rejects Architect-only packages as Builder-ready and rejects CE review-only packages as runtime-ready.

Builder does not yet define a single formal Builder→Responsive export schema. Current Builder action batch, layout check, completion gate, and real Elementor execution evidence artifacts are Builder-owned evidence surfaces only.

## Responsive Architect

Responsive reference-family linkage is local-authoritative inside Responsive repo for now.

It is not yet a canonical shared contract.

Responsive behavior is not inferred from desktop screenshots or raw screenshot authority.

Responsive does not yet define a formal Builder-specific input package schema. Current Builder→Responsive boundary is documented as fail-closed until a formal input package exists or Project Gate transports pinned Builder evidence without treating that transport as Responsive-owned schema.
