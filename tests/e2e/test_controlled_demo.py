import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_demo_module():
    spec = importlib.util.spec_from_file_location("controlled_demo_for_e2e_test", ROOT / "scripts/run-project-gate-demo.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_unique_run_directory_avoids_output_collisions(tmp_path):
    demo = load_demo_module()

    first = demo._create_unique_run_dir(tmp_path, "demo-fixed")
    second = demo._create_unique_run_dir(tmp_path, "demo-fixed")

    assert first == tmp_path / "demo-fixed"
    assert second == tmp_path / "demo-fixed-001"
    assert first.is_dir()
    assert second.is_dir()


def test_controlled_demo_contract_never_claims_real_readiness():
    text = (ROOT / "scripts/run-project-gate-demo.py").read_text(encoding="utf-8")
    for required in [
        '"final_gate_status": "insufficient_evidence"',
        '"real_evidence_claimed": False',
        '"production_readiness_claimed": False',
        '"real_elementor_validation_claimed": False',
        '"export_validation_claimed": False',
        '"accessibility_completion_claimed": False',
        '"frontend_correctness_claimed": False',
        '"responsive_correctness_claimed": False',
        '"real_end_to_end_readiness_claimed": False',
    ]:
        assert required in text


def test_fixture_metadata_errors_are_safe_and_validation_diagnostics_remain_authoritative(tmp_path):
    demo = load_demo_module()

    class DummyValidator:
        def validate_file(self, path: Path):
            code = "FILE_READ_ERROR" if not path.exists() else "MALFORMED_JSON"
            return {"status": "invalid", "diagnostics": [{"code": code, "severity": "error"}]}

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{not json", encoding="utf-8")
    missing = tmp_path / "missing.json"

    malformed_result = demo._validate_fixture(malformed, DummyValidator())
    missing_result = demo._validate_fixture(missing, DummyValidator())

    assert malformed_result["synthetic"] is False
    assert missing_result["synthetic"] is False
    assert malformed_result["validation_status"] == "invalid"
    assert missing_result["validation_status"] == "invalid"
    assert malformed_result["diagnostics"][0]["code"] == "MALFORMED_JSON"
    assert missing_result["diagnostics"][0]["code"] == "FILE_READ_ERROR"
    assert "metadata_error" in malformed_result
    assert "metadata_error" in missing_result


def test_rendered_demo_report_keeps_safe_claims_visible():
    demo = load_demo_module()
    report = demo._render_markdown(
        {
            "overall_status": "partial_setup",
            "final_gate_status": "insufficient_evidence",
            "ui": {"status": "missing", "owner": "Prompt 1"},
            "service": {"status": "missing", "owner": "Prompt 2"},
            "samples": [
                {
                    "path": "fixtures/personal-use/sample-valid-stage-bundle.synthetic.json",
                    "validation_status": "valid",
                    "synthetic": True,
                    "declared_evidence_status": "complete",
                }
            ],
        }
    )

    assert "insufficient_evidence" in report
    assert "production readiness" in report
    assert "real end-to-end readiness" in report
    assert "export validation" in report
    assert "accessibility completion" in report
