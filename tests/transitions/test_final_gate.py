from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from ev4_transition.canonical_json import bytes_sha256
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.transitions.final_gate import (
    EXPECTED_FINAL_GATE_DEPENDENCIES,
    GATE_ID,
    PG_REPO,
    RESPONSIVE_OUTPUT_SCHEMA,
    RESPONSIVE_REPO,
    FinalGateConfig,
    run_final_gate,
    verify_final_gate_lock,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["schema"],
        "properties": {"schema": {"const": RESPONSIVE_OUTPUT_SCHEMA}},
        "additionalProperties": True,
    }


def _output() -> dict:
    return {
        "schema": RESPONSIVE_OUTPUT_SCHEMA,
        "responsive_tree_output": {"mode": "blocked"},
        "real_evidence": True,
        "evidence_status": "real",
    }


def _repos(tmp_path: Path):
    pg = tmp_path / "pg"
    responsive = tmp_path / "responsive"
    for dep in EXPECTED_FINAL_GATE_DEPENDENCIES.values():
        root = pg if dep.repository == PG_REPO else responsive
        if dep.path.endswith(".py"):
            text = "import sys\nprint('responsive ok')\nsys.exit(0)\n"
        elif dep.path.endswith(".json") and "responsive-output" in dep.path:
            text = json.dumps({"id": dep.contract_or_schema_id, "marker": dep.identity_marker, **_schema()})
        elif dep.path.endswith(".json"):
            text = json.dumps({"id": dep.contract_or_schema_id, "marker": dep.identity_marker})
        else:
            text = f"{dep.identity_marker}\n"
        _write(root / dep.path, text)
    source = LocalCheckoutContractSource({PG_REPO: pg, RESPONSIVE_REPO: responsive})
    lock = {"schema_version": "final-gate-lock.v1", "gate_id": GATE_ID, "files": []}
    for dep in EXPECTED_FINAL_GATE_DEPENDENCIES.values():
        root = pg if dep.repository == PG_REPO else responsive
        content = (root / dep.path).read_bytes()
        lock["files"].append({
            "role": dep.role,
            "repository": dep.repository,
            "accepted_commit": dep.accepted_commit,
            "path": dep.path,
            "contract_or_schema_id": dep.contract_or_schema_id,
            "sha256_file_bytes": bytes_sha256(content),
        })
    return pg, responsive, source, lock


def _config(tmp_path: Path, lock: dict, pg: Path | None, responsive: Path | None) -> FinalGateConfig:
    return FinalGateConfig(tmp_path / "schemas", lock, pg, responsive)


def _codes(result: dict) -> list[str]:
    return [item["code"] for item in result["diagnostics"]]


def test_final_gate_verifies_prior_lock_chain(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    result = run_final_gate(_output(), source, _config(tmp_path, lock, pg, responsive))
    assert result["accepted_requires"]["prior_lock_chain_verified"] is True


def test_final_gate_blocks_production_ready_without_evidence(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    packet = _output()
    packet["claim"] = "production_ready"
    result = run_final_gate(packet, source, _config(tmp_path, lock, pg, responsive))
    assert result["status"] == "invalid"
    assert "PG.FINAL.FORBIDDEN_CLAIM" in _codes(result)


def test_final_gate_blocks_release_ready_without_evidence(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    packet = _output()
    packet["claim"] = "release_ready"
    result = run_final_gate(packet, source, _config(tmp_path, lock, pg, responsive))
    assert result["status"] == "invalid"
    assert "PG.FINAL.FORBIDDEN_CLAIM" in _codes(result)


def test_final_gate_does_not_count_synthetic_as_real_evidence(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    packet = _output()
    packet["evidence_status"] = "synthetic_fixture"
    packet["synthetic_only"] = True
    result = run_final_gate(packet, source, _config(tmp_path, lock, pg, responsive))
    assert result["status"] == "insufficient_evidence"
    assert "PG.FINAL.SYNTHETIC_ONLY_EVIDENCE" in _codes(result)


def test_final_gate_result_schema_validated(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    schema_dir = tmp_path / "schemas" / "final-gate-result"
    schema_dir.mkdir(parents=True)
    schema_dir.joinpath("final-gate-result.v1.schema.json").write_text(json.dumps({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": ["schema_version", "gate_id", "status"],
    }), encoding="utf-8")
    result = run_final_gate(_output(), source, _config(tmp_path, lock, pg, responsive))
    Draft202012Validator(json.loads(schema_dir.joinpath("final-gate-result.v1.schema.json").read_text())).validate(result)


def test_final_gate_lock_verification_detects_hash_mismatch(tmp_path: Path):
    pg, responsive, source, lock = _repos(tmp_path)
    lock["files"][0]["sha256_file_bytes"] = "0" * 64
    diagnostics = verify_final_gate_lock(lock, source)
    assert any(item.code == "PG.FINAL.EXTERNAL_HASH_MISMATCH" for item in diagnostics)

def test_final_gate_lock_rejects_non_string_role_without_crash(tmp_path: Path):
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
