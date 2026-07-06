from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_unique_run_directory_helper_avoids_output_collisions():
    text = read("scripts/run-project-gate-demo.py")
    assert "def _create_unique_run_dir" in text
    assert "FileExistsError" in text
    assert "-{index:03d}" in text
    assert "exist_ok=False" in text


def test_controlled_demo_contract_never_claims_real_readiness():
    text = read("scripts/run-project-gate-demo.py")
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


def test_fixture_metadata_errors_do_not_replace_validation_diagnostics():
    text = read("scripts/run-project-gate-demo.py")
    assert "def _safe_fixture_metadata" in text
    assert "metadata_error" in text
    assert "result = validator.validate_file(path)" in text
    assert '"validation_status": result.get("status")' in text
    assert '"diagnostics": result.get("diagnostics", [])' in text


def test_rendered_demo_report_keeps_safe_claims_visible():
    text = read("scripts/run-project-gate-demo.py")
    for phrase in [
        "production readiness",
        "real end-to-end readiness",
        "export validation",
        "accessibility completion",
        "insufficient_evidence",
    ]:
        assert phrase in text


def test_demo_workflow_doc_remains_controlled_not_real_e2e():
    text = read("docs/E2E_DEMO_WORKFLOW.md")
    assert "demo کنترل‌شده" in text
    assert "insufficient_evidence" in text
    assert "real Elementor validation" in text
    assert "real end-to-end readiness" in text
    assert "demo-fixed-001" in text
