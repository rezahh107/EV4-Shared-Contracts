from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ev4_transition.canonical_json import bytes_sha256
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.transitions.builder_to_responsive import (
    BUILDER_REPO,
    EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES,
    RESPONSIVE_INPUT_SCHEMA,
    RESPONSIVE_REPO,
    TRANSITION_ID,
    BuilderToResponsiveTransitionConfig,
    transition_builder_to_responsive,
    verify_builder_to_responsive_lock,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["schema", "builder_evidence", "viewport_evidence"],
        "properties": {"schema": {"const": RESPONSIVE_INPUT_SCHEMA}},
        "additionalProperties": True,
    }


def _responsive_input() -> dict:
    return {
        "schema": RESPONSIVE_INPUT_SCHEMA,
        "builder_evidence": {
            "action_batch_ref": "action-batch.json",
            "execution_evidence_ref": "execution-evidence.json",
            "layout_check_ref": "layout-check.json",
            "completion_gate_ref": "completion-gate.json",
        },
        "viewport_evidence": {
            "desktop": {"evidence_ref": "desktop.json"},
            "tablet": {"evidence_ref": "tablet.json"},
            "mobile": {"evidence_ref": "mobile.json"},
        },
        "real_evidence": True,
    }


def _repos(tmp_path: Path):
    builder = tmp_path / "builder"
    responsive = tmp_path / "responsive"
    for dep in EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES.values():
        root = builder if dep.repository == BUILDER_REPO else responsive
        if dep.path.endswith(".py"):
            text = "import sys\nprint('boundary ok')\nsys.exit(0)\n"
        elif dep.path.endswith(".json") and "builder-responsive-input" in dep.path:
            text = json.dumps({"id": dep.contract_or_schema_id, "marker": dep.identity_marker, **_schema()})
        elif dep.path.endswith(".json"):
            text = json.dumps({"id": dep.contract_or_schema_id, "marker": dep.identity_marker})
        else:
            text = f"{dep.identity_marker}\n"
        _write(root / dep.path, text)
    source = LocalCheckoutContractSource({BUILDER_REPO: builder, RESPONSIVE_REPO: responsive})
    lock = {"schema_version": "builder-to-responsive-transition-lock.v1", "transition_id": TRANSITION_ID, "files": []}
    for dep in EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES.values():
        root = builder if dep.repository == BUILDER_REPO else responsive
        content = (root / dep.path).read_bytes()
        lock["files"].append({
            "role": dep.role,
            "repository": dep.repository,
            "accepted_commit": dep.accepted_commit,
            "path": dep.path,
            "contract_or_schema_id": dep.contract_or_schema_id,
            "sha256_file_bytes": bytes_sha256(content),
        })
    return builder, responsive, source, lock


def _config(tmp_path: Path, lock: dict, builder: Path | None, responsive: Path | None) -> BuilderToResponsiveTransitionConfig:
    return BuilderToResponsiveTransitionConfig(tmp_path / "schemas", lock, builder, responsive)


def _codes(result: dict) -> list[str]:
    return [item["code"] for item in result["diagnostics"]]


