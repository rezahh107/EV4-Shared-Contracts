import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATE_WORKFLOW = ROOT / ".github/workflows/validate.yml"
REUSABLE_WORKFLOW = ROOT / ".github/workflows/verify-vendored-common-contract.yml"


def _workflow(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


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
        assert json.loads((ROOT / relative).read_text(encoding="utf-8")).get("synthetic") is True


def test_personal_use_docs_explain_statuses_and_outputs():
    guide = (ROOT / "docs/PERSONAL_USE_GUIDE.md").read_text(encoding="utf-8")
    for token in [
        "accepted",
        "invalid",
        "insufficient_evidence",
        "repair_needed",
        "outputs/runs/<timestamp-or-run-id>/",
    ]:
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

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Setup" in readme
    assert "uv sync --locked --extra dev --extra ui" in readme
    assert "Fallback when `uv` is unavailable" in readme


def test_windows_uv_setup_script_is_safe_and_copy_ready():
    script = (ROOT / "scripts/setup-windows-uv.ps1").read_text(encoding="utf-8")
    for token in [
        "Get-Command uv",
        "winget install --id=astral-sh.uv -e",
        "uv python install 3.11",
        "uv sync --locked --extra dev --extra ui",
        "uv run --locked ev4-transition inspect",
        "will not install remote tools automatically",
    ]:
        assert token in script


def test_unified_workflow_uses_locked_uv_and_one_core_suite():
    text = VALIDATE_WORKFLOW.read_text(encoding="utf-8")
    assert "astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b" in text
    assert "uv lock --check" in text
    assert "uv sync --locked --extra dev --extra ui" in text
    assert text.count("uv run pytest -vv") == 1
    assert text.count("Build wheel once") == 1
    assert text.count("Clean-install package and construct UI once") == 1
    assert "python -m pip install" not in text


def test_unified_workflow_keeps_owner_validators_and_real_node_boundary():
    text = VALIDATE_WORKFLOW.read_text(encoding="utf-8")
    for token in [
        "scripts/check-architect-stage-payload.py",
        "scripts/validate-ce-architect-stage-intake.py",
        "scripts/ce-to-builder-smoke.py",
        "validation/e2e/run_builder_responsive_input_boundary_check.py",
        "validation/e2e/run_responsive_tree_architecture_refactor_check.py",
        "scripts/kernel-decision-intake-bridge.mjs",
        "npm run validate:mvk",
        "Setup Node for Kernel boundary only",
    ]:
        assert token in text
    assert not (ROOT / "package.json").exists()
    assert not (ROOT / "scripts/validate.js").exists()
    assert not (ROOT / "scripts/status.js").exists()


def test_unified_workflow_topology_and_permissions_are_lean():
    workflow = _workflow(VALIDATE_WORKFLOW)
    jobs = workflow["jobs"]
    assert set(jobs) == {"skeleton", "python-core", "affected-boundaries", "quality-gate"}
    assert workflow["permissions"] == {"contents": "read"}
    text = VALIDATE_WORKFLOW.read_text(encoding="utf-8")
    assert "actions/upload-artifact" not in text
    assert "contents: write" not in text
    assert "status-after-merge" not in text


def test_reusable_external_contract_workflow_remains_public():
    assert REUSABLE_WORKFLOW.is_file()
    text = REUSABLE_WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_call:" in text
    assert "verify-vendored-common-contract.py" in text
