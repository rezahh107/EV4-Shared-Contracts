from pathlib import Path

import pytest

from ev4_transition.bundle_validator import BundleValidator, ResultValidationError
from ev4_transition.canonical_json import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]


def validator() -> BundleValidator:
    return BundleValidator(ROOT / "schemas")


def test_valid_stage_evidence_bundle():
    result = validator().validate_file(ROOT / "fixtures/valid/architect-stage-bundle.v1.json")
    assert result["status"] == "valid"
    assert result["diagnostics"] == []
    assert result["hashes"]["source_bundle_hash"]["value"]
    assert result["hashes"]["canonical_payload_hash"]["value"]


def test_malformed_object_is_invalid_without_repair():
    result = validator().validate_file(ROOT / "fixtures/invalid/malformed-missing-payload-schema.v1.json")
    assert result["status"] == "invalid"
    assert any(item["code"] == "SCHEMA_VALIDATION_FAILED" for item in result["diagnostics"])
    assert result["output"] is None


def test_no_silent_repair_missing_payload_schema_id():
    result = validator().validate_file(ROOT / "fixtures/invalid/no-silent-repair-missing-schema-id.v1.json")
    assert result["status"] == "invalid"
    assert result["output"] is None


def test_no_invented_evidence_missing_source_is_invalid():
    result = validator().validate_file(ROOT / "fixtures/invalid/no-invented-evidence-missing-source.v1.json")
    assert result["status"] == "invalid"
    assert result["output"] is None


def test_array_input_is_invalid_not_crash():
    result = validator().validate_file(ROOT / "fixtures/invalid/array-input.v1.json")
    assert result["status"] == "invalid"
    assert result["source_stage"] is None
    assert result["diagnostics"][0]["code"] == "INPUT_NOT_OBJECT"


def test_primitive_input_is_invalid_not_crash():
    result = validator().validate_file(ROOT / "fixtures/invalid/primitive-input.v1.json")
    assert result["status"] == "invalid"
    assert result["source_stage"] is None
    assert result["diagnostics"][0]["code"] == "INPUT_NOT_OBJECT"


def test_missing_required_evidence_is_insufficient_evidence():
    result = validator().validate_file(
        ROOT / "fixtures/invalid/missing-required-evidence.v1.json",
        required_evidence_ids=["architecture_handoff"],
    )
    assert result["status"] == "insufficient_evidence"
    assert result["diagnostics"][0]["code"] == "REQUIRED_EVIDENCE_MISSING"
    assert result["output"] is None


def test_declared_insufficient_evidence_is_structured():
    result = validator().validate_file(ROOT / "fixtures/insufficient-evidence/architect-stage-bundle.v1.json")
    assert result["status"] == "insufficient_evidence"
    assert result["diagnostics"][0]["severity"] == "insufficient_evidence"
    assert result["diagnostics"][0]["code"] == "BUNDLE_INSUFFICIENT_EVIDENCE"


def test_diagnostic_ordering_is_deterministic():
    first = validator().validate_file(ROOT / "fixtures/invalid/no-invented-evidence-missing-source.v1.json")
    second = validator().validate_file(ROOT / "fixtures/invalid/no-invented-evidence-missing-source.v1.json")
    assert first["diagnostics"] == second["diagnostics"]
    sort_projection = [(item["path"], item["severity"], item["code"], item["message"]) for item in first["diagnostics"]]
    assert sort_projection == sorted(sort_projection)


def test_provenance_preservation():
    result = validator().validate_file(ROOT / "fixtures/valid/architect-stage-bundle.v1.json")
    assert result["provenance"]["source_provenance"]["source"] == "synthetic-fixture"
    assert result["provenance"]["produced_by"]["repository"] == "rezahh107/EV4-Architect-Repo"


def test_source_bundle_hash_matches_canonical_source():
    import json

    bundle = json.loads((ROOT / "fixtures/valid/architect-stage-bundle.v1.json").read_text(encoding="utf-8"))
    result = validator().validate_bundle(bundle)
    assert result["hashes"]["source_bundle_hash"]["value"] == canonical_sha256(bundle)


def test_transition_result_schema_enforcement_rejects_bad_result():
    with pytest.raises(ResultValidationError):
        validator().validate_result({"schema_version": "transition-result.v1", "status": "valid"})