def test_builder_to_responsive_live_boundary_audit_records_responsive_contract_state(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    result = transition_builder_to_responsive(_responsive_input(), source, _config(tmp_path, lock, builder, responsive))
    assert result["transition_id"] == TRANSITION_ID
    assert result["accepted_requires"]["responsive_input_schema_verified"] is True
    assert result["accepted_requires"]["responsive_input_validator_passed"] is True


def test_builder_to_responsive_missing_builder_evidence_is_insufficient_evidence(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    packet = _responsive_input()
    packet["builder_evidence"].pop("layout_check_ref")
    result = transition_builder_to_responsive(packet, source, _config(tmp_path, lock, builder, responsive))
    assert result["status"] == "insufficient_evidence"
    assert "PG.B2R.BUILDER_EVIDENCE_MISSING" in _codes(result)


def test_builder_to_responsive_missing_responsive_schema_is_insufficient_evidence(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    (responsive / "schemas/ev4-builder-responsive-input.schema.json").unlink()
    result = transition_builder_to_responsive(_responsive_input(), source, _config(tmp_path, lock, builder, responsive))
    assert "PG.B2R.RESPONSIVE_SCHEMA_UNAVAILABLE" in _codes(result)


def test_builder_to_responsive_missing_responsive_validator_is_insufficient_evidence(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    (responsive / "validation/e2e/run_builder_responsive_input_boundary_check.py").unlink()
    result = transition_builder_to_responsive(_responsive_input(), source, _config(tmp_path, lock, builder, responsive))
    assert "PG.B2R.RESPONSIVE_VALIDATOR_MISSING" in _codes(result)


def test_builder_to_responsive_forbidden_claim_is_invalid(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    packet = _responsive_input()
    packet["claim"] = "production_ready"
    result = transition_builder_to_responsive(packet, source, _config(tmp_path, lock, builder, responsive))
    assert result["status"] == "invalid"
    assert "PG.B2R.FORBIDDEN_CLAIM" in _codes(result)


def test_builder_to_responsive_missing_viewport_evidence_blocks_accepted(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    packet = _responsive_input()
    packet["viewport_evidence"].pop("mobile")
    result = transition_builder_to_responsive(packet, source, _config(tmp_path, lock, builder, responsive))
    assert result["status"] == "insufficient_evidence"
    assert "PG.B2R.VIEWPORT_EVIDENCE_MISSING" in _codes(result)


def test_builder_to_responsive_raw_screenshot_does_not_prove_correctness(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    packet = _responsive_input()
    packet["raw_screenshot"] = "screenshot.png"
    result = transition_builder_to_responsive(packet, source, _config(tmp_path, lock, builder, responsive))
    assert "PG.B2R.RAW_SCREENSHOT_CORRECTNESS_CLAIM" in _codes(result)


def test_builder_to_responsive_ci_success_does_not_prove_frontend_correctness(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    packet = _responsive_input()
    packet["evidence_claim"] = "ci_success_as_frontend_evidence"
    result = transition_builder_to_responsive(packet, source, _config(tmp_path, lock, builder, responsive))
    assert result["status"] == "invalid"
    assert "PG.B2R.CI_FRONTEND_CORRECTNESS_CLAIM" in _codes(result)


def test_builder_to_responsive_result_schema_validated(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    schema_dir = tmp_path / "schemas" / "builder-to-responsive-transition-result"
    schema_dir.mkdir(parents=True)
    schema_dir.joinpath("builder-to-responsive-transition-result.v1.schema.json").write_text(json.dumps({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["schema_version", "transition_id", "status"],
    }), encoding="utf-8")
    result = transition_builder_to_responsive(_responsive_input(), source, _config(tmp_path, lock, builder, responsive))
    Draft202012Validator(json.loads(schema_dir.joinpath("builder-to-responsive-transition-result.v1.schema.json").read_text())).validate(result)


def test_diagnostics_have_stable_ordering(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    packet = _responsive_input()
    packet["claim"] = "production_ready"
    packet["viewport_evidence"].pop("mobile")
    first = transition_builder_to_responsive(packet, source, _config(tmp_path, lock, builder, responsive))
    second = transition_builder_to_responsive(packet, source, _config(tmp_path, lock, builder, responsive))
    assert first["diagnostics"] == second["diagnostics"]


def test_builder_to_responsive_lock_verification_detects_hash_mismatch(tmp_path: Path):
    builder, responsive, source, lock = _repos(tmp_path)
    lock["files"][0]["sha256_file_bytes"] = "0" * 64
    diagnostics = verify_builder_to_responsive_lock(lock, source)
    assert any(item.code == "PG.B2R.EXTERNAL_HASH_MISMATCH" for item in diagnostics)

def test_builder_to_responsive_lock_rejects_non_string_role_without_crash(tmp_path: Path):
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
