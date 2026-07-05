#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESPONSIVE_COMMIT = "df74c7ba2ffbed1a4136b5ea6be6ce30db4e161a"
FINAL_GATE_COMMIT_MARKER = "__PROMPT05_STAGE1_COMMIT__"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one replacement in {path}, found {count}: {old[:80]!r}")
    write(path, text.replace(old, new, 1))


def append_once(path: str, marker: str, block: str) -> None:
    text = read(path)
    if marker in text:
        return
    if not text.endswith("\n"):
        text += "\n"
    write(path, text + "\n" + block.rstrip() + "\n")


def apply_source_fixes() -> None:
    replace_once(
        "src/ev4_transition/transitions/builder_to_responsive.py",
        'RESPONSIVE_COMMIT = "main"',
        f'RESPONSIVE_COMMIT = "{RESPONSIVE_COMMIT}"',
    )
    replace_once(
        "src/ev4_transition/transitions/final_gate.py",
        'PG_COMMIT = "main"\nRESPONSIVE_REPO = "rezahh107/EV4-Responsive-Architect"\nRESPONSIVE_COMMIT = "main"',
        f'PG_COMMIT = "{FINAL_GATE_COMMIT_MARKER}"\nRESPONSIVE_REPO = "rezahh107/EV4-Responsive-Architect"\nRESPONSIVE_COMMIT = "{RESPONSIVE_COMMIT}"',
    )

    replace_once(
        "src/ev4_transition/transitions/builder_to_responsive.py",
        '        role = item.get("role")\n        expected = EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES.get(role)\n',
        '        role = item.get("role")\n        if not isinstance(role, str):\n            diagnostics.append(diagnostic("PG.B2R.LOCK_ROLE_UNEXPECTED", "error", "Lock entry role must be a string.", f"{path}.role", observed_type=type(role).__name__))\n            continue\n        expected = EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES.get(role)\n',
    )
    replace_once(
        "src/ev4_transition/transitions/final_gate.py",
        '        role = item.get("role")\n        expected = EXPECTED_FINAL_GATE_DEPENDENCIES.get(role)\n',
        '        role = item.get("role")\n        if not isinstance(role, str):\n            diagnostics.append(diagnostic("PG.FINAL.LOCK_ROLE_UNEXPECTED", "error", "Lock entry role must be a string.", f"{path}.role", observed_type=type(role).__name__))\n            continue\n        expected = EXPECTED_FINAL_GATE_DEPENDENCIES.get(role)\n',
    )

    old_b2r = '''def _result(original: Any, responsive_input: dict[str, Any] | None, diagnostics: list[Diagnostic], accepted_requires: dict[str, bool], config: BuilderToResponsiveTransitionConfig) -> dict[str, Any]:
    ordered = sort_diagnostics(diagnostics)
    if not ordered and not all(accepted_requires.values()):
        missing = sorted(k for k, v in accepted_requires.items() if not v and k != "result_schema_valid")
        ordered = sort_diagnostics([diagnostic("PG.B2R.ACCEPTED_REQUIRES_MISSING", "insufficient_evidence", "Accepted status requires every accepted_requires item to be true.", "$.accepted_requires", missing=missing)])
    status = project_gate_status_from_diagnostics(ordered)
    result = {
        "schema_version": "builder-to-responsive-transition-result.v1",
        "result_type": "builder_to_responsive_transition",
        "transition_id": TRANSITION_ID,
        "transition_version": TRANSITION_VERSION,
        "status": status,
        "diagnostics": [d.to_dict() for d in ordered],
        "accepted_requires": {**accepted_requires, "result_schema_valid": True},
        "hashes": {"source_input_hash": {"algorithm": "sha256", "canonicalization": "ev4-canonical-json.v1", "scope": "source_input", "value": _safe_hash(original)}},
        "output": responsive_input if status == "accepted" else None,
    }
    _validate_result_schema(config.schema_root, result)
    return result


def _validate_result_schema(schema_root: Path, result: dict[str, Any]) -> None:
    path = schema_root / "builder-to-responsive-transition-result" / "builder-to-responsive-transition-result.v1.schema.json"
    if not path.exists():
        return
    errors = sorted(Draft202012Validator(load_json_file(path)).iter_errors(result), key=lambda item: (list(item.path), item.message))
    if errors:
        raise RuntimeError("; ".join(f"{_json_path(list(e.path))}: {e.message}" for e in errors))
'''
    new_b2r = '''def _result(original: Any, responsive_input: dict[str, Any] | None, diagnostics: list[Diagnostic], accepted_requires: dict[str, bool], config: BuilderToResponsiveTransitionConfig) -> dict[str, Any]:
    ordered = sort_diagnostics(diagnostics)
    accepted = {**accepted_requires, "result_schema_valid": True}
    if not ordered and not all(accepted.values()):
        missing = sorted(key for key, value in accepted.items() if not value)
        ordered = sort_diagnostics([diagnostic("PG.B2R.ACCEPTED_REQUIRES_MISSING", "insufficient_evidence", "Accepted status requires every accepted_requires item to be true.", "$.accepted_requires", missing=missing)])
    status = project_gate_status_from_diagnostics(ordered)
    result = {
        "schema_version": "builder-to-responsive-transition-result.v1",
        "result_type": "builder_to_responsive_transition",
        "transition_id": TRANSITION_ID,
        "transition_version": TRANSITION_VERSION,
        "status": status,
        "diagnostics": [item.to_dict() for item in ordered],
        "accepted_requires": accepted,
        "hashes": {"source_input_hash": {"algorithm": "sha256", "canonicalization": "ev4-canonical-json.v1", "scope": "source_input", "value": _safe_hash(original)}},
        "output": responsive_input if status == "accepted" else None,
    }
    schema_path = config.schema_root / "builder-to-responsive-transition-result" / "builder-to-responsive-transition-result.v1.schema.json"
    schema_diagnostics: list[Diagnostic] = []
    if not schema_path.exists():
        schema_diagnostics.append(diagnostic("PG.B2R.RESULT_SCHEMA_MISSING", "insufficient_evidence", "Builder→Responsive result schema is required.", "$.schema_version", schema_path=str(schema_path)))
    else:
        try:
            schema = load_json_file(schema_path)
            Draft202012Validator.check_schema(schema)
            errors = sorted(Draft202012Validator(schema).iter_errors(result), key=lambda item: (list(item.path), item.message))
            for error in errors:
                schema_diagnostics.append(diagnostic("PG.B2R.RESULT_SCHEMA_VALIDATION_FAILED", "error", error.message, _json_path(list(error.path))))
        except Exception as exc:
            schema_diagnostics.append(diagnostic("PG.B2R.RESULT_SCHEMA_INVALID", "error", "Builder→Responsive result schema could not be validated.", "$.schema_version", error_type=type(exc).__name__))
    if schema_diagnostics:
        accepted["result_schema_valid"] = False
        ordered = sort_diagnostics([*ordered, *schema_diagnostics])
        result["status"] = project_gate_status_from_diagnostics(ordered)
        result["diagnostics"] = [item.to_dict() for item in ordered]
        result["accepted_requires"] = accepted
        result["output"] = None
    return result
'''
    replace_once("src/ev4_transition/transitions/builder_to_responsive.py", old_b2r, new_b2r)

    old_final = '''def _result(original: Any, output: dict[str, Any] | None, diagnostics: list[Diagnostic], accepted_requires: dict[str, bool], config: FinalGateConfig) -> dict[str, Any]:
    ordered = sort_diagnostics(diagnostics)
    if not ordered and not all(accepted_requires.values()):
        missing = sorted(k for k, v in accepted_requires.items() if not v and k != "result_schema_valid")
        ordered = sort_diagnostics([diagnostic("PG.FINAL.ACCEPTED_REQUIRES_MISSING", "insufficient_evidence", "Accepted final status requires every accepted_requires item to be true.", "$.accepted_requires", missing=missing)])
    status = project_gate_status_from_diagnostics(ordered)
    result = {
        "schema_version": "final-gate-result.v1",
        "result_type": "final_evidence_gate",
        "gate_id": GATE_ID,
        "gate_version": GATE_VERSION,
        "status": status,
        "diagnostics": [d.to_dict() for d in ordered],
        "accepted_requires": {**accepted_requires, "result_schema_valid": True},
        "hashes": {"source_input_hash": {"algorithm": "sha256", "canonicalization": "ev4-canonical-json.v1", "scope": "source_input", "value": _safe_hash(original)}},
        "output": output if status == "accepted" else None,
    }
    _validate_result_schema(config.schema_root, result)
    return result


def _validate_result_schema(schema_root: Path, result: dict[str, Any]) -> None:
    path = schema_root / "final-gate-result" / "final-gate-result.v1.schema.json"
    if not path.exists():
        return
    errors = sorted(Draft202012Validator(load_json_file(path)).iter_errors(result), key=lambda item: (list(item.path), item.message))
    if errors:
        raise RuntimeError("; ".join(f"{_json_path(list(e.path))}: {e.message}" for e in errors))
'''
    new_final = '''def _result(original: Any, output: dict[str, Any] | None, diagnostics: list[Diagnostic], accepted_requires: dict[str, bool], config: FinalGateConfig) -> dict[str, Any]:
    ordered = sort_diagnostics(diagnostics)
    accepted = {**accepted_requires, "result_schema_valid": True}
    if not ordered and not all(accepted.values()):
        missing = sorted(key for key, value in accepted.items() if not value)
        ordered = sort_diagnostics([diagnostic("PG.FINAL.ACCEPTED_REQUIRES_MISSING", "insufficient_evidence", "Accepted final status requires every accepted_requires item to be true.", "$.accepted_requires", missing=missing)])
    status = project_gate_status_from_diagnostics(ordered)
    result = {
        "schema_version": "final-gate-result.v1",
        "result_type": "final_evidence_gate",
        "gate_id": GATE_ID,
        "gate_version": GATE_VERSION,
        "status": status,
        "diagnostics": [item.to_dict() for item in ordered],
        "accepted_requires": accepted,
        "hashes": {"source_input_hash": {"algorithm": "sha256", "canonicalization": "ev4-canonical-json.v1", "scope": "source_input", "value": _safe_hash(original)}},
        "output": output if status == "accepted" else None,
    }
    schema_path = config.schema_root / "final-gate-result" / "final-gate-result.v1.schema.json"
    schema_diagnostics: list[Diagnostic] = []
    if not schema_path.exists():
        schema_diagnostics.append(diagnostic("PG.FINAL.RESULT_SCHEMA_MISSING", "insufficient_evidence", "Final gate result schema is required.", "$.schema_version", schema_path=str(schema_path)))
    else:
        try:
            schema = load_json_file(schema_path)
            Draft202012Validator.check_schema(schema)
            errors = sorted(Draft202012Validator(schema).iter_errors(result), key=lambda item: (list(item.path), item.message))
            for error in errors:
                schema_diagnostics.append(diagnostic("PG.FINAL.RESULT_SCHEMA_VALIDATION_FAILED", "error", error.message, _json_path(list(error.path))))
        except Exception as exc:
            schema_diagnostics.append(diagnostic("PG.FINAL.RESULT_SCHEMA_INVALID", "error", "Final gate result schema could not be validated.", "$.schema_version", error_type=type(exc).__name__))
    if schema_diagnostics:
        accepted["result_schema_valid"] = False
        ordered = sort_diagnostics([*ordered, *schema_diagnostics])
        result["status"] = project_gate_status_from_diagnostics(ordered)
        result["diagnostics"] = [item.to_dict() for item in ordered]
        result["accepted_requires"] = accepted
        result["output"] = None
    return result
'''
    replace_once("src/ev4_transition/transitions/final_gate.py", old_final, new_final)


