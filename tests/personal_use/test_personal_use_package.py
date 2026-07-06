import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_personal_use_guides_exist():
    assert (ROOT / "docs/LOCAL_SETUP_GUIDE.md").is_file()
    assert (ROOT / "docs/PERSONAL_USE_GUIDE.md").is_file()
    assert (ROOT / "docs/E2E_DEMO_WORKFLOW.md").is_file()


def test_status_explanations_include_all_project_gate_statuses():
    text = read("docs/PERSONAL_USE_GUIDE.md")
    for status in ["accepted", "invalid", "insufficient_evidence", "repair_needed"]:
        assert status in text


def test_synthetic_samples_are_explicitly_marked_synthetic():
    for relative in [
        "fixtures/personal-use/sample-valid-stage-bundle.synthetic.json",
        "fixtures/personal-use/sample-insufficient-evidence-stage-bundle.synthetic.json",
        "examples/personal-use/sample-valid-stage-bundle.synthetic.json",
        "examples/personal-use/sample-insufficient-evidence-stage-bundle.synthetic.json",
    ]:
        path = ROOT / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["synthetic"] is True
        assert "synthetic" in path.read_text(encoding="utf-8").lower()


def test_launcher_reports_missing_ui_with_persian_and_english_next_action():
    text = read("scripts/run-project-gate-ui.py")
    assert "UI is not installed yet. Merge Prompt 1 UI branch first." in text
    assert "اقدام بعدی" in text
    assert "python scripts/run-project-gate-demo.py" in text
    assert "except Exception as exc" in text
    assert "discovery_errors" in text


def test_demo_runner_handles_optional_module_discovery_failures():
    text = read("scripts/run-project-gate-demo.py")
    assert "def _module_state" in text
    assert "except Exception as exc" in text
    assert '"status": "missing"' in text
    assert '"owner": owner' in text


def test_demo_fixture_metadata_missing_and_malformed_are_safe():
    text = read("scripts/run-project-gate-demo.py")
    assert "def _safe_fixture_metadata" in text
    assert "metadata_error" in text
    assert "validator.validate_file(path)" in text
    assert "except Exception as exc" in text


def test_output_folder_convention_is_documented():
    text = read("outputs/README.md")
    assert "outputs/runs/<timestamp-or-run-id>/" in text
    assert "demo" in text.lower()
    for filename in ["result.json", "report.md", "report.html", "input.snapshot.json", "diagnostics.json"]:
        assert filename in text


def test_guides_clarify_ui_downloads_are_not_demo_run_folders():
    for relative in ["docs/PERSONAL_USE_GUIDE.md", "docs/LOCAL_SETUP_GUIDE.md", "docs/E2E_DEMO_WORKFLOW.md"]:
        text = read(relative)
        assert "UI" in text
        assert "outputs/runs/<timestamp-or-run-id>/" in text
        assert "download" in text.lower() or "دانلود" in text


def test_generated_outputs_are_ignored_but_placeholders_tracked():
    text = read(".gitignore")
    assert "outputs/runs/" in text
    assert "!outputs/.gitkeep" in text
    assert "!outputs/README.md" in text


def test_demo_runner_source_does_not_claim_real_evidence():
    text = read("scripts/run-project-gate-demo.py")
    for claim in [
        '"real_evidence_claimed": False',
        '"production_readiness_claimed": False',
        '"real_elementor_validation_claimed": False',
        '"export_validation_claimed": False',
        '"accessibility_completion_claimed": False',
        '"real_end_to_end_readiness_claimed": False',
    ]:
        assert claim in text


def test_readme_personal_section_does_not_own_capability_truth():
    readme = read("README.md")
    assert readme.count("## Current Status") == 1
    personal_section = readme.split("## Personal local use", 1)[1].split("\n## ", 1)[0]
    assert "capabilities:" not in personal_section
    assert "user_interface:" not in personal_section
    assert "capability-status.v1.json" not in personal_section
