import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_script_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_personal_use_guides_exist():
    assert (ROOT / "docs/LOCAL_SETUP_GUIDE.md").is_file()
    assert (ROOT / "docs/PERSONAL_USE_GUIDE.md").is_file()
    assert (ROOT / "docs/E2E_DEMO_WORKFLOW.md").is_file()


def test_status_explanations_include_all_project_gate_statuses():
    text = (ROOT / "docs/PERSONAL_USE_GUIDE.md").read_text(encoding="utf-8")
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


def test_launcher_detects_missing_ui_gracefully():
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run-project-gate-ui.py"),
            "--module",
            "ev4_transition.ui.__missing_for_personal_use_test__",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    combined = completed.stdout + completed.stderr
    assert "UI is not installed yet. Merge Prompt 1 UI branch first." in combined
    assert "اقدام بعدی" in combined
    assert "Traceback" not in combined


def test_module_discovery_exceptions_are_user_facing():
    demo = load_script_module("demo_launcher_for_discovery_test", "scripts/run-project-gate-demo.py")
    ui = load_script_module("ui_launcher_for_discovery_test", "scripts/run-project-gate-ui.py")

    state = demo._module_state(None, "Prompt 1")  # type: ignore[arg-type]
    assert state["status"] == "missing"
    assert state.get("detail")

    module_name, errors = ui._find_first_module([None])  # type: ignore[list-item]
    assert module_name is None
    assert errors


def test_demo_fixture_metadata_missing_and_malformed_are_safe(tmp_path):
    demo = load_script_module("demo_launcher_for_fixture_test", "scripts/run-project-gate-demo.py")

    class DummyValidator:
        def validate_file(self, path: Path):
            code = "FILE_READ_ERROR" if not path.exists() else "MALFORMED_JSON"
            return {"status": "invalid", "diagnostics": [{"code": code, "severity": "error"}]}

    missing = tmp_path / "missing.json"
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{not json", encoding="utf-8")

    missing_result = demo._validate_fixture(missing, DummyValidator())
    malformed_result = demo._validate_fixture(malformed, DummyValidator())

    for result in [missing_result, malformed_result]:
        assert result["synthetic"] is False
        assert result["declared_evidence_status"] is None
        assert result["validation_status"] == "invalid"
        assert "metadata_error" in result


def test_output_folder_convention_is_documented():
    text = (ROOT / "outputs/README.md").read_text(encoding="utf-8")
    assert "outputs/runs/<timestamp-or-run-id>/" in text
    assert "demo" in text.lower()
    for filename in ["result.json", "report.md", "report.html", "input.snapshot.json", "diagnostics.json"]:
        assert filename in text


def test_guides_clarify_ui_downloads_are_not_demo_run_folders():
    for relative in ["docs/PERSONAL_USE_GUIDE.md", "docs/LOCAL_SETUP_GUIDE.md", "docs/E2E_DEMO_WORKFLOW.md"]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "UI" in text
        assert "outputs/runs/<timestamp-or-run-id>/" in text
        assert "download" in text.lower() or "دانلود" in text


def test_generated_outputs_are_ignored_but_placeholders_tracked():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "outputs/runs/" in text
    assert "!outputs/.gitkeep" in text
    assert "!outputs/README.md" in text


def test_demo_runner_source_does_not_claim_real_evidence():
    text = (ROOT / "scripts/run-project-gate-demo.py").read_text(encoding="utf-8")
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
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.count("## Current Status") == 1
    personal_section = readme.split("## Personal local use", 1)[1].split("\n## ", 1)[0]
    assert "capabilities:" not in personal_section
    assert "user_interface:" not in personal_section
    assert "capability-status.v1.json" not in personal_section
