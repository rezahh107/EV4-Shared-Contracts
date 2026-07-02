import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "ev4_transition.cli", "--schema-root", str(ROOT / "schemas"), "--transition-root", str(ROOT / "transitions"), *args], cwd=ROOT, text=True, capture_output=True, check=False)


def test_cli_validate_json():
    completed = run_cli("validate", str(ROOT / "fixtures/valid/architect-stage-bundle.v1.json"))
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["status"] == "valid"


def test_cli_transition_json():
    completed = run_cli("transition", str(ROOT / "fixtures/valid/architect-stage-bundle.v1.json"), "--transition-id", "architect-to-ce.v1")
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["status"] == "accepted"


def test_cli_persian_summary_for_insufficient_evidence():
    completed = run_cli("validate", str(ROOT / "fixtures/invalid/insufficient-evidence.v1.json"), "--format", "persian")
    assert completed.returncode == 2
    assert "شواهد کافی نیست" in completed.stdout