def write_lock_tools() -> None:
    write(
        "scripts/compute-builder-to-responsive-lock.py",
        '''#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ev4_transition.canonical_json import bytes_sha256, canonical_dumps
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.transitions.builder_to_responsive import (
    BUILDER_REPO,
    EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES,
    LOCK_SCHEMA_VERSION,
    RESPONSIVE_REPO,
    TRANSITION_ID,
)


def compute_lock(builder_repo: Path, responsive_repo: Path) -> dict:
    source = LocalCheckoutContractSource({BUILDER_REPO: builder_repo, RESPONSIVE_REPO: responsive_repo})
    files = []
    for role in sorted(EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES):
        expected = EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES[role]
        content = source.read_bytes(expected.repository, expected.accepted_commit, expected.path)
        files.append({
            "role": expected.role,
            "repository": expected.repository,
            "accepted_commit": expected.accepted_commit,
            "path": expected.path,
            "contract_or_schema_id": expected.contract_or_schema_id,
            "sha256_file_bytes": bytes_sha256(content),
        })
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "transition_id": TRANSITION_ID,
        "hash_state": "computed_from_pinned_owner_file_bytes",
        "hash_algorithm": "sha256_file_bytes",
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute the exact Builder→Responsive owner-file lock.")
    parser.add_argument("--builder-repo", required=True)
    parser.add_argument("--responsive-repo", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = compute_lock(Path(args.builder_repo), Path(args.responsive_repo))
    Path(args.output).write_text(canonical_dumps(payload) + "\\n", encoding="utf-8")
    print(canonical_dumps({"status": "computed", "output": args.output, "roles": [item["role"] for item in payload["files"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
    )
    write(
        "scripts/compute-final-gate-lock.py",
        '''#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ev4_transition.canonical_json import bytes_sha256, canonical_dumps
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.transitions.final_gate import (
    EXPECTED_FINAL_GATE_DEPENDENCIES,
    GATE_ID,
    LOCK_SCHEMA_VERSION,
    PG_REPO,
    RESPONSIVE_REPO,
)


def compute_lock(project_gate_repo: Path, responsive_repo: Path) -> dict:
    source = LocalCheckoutContractSource({PG_REPO: project_gate_repo, RESPONSIVE_REPO: responsive_repo})
    files = []
    for role in sorted(EXPECTED_FINAL_GATE_DEPENDENCIES):
        expected = EXPECTED_FINAL_GATE_DEPENDENCIES[role]
        content = source.read_bytes(expected.repository, expected.accepted_commit, expected.path)
        files.append({
            "role": expected.role,
            "repository": expected.repository,
            "accepted_commit": expected.accepted_commit,
            "path": expected.path,
            "contract_or_schema_id": expected.contract_or_schema_id,
            "sha256_file_bytes": bytes_sha256(content),
        })
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "gate_id": GATE_ID,
        "hash_state": "computed_from_pinned_owner_file_bytes",
        "hash_algorithm": "sha256_file_bytes",
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute the exact Final Evidence Gate lock.")
    parser.add_argument("--project-gate-repo", required=True)
    parser.add_argument("--responsive-repo", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = compute_lock(Path(args.project_gate_repo), Path(args.responsive_repo))
    Path(args.output).write_text(canonical_dumps(payload) + "\\n", encoding="utf-8")
    print(canonical_dumps({"status": "computed", "output": args.output, "roles": [item["role"] for item in payload["files"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
    )


def patch_tests() -> None:
    append_once(
        "tests/transitions/test_builder_to_responsive.py",
        "test_builder_to_responsive_lock_rejects_non_string_role_without_crash",
        '''def test_builder_to_responsive_lock_rejects_non_string_role_without_crash(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    lock["files"][0]["role"] = {"malformed": True}
    diagnostics = verify_builder_to_responsive_lock(lock, source)
    assert any(item.code == "PG.B2R.LOCK_ROLE_UNEXPECTED" for item in diagnostics)


def test_builder_to_responsive_missing_result_schema_is_insufficient_evidence(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    result = transition_builder_to_responsive(_responsive_input(), source, _config(tmp_path, lock, builder, responsive))
    assert result["status"] == "insufficient_evidence"
    assert result["accepted_requires"]["result_schema_valid"] is False
    assert "PG.B2R.RESULT_SCHEMA_MISSING" in _codes(result)
''',
    )
    append_once(
        "tests/transitions/test_final_gate.py",
        "test_final_gate_lock_rejects_non_string_role_without_crash",
        '''def test_final_gate_lock_rejects_non_string_role_without_crash(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    lock["files"][0]["role"] = []
    diagnostics = verify_final_gate_lock(lock, source)
    assert any(item.code == "PG.FINAL.LOCK_ROLE_UNEXPECTED" for item in diagnostics)


def test_final_gate_missing_result_schema_is_insufficient_evidence(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    result = run_final_gate(_output(), source, _config(tmp_path, lock, pg, responsive))
    assert result["status"] == "insufficient_evidence"
    assert result["accepted_requires"]["result_schema_valid"] is False
    assert "PG.FINAL.RESULT_SCHEMA_MISSING" in _codes(result)
''',
    )
    append_once(
        "tests/test_cli.py",
        "test_cli_inspect_reports_prompt05_layered_truth",
        '''def test_cli_inspect_reports_prompt05_layered_truth():
    completed = run_cli("inspect")
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["capabilities"]["builder_to_responsive"] == {
        "orchestration_baseline": "implemented",
        "cli_exposure": "not_implemented",
        "owner_contract_lock": "computed_from_pinned_owner_file_bytes",
        "official_responsive_validator_integration": "implemented",
        "verification_state": "pending_exact_head_ci",
        "real_non_synthetic_handoff": "insufficient_evidence",
    }
    assert payload["capabilities"]["final_evidence_gate"] == {
        "orchestration_baseline": "implemented",
        "cli_exposure": "not_implemented",
        "prior_lock_chain": "pinned_to_immutable_project_gate_commit",
        "official_responsive_validator_integration": "implemented",
        "verification_state": "pending_exact_head_ci",
        "real_non_synthetic_evidence": "insufficient_evidence",
    }
    assert "builder-to-responsive public CLI exposure" in payload["not_implemented"]
    assert "final evidence gate public CLI exposure" in payload["not_implemented"]
    assert "builder-to-responsive" not in payload["public_cli_transitions"]
''',
    )


def write_capability_truth() -> None:
    payload = {
        "schema_version": "ev4-project-gate-capability-status.v1",
        "package": "ev4-project-gate",
        "repository": "rezahh107/EV4-Project-Gate",
        "capabilities": {
            "architect_to_ce": {
                "orchestration_baseline": "implemented",
                "cli_exposure": "implemented",
                "verification_state": "synthetic_fixture_only",
                "real_non_synthetic_handoff": "insufficient_evidence",
            },
            "ce_to_builder": {
                "orchestration_baseline": "implemented",
                "cli_exposure": "not_implemented",
                "owner_fixture_integration": "verified",
                "real_non_synthetic_handoff": "insufficient_evidence",
            },
            "builder_to_responsive": {
                "orchestration_baseline": "implemented",
                "cli_exposure": "not_implemented",
                "owner_contract_lock": "computed_from_pinned_owner_file_bytes",
                "official_responsive_validator_integration": "implemented",
                "verification_state": "pending_exact_head_ci",
                "real_non_synthetic_handoff": "insufficient_evidence",
            },
            "final_evidence_gate": {
                "orchestration_baseline": "implemented",
                "cli_exposure": "not_implemented",
                "prior_lock_chain": "pinned_to_immutable_project_gate_commit",
                "official_responsive_validator_integration": "implemented",
                "verification_state": "pending_exact_head_ci",
                "real_non_synthetic_evidence": "insufficient_evidence",
            },
            "user_interface": {"status": "not_implemented"},
        },
        "public_cli_transitions": ["architect-to-ce"],
        "implemented": [
            "canonical_json",
            "sha256",
            "structured_diagnostics",
            "stage_bundle_validation",
            "transition_result_schema_foundation",
            "status_presentation_mapping",
            "behavioral_coverage_validation",
            "architect-to-ce transition",
            "ce-to-builder orchestration baseline",
            "builder-to-responsive orchestration baseline",
            "final evidence gate orchestration baseline",
            "minimal_cli",
        ],
        "not_implemented": [
            "ce-to-builder public CLI exposure",
            "builder-to-responsive public CLI exposure",
            "final evidence gate public CLI exposure",
            "real EV4 artifact validation",
            "UI",
        ],
        "evidence": {
            "ce_to_builder_owner_fixture_integration": {
                "pull_request": 20,
                "head_sha": "42bfa484481c585f589d86c40424660c70b038a0",
                "workflow_run_id": 28744810186,
                "workflow": "Skeleton Health",
                "result": "success",
                "scope": "owner_fixture_integration_only",
            },
            "last_verified_project_gate_pr": {
                "pull_request": 21,
                "head_sha": "ce356b6f6a8dee5f807679aed0f78aa057152d1b",
                "workflow_run_id": 28748324684,
                "workflow": "Skeleton Health",
                "result": "success",
            },
            "foundation_main_head_ci": {
                "observed_head_sha": "4233d2ff22310f86305b2e67055c8e4eeb03d6df",
                "status": "insufficient_evidence",
                "reason": "No exact-head workflow run was visible for the automatic historical-ledger commit during this repair audit.",
            },
        },
    }
    write("src/ev4_transition/data/capability-status.v1.json", json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_docs() -> None:
    write(
        "docs/IMPLEMENTATION_STATUS.yaml",
        '''schema_version: ev4-project-gate-implementation-status.v1
updated_at: 2026-07-05
status_authority: active_capability_truth
capability_truth_source: src/ev4_transition/data/capability-status.v1.json
historical_merge_ledger: docs/EV4_SHARED_CONTRACTS_STATUS.md

repository:
  name: rezahh107/EV4-Project-Gate
  default_branch: main
  foundation_main_head: 4233d2ff22310f86305b2e67055c8e4eeb03d6df
  foundation_main_head_ci:
    status: insufficient_evidence
    reason: no_visible_exact_head_run_for_automatic_historical_ledger_commit
  last_verified_project_gate_pr:
    number: 21
    head_sha: ce356b6f6a8dee5f807679aed0f78aa057152d1b
    workflow_run_id: 28748324684
    workflow_result: success
  prompt_05_repair_branch: fix/prompt-05-foundation-reconciliation

capabilities:
  architect_to_ce:
    orchestration_baseline: implemented
    cli_exposure: implemented
    verification_state: synthetic_fixture_only
    real_non_synthetic_handoff: insufficient_evidence
  ce_to_builder:
    transition_id: ev4-ce-to-builder-transition@1.0.0
    orchestration_baseline: implemented
    cli_exposure: not_implemented
    owner_fixture_integration: verified
    real_non_synthetic_handoff: insufficient_evidence
    source_repository: rezahh107/EV4-Constructability-Engineer-Repo
    source_commit: cfceec5c20269c75a1cc19b2675d7087cede4599
    consumer_repository: rezahh107/EV4-Builder-Assistant-Repo
    consumer_commit: 69a2c61edf6d06b4418ad770fcefbfdffcf275d6
    result_schema: schemas/ce-to-builder-transition-result/ce-to-builder-transition-result.v1.schema.json
    lock_manifest: contracts/locks/ce-to-builder-transition.v1.lock.json
  builder_to_responsive:
    transition_id: ev4-builder-to-responsive-transition@1.0.0
    orchestration_baseline: implemented
    cli_exposure: not_implemented
    producer_commit: 69a2c61edf6d06b4418ad770fcefbfdffcf275d6
    consumer_commit: df74c7ba2ffbed1a4136b5ea6be6ce30db4e161a
    owner_contract_lock: computed_from_pinned_owner_file_bytes
    official_responsive_validator_integration: implemented
    verification_state: pending_exact_head_ci
    real_non_synthetic_handoff: insufficient_evidence
    result_schema: schemas/builder-to-responsive-transition-result/builder-to-responsive-transition-result.v1.schema.json
    lock_manifest: contracts/locks/builder-to-responsive-transition.v1.lock.json
  final_evidence_gate:
    gate_id: ev4-final-evidence-gate@1.0.0
    orchestration_baseline: implemented
    cli_exposure: not_implemented
    prior_lock_chain: pinned_to_immutable_project_gate_commit
    official_responsive_validator_integration: implemented
    verification_state: pending_exact_head_ci
    real_non_synthetic_evidence: insufficient_evidence
    result_schema: schemas/final-gate-result/final-gate-result.v1.schema.json
    lock_manifest: contracts/locks/final-gate.v1.lock.json
  user_interface:
    status: not_implemented

verification:
  ce_to_builder_owner_fixture_integration:
    state: verified
    evidence_type: pinned_owner_fixture_integration
    workflow_run_id: 28744810186
    workflow_head_sha: 42bfa484481c585f589d86c40424660c70b038a0
    scope_limit: not_real_non_synthetic_handoff
  prompt_05:
    state: pending_exact_head_ci
    evidence_type: pinned_owner_contract_and_official_validator_integration
    scope_limit: not_real_non_synthetic_handoff_or_frontend_correctness

remaining_insufficient_evidence:
  - exact_foundation_main_head_ci_result
  - real_non_synthetic_CE_to_Builder_transition_evidence
  - real_Builder_execution_evidence_bundle
  - real_Responsive_input_and_output_evidence_bundle
  - accessibility_export_and_frontend_correctness_evidence
''',
    )
    write(
        "docs/TRANSITION_BOUNDARY_MAP.md",
        '''# EV4 Transition Boundary Map

Status: PR #21 is merged. Prompt-05 Builder→Responsive and Final Evidence Gate orchestration baselines are implemented on `fix/prompt-05-foundation-reconciliation` with immutable owner pins and fail-closed lock verification. Exact-head CI is pending. Real non-synthetic Builder and Responsive evidence remains unavailable.

## Status vocabulary

Project Gate transition decisions use:

```text
accepted
repair_needed
insufficient_evidence
invalid
```

`accepted` is allowed only when every transition-specific `accepted_requires` item is true and no blocking diagnostic exists.

## Architect → CE

```yaml
transition_id: ev4-architect-to-ce-transition@1.0.0
orchestration_baseline: implemented
cli_exposure: implemented
verification_state: synthetic_fixture_only
```

Allowed Project Gate behavior:

```text
Architect Stage Evidence Bundle
→ Project Gate envelope validation
→ pinned Architect/CE contract hash checks
→ official Architect validator
→ deterministic Project Gate projection using CE-owned mapping contract
→ official CE validator
→ Architect→CE transition result validation
```

Forbidden Project Gate behavior includes creating CE constructability decisions, proving Elementor buildability, authorizing Builder runtime, or claiming production readiness.

## CE → Builder

```yaml
transition_id: ev4-ce-to-builder-transition@1.0.0
orchestration_baseline: implemented
cli_exposure: not_implemented
owner_fixture_integration: verified
real_non_synthetic_handoff: insufficient_evidence
source_repository: rezahh107/EV4-Constructability-Engineer-Repo
source_commit: cfceec5c20269c75a1cc19b2675d7087cede4599
consumer_repository: rezahh107/EV4-Builder-Assistant-Repo
consumer_commit: 69a2c61edf6d06b4418ad770fcefbfdffcf275d6
project_gate_lock: contracts/locks/ce-to-builder-transition.v1.lock.json
project_gate_result_schema: schemas/ce-to-builder-transition-result/ce-to-builder-transition-result.v1.schema.json
```

## Builder → Responsive

```yaml
transition_id: ev4-builder-to-responsive-transition@1.0.0
orchestration_baseline: implemented
cli_exposure: not_implemented
producer_repository: rezahh107/EV4-Builder-Assistant-Repo
producer_commit: 69a2c61edf6d06b4418ad770fcefbfdffcf275d6
consumer_repository: rezahh107/EV4-Responsive-Architect
consumer_commit: df74c7ba2ffbed1a4136b5ea6be6ce30db4e161a
owner_contract_lock: contracts/locks/builder-to-responsive-transition.v1.lock.json
official_input_validator: validation/e2e/run_builder_responsive_input_boundary_check.py
verification_state: pending_exact_head_ci
real_non_synthetic_handoff: insufficient_evidence
```

Project Gate packages pinned Builder evidence references as transport metadata and validates Responsive-owned intake contracts. It does not create a Builder-owned formal export schema and must not claim Responsive correctness, frontend correctness, accessibility completion, export validation completion, or production readiness.

## Final Evidence Gate

```yaml
gate_id: ev4-final-evidence-gate@1.0.0
orchestration_baseline: implemented
cli_exposure: not_implemented
prior_lock_chain: pinned_to_immutable_project_gate_commit
official_output_validator: validation/e2e/run_responsive_tree_architecture_refactor_check.py
verification_state: pending_exact_head_ci
real_non_synthetic_evidence: insufficient_evidence
```

The final gate verifies the immutable prior lock chain, Responsive-owned output schema and validator execution, and explicit real-evidence presence. Synthetic fixtures and CI success cannot be promoted into frontend or production correctness.

## Evidence interpretation

A green Project Gate CI run proves only that the checked implementation, fixtures, immutable locks, and owner-tool integrations passed for the exact tested head. It does not prove real Elementor execution, Responsive correctness, accessibility, export validity, release readiness, or production readiness.

## Foundation CI note

The current foundation `main` head observed before this repair was `4233d2ff22310f86305b2e67055c8e4eeb03d6df`. No exact-head workflow run was visible for that automatic historical-ledger commit, so that specific head remains `insufficient_evidence`. PR #21 head `ce356b6f6a8dee5f807679aed0f78aa057152d1b` passed Skeleton Health run `28748324684`.
''',
    )


def write_prompt_workflow() -> None:
    write(
        ".github/workflows/prompt-05.yml",
        '''name: Prompt 05 Builder Responsive Final Gate

on:
  pull_request:
  push:
    branches:
      - project-gate-prompt-05-builder-responsive-final-gate
      - fix/prompt-05-foundation-reconciliation

permissions:
  contents: read

jobs:
  prompt-05:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout Project Gate
        uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          path: EV4-Project-Gate
          persist-credentials: false

      - name: Checkout pinned Builder owner repository
        uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          repository: rezahh107/EV4-Builder-Assistant-Repo
          ref: 69a2c61edf6d06b4418ad770fcefbfdffcf275d6
          path: EV4-Builder-Assistant-Repo
          persist-credentials: false

      - name: Checkout pinned Responsive owner repository
        uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5
        with:
          repository: rezahh107/EV4-Responsive-Architect
          ref: df74c7ba2ffbed1a4136b5ea6be6ce30db4e161a
          path: EV4-Responsive-Architect
          persist-credentials: false

      - name: Setup Python
        uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
        with:
          python-version: '3.11'

      - name: Install package
        working-directory: EV4-Project-Gate
        run: python -m pip install -e '.[dev]'

      - name: Verify action pins
        working-directory: EV4-Project-Gate
        run: python scripts/check-github-action-pinning.py

      - name: Prompt-05 syntax and JSON checks
        working-directory: EV4-Project-Gate
        run: |
          python -m py_compile \
            src/ev4_transition/progress.py \
            src/ev4_transition/runners/responsive_tools.py \
            src/ev4_transition/transitions/builder_to_responsive.py \
            src/ev4_transition/transitions/final_gate.py \
            scripts/compute-builder-to-responsive-lock.py \
            scripts/compute-final-gate-lock.py
          python -m json.tool schemas/builder-to-responsive-transition-result/builder-to-responsive-transition-result.v1.schema.json >/dev/null
          python -m json.tool schemas/final-gate-result/final-gate-result.v1.schema.json >/dev/null
          python -m json.tool contracts/locks/builder-to-responsive-transition.v1.lock.json >/dev/null
          python -m json.tool contracts/locks/final-gate.v1.lock.json >/dev/null

      - name: Prompt-05 transition and capability tests
        working-directory: EV4-Project-Gate
        run: pytest -q tests/transitions/test_builder_to_responsive.py tests/transitions/test_final_gate.py tests/test_cli.py

      - name: Recompute and compare immutable locks
        working-directory: EV4-Project-Gate
        run: |
          python scripts/compute-builder-to-responsive-lock.py \
            --builder-repo ../EV4-Builder-Assistant-Repo \
            --responsive-repo ../EV4-Responsive-Architect \
            --output /tmp/b2r-lock.json
          cmp /tmp/b2r-lock.json contracts/locks/builder-to-responsive-transition.v1.lock.json
          python scripts/compute-final-gate-lock.py \
            --project-gate-repo . \
            --responsive-repo ../EV4-Responsive-Architect \
            --output /tmp/final-lock.json
          cmp /tmp/final-lock.json contracts/locks/final-gate.v1.lock.json

      - name: Run pinned official Responsive validators
        run: |
          python EV4-Responsive-Architect/validation/e2e/run_builder_responsive_input_boundary_check.py
          python EV4-Responsive-Architect/validation/e2e/run_responsive_tree_architecture_refactor_check.py

      - name: Upload recomputed lock evidence
        if: always()
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: prompt-05-recomputed-locks
          path: |
            /tmp/b2r-lock.json
            /tmp/final-lock.json
          if-no-files-found: ignore
          retention-days: 14

      - name: Record exact head
        run: echo "Prompt-05 validated source head ${{ github.event.pull_request.head.sha || github.sha }}" >> "$GITHUB_STEP_SUMMARY"
''',
    )


def patch_primary_workflow() -> None:
    path = ".github/workflows/validate.yml"
    text = read(path)
    branch_line = "      - project-gate-prompt-04-ce-to-builder\n"
    if "      - fix/prompt-05-foundation-reconciliation\n" not in text:
        if branch_line not in text:
            raise SystemExit("validate.yml branch insertion anchor missing")
        text = text.replace(branch_line, branch_line + "      - fix/prompt-05-foundation-reconciliation\n", 1)
    old_allow = "schemas/ce-to-builder-transition-result/ce-to-builder-transition-result.v1.schema.json|schemas/diagnostic/diagnostic.v1.schema.json"
    new_allow = "schemas/ce-to-builder-transition-result/ce-to-builder-transition-result.v1.schema.json|schemas/builder-to-responsive-transition-result/builder-to-responsive-transition-result.v1.schema.json|schemas/final-gate-result/final-gate-result.v1.schema.json|schemas/diagnostic/diagnostic.v1.schema.json"
    if new_allow not in text:
        if old_allow not in text:
            raise SystemExit("validate.yml schema allowlist anchor missing")
        text = text.replace(old_allow, new_allow, 1)
    anchor = '''      - name: Upload CE-to-Builder pytest log
        if: failure()
'''
    prompt_step = '''      - name: Prompt-05 transition tests
        working-directory: EV4-Project-Gate
        run: pytest -q tests/transitions/test_builder_to_responsive.py tests/transitions/test_final_gate.py

'''
    if "      - name: Prompt-05 transition tests\n" not in text:
        if anchor not in text:
            raise SystemExit("validate.yml Prompt-05 test insertion anchor missing")
        text = text.replace(anchor, prompt_step + anchor, 1)
    write(path, text)


def apply() -> None:
    apply_source_fixes()
    write_lock_tools()
    patch_tests()
    write_capability_truth()
    write_docs()
    write_prompt_workflow()
    patch_primary_workflow()


def finalize(commit_sha: str) -> None:
    if len(commit_sha) != 40 or any(ch not in "0123456789abcdef" for ch in commit_sha):
        raise SystemExit("finalize commit must be a full lowercase SHA-1")
    replace_once(
        "src/ev4_transition/transitions/final_gate.py",
        f'PG_COMMIT = "{FINAL_GATE_COMMIT_MARKER}"',
        f'PG_COMMIT = "{commit_sha}"',
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--finalize-commit")
    args = parser.parse_args()
    if args.apply:
        apply()
    else:
        finalize(args.finalize_commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
