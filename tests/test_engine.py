from pathlib import Path

from ev4_transition.bundle_validator import BundleValidator
from ev4_transition.canonical_json import canonical_hash
from ev4_transition.transition_engine import TransitionEngine

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_hash_is_stable():
    assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})


def test_valid_bundle_validation():
    result = BundleValidator(ROOT / "schemas").validate_file(ROOT / "fixtures/valid/architect-stage-bundle.v1.json")
    assert result["status"] == "valid"


def test_invalid_bundle_validation():
    result = BundleValidator(ROOT / "schemas").validate_file(ROOT / "fixtures/invalid/missing-required-field.v1.json")
    assert result["status"] == "invalid"


def test_insufficient_evidence_validation():
    result = BundleValidator(ROOT / "schemas").validate_file(ROOT / "fixtures/invalid/insufficient-evidence.v1.json")
    assert result["status"] == "insufficient_evidence"


def test_transition_success_is_deterministic():
    engine = TransitionEngine(ROOT / "schemas", ROOT / "transitions")
    first = engine.transition_file(ROOT / "fixtures/valid/architect-stage-bundle.v1.json", "architect-to-ce.v1")
    second = engine.transition_file(ROOT / "fixtures/valid/architect-stage-bundle.v1.json", "architect-to-ce.v1")
    assert first == second
    assert first["status"] == "accepted"
    assert first["output"]["target_stage"] == "ce"
    assert first["output_hash"] == canonical_hash(first["output"])


def test_transition_fails_closed_for_wrong_stage():
    engine = TransitionEngine(ROOT / "schemas", ROOT / "transitions")
    result = engine.transition_file(ROOT / "fixtures/valid/architect-stage-bundle.v1.json", "ce-to-builder.v1")
    assert result["status"] == "failed"
    assert result["output"] is None


def test_transition_insufficient_evidence_result():
    engine = TransitionEngine(ROOT / "schemas", ROOT / "transitions")
    result = engine.transition_file(ROOT / "fixtures/invalid/insufficient-evidence.v1.json", "architect-to-ce.v1")
    assert result["status"] == "insufficient_evidence"
    assert result["output"] is None
