import json
import subprocess
import sys
from pathlib import Path

from ev4_transition.service import GateRequest, run_gate_request

ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_STATIC_KEYS = {
    "current_main",
    "current_main_sha",
    "current_main_head",
    "current_main_head_ci",
    "observed_head_sha",
    "current_pr_state",
    "current_branch_state",
    "current_workflow_run",
    "current_workflow_run_id",
    "head_sha",
    "pr_head_sha",
    "workflow_run_id",
    "workflow_runs",
}


def run_cli(*args):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ev4_transition.cli",
            "--schema-root",
            str(ROOT / "schemas"),
            *args,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_script(script: str, *args: str):
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _all_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _all_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_keys(child)


def _copy_capability_repository(tmp_path: Path) -> Path:
    for relative in (
        "src/ev4_transition/data/capability-status.v1.json",
        "README.md",
        "AGENTS.md",
    ):
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path / "src/ev4_transition/data/capability-status.v1.json"


def test_cli_json_output_valid_bundle():
    completed = run_cli("validate", str(ROOT / "fixtures/valid/architect-stage-bundle.v1.json"))
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["status"] == "valid"


def test_cli_invalid_input_exit_code():
    completed = run_cli("validate", str(ROOT / "fixtures/invalid/array-input.v1.json"))
    assert completed.returncode == 1
    assert json.loads(completed.stdout)["status"] == "invalid"


def test_cli_missing_file_returns_invalid_without_traceback():
    completed = run_cli("validate", str(ROOT / "fixtures/invalid/missing-file.v1.json"))
    assert completed.returncode == 1
    assert completed.stderr == ""
    assert json.loads(completed.stdout)["diagnostics"][0]["code"] == "FILE_READ_ERROR"


def test_cli_persian_insufficient_evidence_output():
    completed = run_cli(
        "validate",
        str(ROOT / "fixtures/insufficient-evidence/architect-stage-bundle.v1.json"),
        "--format",
        "persian",
    )
    assert completed.returncode == 2
    assert "شواهد کافی نیست" in completed.stdout


def test_cli_inspect_persian_reports_guarded_transition_truth():
    completed = run_cli("inspect", "--format", "persian")
    assert completed.returncode == 0
    for expected in (
        "Architect → CE",
        "CE → Builder",
        "Builder → Responsive",
        "Final Evidence Gate",
        "guarded/fail-closed",
        "insufficient_evidence",
    ):
        assert expected in completed.stdout


def test_cli_inspect_reports_layered_ce_to_builder_truth():
    completed = run_cli("inspect")
    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert "stage_bundle_validation" in payload["implemented"]
    assert "architect-to-ce transition" in payload["implemented"]
    assert payload["capabilities"]["ce_to_builder"] == {
        "orchestration_baseline": "implemented",
        "cli_exposure": "guarded",
        "owner_fixture_integration": "verified",
        "real_non_synthetic_handoff": "insufficient_evidence",
    }
    assert "ce-to-builder" in payload["public_cli_transitions"]


def test_cli_inspect_returns_static_capability_truth_only():
    payload = json.loads(run_cli("inspect").stdout)
    assert payload["capabilities"]["ce_to_builder"]["real_non_synthetic_handoff"] == "insufficient_evidence"
    assert "evidence" not in payload
    assert "kroad_011" not in payload
    assert "pg_int" not in payload
    assert PROHIBITED_STATIC_KEYS.isdisjoint(set(_all_keys(payload)))


def test_service_capability_inspection_returns_static_truth_only():
    response = run_gate_request(GateRequest(transition_choice="inspect_capabilities"))
    assert response.status == "accepted"
    assert response.engine_result is not None
    payload = response.engine_result["capabilities"]
    assert payload["schema_version"] == "ev4-project-gate-capability-status.v1"
    assert PROHIBITED_STATIC_KEYS.isdisjoint(set(_all_keys(payload)))


def test_capability_truth_gate_passes_single_authority_repository():
    completed = run_script("scripts/check-capability-truth.py", str(ROOT))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "capability-status.v1.json" in completed.stdout


def test_capability_truth_gate_detects_missing_required_capability(tmp_path):
    authority_path = _copy_capability_repository(tmp_path)
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    del authority["capabilities"]["ce_to_builder"]
    authority_path.write_text(json.dumps(authority), encoding="utf-8")
    completed = run_script("scripts/check-capability-truth.py", str(tmp_path))
    assert completed.returncode == 1
    assert "ce_to_builder" in completed.stdout


