# PROMPT-06 Theme Readability Repair Handoff

```yaml
patch_id: PROMPT-06-THEME-READABILITY-REPAIR
branch: project-gate-prompt-06-theme-readability
base_branch: main
base_commit: f038a8ca893438dcd793897092c7a36b06e586e2
pre_handoff_head: 959486643eb520275f9594d48e96bfd92e470b43
pull_request: pending_at_handoff_creation
scope:
  - repair operator panel Light/Dark/System readability
  - align EV4 semantic tokens with Gradio theme variables
  - improve Settings modal, disabled state, input, upload, radio, accordion, footer, and button readability
  - add token-level WCAG contrast regression tests
out_of_scope:
  - transition logic changes
  - schema/validator/specialist adapter changes
  - Project Gate status semantics changes
  - production/frontend/Elementor/Responsive readiness claims
files_changed:
  - src/ev4_transition/presentation/theme_tokens.py
  - src/ev4_transition/ui/app.py
  - tests/theme_acceptance/test_theme_tokens.py
  - tests/theme_acceptance/test_operator_panel_theme_tokens.py
  - tests/theme_acceptance/test_operator_panel_theme_contract.py
  - tests/theme_acceptance/test_theme_contrast.py
  - docs/VISUAL_THEME_CONTRACT.md
  - docs/OPERATOR_PANEL_UX_CONTRACT.md
  - docs/OPERATOR_PANEL_MANUAL_QA.md
  - docs/handoffs/PROMPT-06_THEME_READABILITY_REPAIR_HANDOFF.md
commits_created_before_handoff:
  - 0b05f5bd95f47fbc4246ddc36366f9309b2fd192
  - 9699713f5ac62ac9e3f1c2561d2144155b8eff1e
  - 3e48ccf42e5bea58004f80fe68654d5ecee23888
  - fe40c19a58b98c0aab10eb740df1d5e5a1f5b8e5
  - c59de66ded33f5015257d9081dd5decf9571b275
  - fb42c4fe39c43253f447f07a16e3b12c66da2220
  - 10450d011c5bca763f96d72be7433d96e2010734
  - 893b2db3f2e2eb096bf27904fa4a86e99200eaaf
  - 959486643eb520275f9594d48e96bfd92e470b43
tests_run:
  - local sandbox targeted theme tests on reconstructed source: PYTHONPATH=/tmp/ev4patch/src pytest -q /tmp/ev4patch/tests/theme_acceptance
  - local sandbox syntax check: python -m py_compile /tmp/ev4patch/src/ev4_transition/presentation/theme_tokens.py /tmp/ev4patch/src/ev4_transition/ui/app.py
  - local sandbox Gradio theme construction smoke with mocked non-theme modules: operator_gradio_theme(gr) returned Base and operator_panel_css contained required selectors
test_results:
  targeted_theme_tests: 15 passed
  syntax_check: passed
  gradio_theme_smoke: passed in local sandbox with Gradio 6.5.1, while repository dependency range remains gradio>=4,<6
tests_not_run:
  - full repository pytest; container could not clone GitHub due DNS/network failure
  - uv sync --extra dev --extra ui; full checkout unavailable in sandbox
  - browser launch and screenshot QA; connector environment cannot render local browser UI
  - CI; pending after PR creation
coverage_rules_advanced:
  - PG-THEME-001: expanded from token presence/non-inversion to component token coverage for dialog/input/button/disabled/selection/state colors
  - PG-THEME-CONTRAST-001: added token-level contrast ratio tests for text, UI boundary/focus, button, disabled, and status pairs
  - PG-GRADIO-THEME-001: added Gradio theme variable mapping to EV4 semantic tokens
  - PG-THEME-RESOLUTION-001: added explicit light/dark selector support and made system preference a fallback rather than the only driver
coverage_rules_still_gap:
  - Browser/computed-style QA is still manual, not CI-enforced
  - Settings modal readability is statically repaired through Gradio theme mapping and scoped CSS, but screenshot evidence remains pending
  - Accessibility completion remains insufficient_evidence until real browser keyboard/focus and screenshot QA are recorded
new_diagnostics:
  - none
cli_or_ci_changes:
  - none
important_design_decisions:
  - Kept all color values centralized in theme_tokens.py rather than scattered across components
  - Added button.primary.text and input/disabled/dialog tokens to eliminate inherited unreadable Gradio defaults
  - Used gr.themes.Base(...).set(...) for stable Gradio variable mapping and reserved scoped CSS overrides for readability-critical gaps
  - Kept prefers-color-scheme as fallback, while adding explicit data-theme/body light/dark selector support for Gradio/System mode alignment
  - Did not change Project Gate validation logic, transition execution, canonical JSON, hashing, status mapping, or specialist boundaries
web_sources_used:
  - W3C WCAG 2.2 Contrast Minimum and Non-text Contrast
  - Official Gradio theming guide and custom CSS guidance
next_allowed_prompt: PROMPT-06 review/CI/manual screenshot QA, then PROMPT-07 closure audit if accepted
blockers:
  - CI status unknown until PR workflows run
  - manual browser screenshot QA pending for Light/Dark/System and Settings modal
remaining_insufficient_evidence:
  - production readiness
  - real Elementor validation
  - frontend correctness
  - responsive correctness
  - accessibility completion
  - browser screenshot QA
  - computed-style Settings modal verification
```
