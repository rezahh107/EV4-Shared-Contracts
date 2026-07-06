import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_personal_use_package_files_exist():
    for relative in [
        "docs/LOCAL_SETUP_GUIDE.md",
        "docs/PERSONAL_USE_GUIDE.md",
        "docs/E2E_DEMO_WORKFLOW.md",
        "scripts/run-project-gate-ui.py",
        "scripts/run-project-gate-demo.py",
        "outputs/README.md",
        "outputs/.gitkeep",
    ]:
        assert (ROOT / relative).exists(), relative


def test_personal_use_samples_are_synthetic_json():
    for relative in [
        "fixtures/personal-use/sample-valid-stage-bundle.synthetic.json",
        "fixtures/personal-use/sample-insufficient-evidence-stage-bundle.synthetic.json",
        "examples/personal-use/sample-valid-stage-bundle.synthetic.json",
        "examples/personal-use/sample-insufficient-evidence-stage-bundle.synthetic.json",
    ]:
        data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        assert data.get("synthetic") is True


def test_personal_use_docs_explain_statuses_and_outputs():
    guide = (ROOT / "docs/PERSONAL_USE_GUIDE.md").read_text(encoding="utf-8")
    for token in ["accepted", "invalid", "insufficient_evidence", "repair_needed", "outputs/runs/<timestamp-or-run-id>/"]:
        assert token in guide


def test_demo_runner_keeps_safety_markers():
    text = (ROOT / "scripts/run-project-gate-demo.py").read_text(encoding="utf-8")
    for token in [
        "_safe_fixture_metadata",
        "_create_unique_run_dir",
        "metadata_error",
        "FileExistsError",
        '"final_gate_status": "insufficient_evidence"',
        '"real_evidence_claimed": False',
    ]:
        assert token in text


def test_uv_default_setup_artifacts_and_docs_are_present():
    assert (ROOT / "uv.lock").exists()
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.11"
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in pyproject
    assert "[project.optional-dependencies]" in pyproject
    assert "[dependency-groups]" not in pyproject

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Default setup with uv" in readme
    assert "uv sync --extra dev --extra ui" in readme
    assert "not uv dependency groups" in readme
    assert "### Fallback if uv is unavailable" in readme
    assert readme.index("## Default setup with uv") < readme.index("### Fallback if uv is unavailable")


def test_windows_uv_setup_script_is_safe_and_copy_ready():
    script = (ROOT / "scripts/setup-windows-uv.ps1").read_text(encoding="utf-8")
    assert "Get-Command uv" in script
    assert "winget install --id=astral-sh.uv -e" in script
    assert "uv python install 3.11" in script
    assert "uv sync --locked --extra dev --extra ui" in script
    assert "uv run --locked ev4-transition inspect" in script
    assert "irm https://astral.sh/uv/install.ps1 | iex" in script
    assert "will not install remote tools automatically" in script


def test_ci_uses_uv_lock_sync_and_run_for_python_workflows():
    for relative in [
        ".github/workflows/validate.yml",
        ".github/workflows/prompt-05.yml",
        ".github/workflows/prompt-06.yml",
        ".github/workflows/ui-runtime-smoke.yml",
    ]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b" in text
        assert "uv lock --check" in text
        assert "uv sync --locked --extra dev --extra ui" in text
        assert "python -m pip install" not in text
    validate = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "uv run pytest" in validate
    assert "uv run ev4-transition" in validate