def test_capability_truth_gate_rejects_current_main_sha(tmp_path):
    authority_path = _copy_capability_repository(tmp_path)
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    authority["capabilities"]["architect_to_ce"]["current_main_sha"] = "0" * 40
    authority_path.write_text(json.dumps(authority), encoding="utf-8")
    completed = run_script("scripts/check-capability-truth.py", str(tmp_path))
    assert completed.returncode == 1
    assert "current_main_sha" in completed.stdout


def test_capability_truth_gate_rejects_nested_observed_head_sha(tmp_path):
    authority_path = _copy_capability_repository(tmp_path)
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    authority["capabilities"]["architect_to_ce"]["observation"] = {"observed_head_sha": "1" * 40}
    authority_path.write_text(json.dumps(authority), encoding="utf-8")
    completed = run_script("scripts/check-capability-truth.py", str(tmp_path))
    assert completed.returncode == 1
    assert "observed_head_sha" in completed.stdout


def test_lean_pipeline_has_no_removed_automation_or_duplicate_workflows():
    removed = (
        ".github/workflows/status-after-merge.yml",
        ".github/workflows/prompt-05.yml",
        ".github/workflows/prompt-06.yml",
        ".github/workflows/ui-runtime-smoke.yml",
        ".github/workflows/kroad-011.yml",
        ".github/workflows/prompt-05-producer-integration.yml",
        "scripts/update-status-after-merge.js",
        "scripts/package-ci-evidence.py",
        "scripts/check-workflow-permissions.py",
        "scripts/check-github-action-pinning.py",
        "package.json",
        "docs/IMPLEMENTATION_STATUS.yaml",
        "docs/EV4_SHARED_CONTRACTS_STATUS.md",
        "docs/BEHAVIORAL_RULE_COVERAGE.md",
    )
    for relative in removed:
        assert not (ROOT / relative).exists(), relative


def test_unified_workflow_runs_core_once_and_preserves_legacy_check_names():
    workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert workflow.count("Run full internal quality suite once") == 1
    assert workflow.count("Build wheel once") == 1
    assert workflow.count("Clean-install package and construct UI once") == 1
    assert "actions/upload-artifact" not in workflow
    assert "contents: write" not in workflow
    assert "Setup Node for Kernel boundary only" in workflow
    assert "  skeleton:\n    name: skeleton\n" in workflow
    assert "  python-core:\n    name: python-core\n" in workflow
    reusable = ROOT / ".github/workflows/verify-vendored-common-contract.yml"
    assert reusable.is_file()
    assert "workflow_call:" in reusable.read_text(encoding="utf-8")


def test_cli_inspect_reports_stable_builder_responsive_and_final_gate_truth():
    payload = json.loads(run_cli("inspect").stdout)
    responsive = payload["capabilities"]["builder_to_responsive"]
    final_gate = payload["capabilities"]["final_evidence_gate"]
    assert responsive["official_responsive_validator_integration"] == "implemented"
    assert final_gate["official_responsive_validator_integration"] == "implemented"
    assert final_gate["real_non_synthetic_evidence"] == "insufficient_evidence"
    assert "verification_state" not in responsive
    assert "verification_state" not in final_gate


def test_cli_guarded_ce_to_builder_requires_local_paths():
    completed = run_cli("transition", "ce-to-builder", str(ROOT / "fixtures/valid/architect-stage-bundle.v1.json"))
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert payload["status"] == "insufficient_evidence"
    assert payload["diagnostics"][0]["code"] == "CLI_LOCAL_PATH_REQUIRED"


def test_cli_guarded_builder_to_responsive_rejects_github_url():
    completed = run_cli(
        "transition",
        "builder-to-responsive",
        str(ROOT / "fixtures/valid/architect-stage-bundle.v1.json"),
        "--builder-repo",
        "https://github.com/rezahh107/EV4-Builder-Assistant-Repo",
        "--responsive-repo",
        str(ROOT),
    )
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["diagnostics"][0]["code"] == "CLI_GITHUB_URL_REJECTED"


def test_cli_guarded_final_gate_missing_path_fails_closed():
    completed = run_cli(
        "transition",
        "final-evidence-gate",
        str(ROOT / "fixtures/valid/architect-stage-bundle.v1.json"),
        "--project-gate-repo",
        str(ROOT),
        "--responsive-repo",
        str(ROOT / "missing-responsive-repo"),
    )
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["diagnostics"][0]["code"] == "CLI_LOCAL_PATH_NOT_FOUND"
