from __future__ import annotations

import json
from pathlib import Path

from ev4_transition.canonical_json import bytes_sha256
from ev4_transition.evidence_truth import (
    derive_evidence_classification,
    resolve_evidence,
    synthetic_indicators,
)


def test_top_level_synthetic_derives_synthetic():
    value = {"synthetic": True}
    assert synthetic_indicators(value)
    assert derive_evidence_classification(value, source_resolved=True, hash_verified=True, owner_validation_status="accepted") == "synthetic"


def test_nested_fixture_source_derives_synthetic():
    value = {"evidence": {"source": {"type": "synthetic_fixture"}}}
    assert derive_evidence_classification(value, source_resolved=True, hash_verified=True, owner_validation_status="accepted") == "synthetic"


def test_fixture_path_derives_synthetic():
    assert synthetic_indicators({"source": {"reference": "fixtures/evidence.json"}})


def test_absent_source_bytes_derives_insufficient_evidence(tmp_path: Path):
    result = resolve_evidence(artifact_ref="missing.json", declared_sha256="0" * 64, repository_root=tmp_path)
    assert result.classification == "insufficient_evidence"
    assert any(item["code"] == "PG.EVIDENCE.FILE_MISSING" for item in result.diagnostics)


def test_valid_file_hash_can_derive_real_verified(tmp_path: Path):
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps({"status": "confirmed"}), encoding="utf-8")
    result = resolve_evidence(artifact_ref="evidence.json", declared_sha256=bytes_sha256(path.read_bytes()), repository_root=tmp_path)
    assert result.hash_verified is True
    assert result.classification == "real_verified"


def test_wrong_file_hash_is_rejected(tmp_path: Path):
    path = tmp_path / "evidence.json"
    path.write_text("{}", encoding="utf-8")
    result = resolve_evidence(artifact_ref="evidence.json", declared_sha256="a" * 64, repository_root=tmp_path)
    assert result.classification == "insufficient_evidence"
    assert any(item["code"] == "PG.EVIDENCE.HASH_MISMATCH" for item in result.diagnostics)


def test_desktop_evidence_cannot_satisfy_tablet_claim(tmp_path: Path):
    path = tmp_path / "viewport.json"
    path.write_text(json.dumps({"evidence_ref": "desktop", "viewport": "desktop", "status": "confirmed"}), encoding="utf-8")
    result = resolve_evidence(
        artifact_ref="viewport.json",
        declared_sha256=bytes_sha256(path.read_bytes()),
        repository_root=tmp_path,
        owner_repository="rezahh107/EV4-Builder-Assistant-Repo",
        claim_id="tablet_evidence_verified",
        evidence_type="viewport_evidence",
        subject_ref="desktop",
        expected_subject_ref="desktop",
        viewport="desktop",
    )
    assert result.classification == "insufficient_evidence"
    assert any(item["code"] == "PG.EVIDENCE.CLAIM_VIEWPORT_MISMATCH" for item in result.diagnostics)
