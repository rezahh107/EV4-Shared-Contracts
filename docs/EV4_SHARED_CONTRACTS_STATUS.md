# EV4 Shared Contracts Status

## 1. Current Status Summary

```text
EV4-Shared-Contracts currently exists as a non-authoritative skeleton.
Canonical schema migration remains blocked.
The skeleton branch is initialized and locally verified.
GitHub Actions / CI evidence is pending for the latest agent-guidance update until verified.
```

- Repository: `rezahh107/EV4-Shared-Contracts`
- Current branch: `init/non-authoritative-skeleton`
- Current baseline commit: `f1595091474eacd9d58e8a3f92e364f980c08e58`
- Previous status-dashboard commit: `0233e677adfef0a27d32c16d004382a765eb5aca`
- Status: `skeleton verified with limitations`
- Canonical migration: `blocked`
- CI status: `pending for latest update until Skeleton Health evidence is available`

## 2. Mental Model

چهار repo اصلی EV4 مثل چهار کارگاه جدا هستند.

`EV4-Shared-Contracts` مثل دفتر مرکزی تازه‌ساخته است. فعلاً این دفتر فقط نقشه‌ها، چک‌لیست‌ها، inventory و قوانین promotion را نگه می‌دارد.

هنوز اداره رسمی ثبت schemaها نیست.

## 3. Completed Work

- [x] Cross-repo drift was audited.
- [x] Patch 1 — Cross-Repo Role Alignment was implemented.
- [x] Patch 1 hardening was statically confirmed.
- [x] Architect direct-to-Builder execution was downgraded.
- [x] CE role as execution gate was clarified.
- [x] Builder runtime intake ownership was clarified.
- [x] Responsive Golden Reference family/scope linkage was added.
- [x] EV4-Shared-Contracts repository was created by the user.
- [x] Non-authoritative skeleton was initialized.
- [x] Skeleton local checks passed.
- [x] No canonical schemas were migrated.
- [x] Existing EV4 repos were not modified during skeleton initialization.
- [x] Project status dashboard was added.
- [x] Repository-level agent guidance was added in `AGENTS.md`.

## 4. Known Limitations / Risks

- [!] Full CI evidence across all four EV4 repos is incomplete.  
  The ecosystem-wide validation set is still incomplete, so promotion cannot rely on full cross-repo CI evidence yet.

- [!] EV4-Shared-Contracts skeleton CI must be checked after each new commit.  
  Do not report the latest branch state as CI-verified until the matching `Skeleton Health` run is visible and successful.

- [!] ev4-builder-context-package@1.0.0 still has historical split risk.  
  This contract/version name has carried different producer and consumer assumptions historically.

- [!] Canonical schema migration is not allowed yet.  
  Shared schemas must wait for checklist approval, CI evidence, migration plan, rollback guidance, and promotion ADR.

- [!] Builder/CE adapter boundary still exists.  
  CE-to-Builder normalization remains a boundary that must be preserved until a safe shared contract is promoted.

## 5. Phase Checklist

| Phase | Goal | Status | Mental Image | Next Action |
|---|---|---|---|---|
| Phase 0 — Cross-repo role alignment | align Architect, CE, Builder, Responsive roles | mostly done, CI incomplete | road signs between workshops were corrected | no conceptual hardening unless CI reveals issues |
| Phase 1 — Shared repo skeleton | create non-authoritative coordination repo | initialized and locally verified | central office building created, but not legal archive yet | open PR and get CI evidence |
| Phase 2 — Skeleton PR and merge | review and merge skeleton into main | pending | office documents are waiting for approval stamp | PR from init/non-authoritative-skeleton to main |
| Phase 3 — Status-driven continuation | continue from this document in a new chat | this document creates the handoff anchor | project map pinned to the wall | use `AGENTS.md` and this file as first context in the new chat |
| Phase 4 — Minimal shared governance | add only low-risk shared policies and vocabulary | future | office creates naming rules before accepting legal documents | propose minimal governance, not schema migration |
| Phase 5 — First promotion candidate | choose one safe contract/concept for future promotion proposal | future | one document is reviewed before entering the archive | choose low-risk candidate; avoid `ev4-builder-context-package@1.0.0` first |
| Phase 6 — Canonical migration | migrate canonical schemas only after evidence | blocked | legal archive opens only after all locks are tested | wait for full CI and promotion approval |

## 6. Do / Do Not Rules

Do:

- keep `EV4-Shared-Contracts` non-authoritative for now
- use checklists before migration
- require CI evidence before promotion
- document mental model after each phase
- update this status file after each completed phase
- read `AGENTS.md` first when an AI coding agent connects to this repo

Do not:

- do not migrate schemas yet
- do not make this repo source of truth yet
- do not touch the four existing EV4 repos from this branch
- do not promote `ev4-builder-context-package@1.0.0` first
- do not claim CI passed without workflow evidence

## 7. Next Immediate Step

Open PR:

```text
init/non-authoritative-skeleton → main
```

Then:

```text
Wait for GitHub Actions / Skeleton Health result.
If CI passes, merge skeleton.
If CI does not trigger, report CI_NOT_TRIGGERED.
If CI fails, fix only skeleton-health issues.
```

## 8. New Chat Handoff Prompt

```text
You are helping me continue the EV4-Shared-Contracts workflow.

Read AGENTS.md first.
Then read docs/EV4_SHARED_CONTRACTS_STATUS.md as the current source of project status.

Do not perform canonical schema migration unless the status file says all promotion blockers are resolved.

First, summarize:
1. current status
2. next immediate action
3. blocked actions
4. mental model

Then wait for my next instruction.
```

## 9. Update Protocol

After every completed phase, update this file:

```text
- mark the phase checkbox/status
- add commit SHA
- add validation/CI evidence
- add one simple mental model
- update next action
```

## 10. Final Guardrail

```text
Canonical migration remains blocked until explicitly unlocked by checklist, CI evidence, and promotion ADR.
```
