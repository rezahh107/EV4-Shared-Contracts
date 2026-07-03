from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .canonical_json import write_canonical_json
from .diagnostics import diagnostic, Diagnostic


def run_architect_validator(repo_root: str | Path, payload: dict[str, Any]) -> list[Diagnostic]:
    return _run_validator(repo_root, "scripts/check-architect-stage-payload.py", payload, "PG_A2C_ARCHITECT_OFFICIAL_VALIDATOR_FAILED")


def run_ce_validator(repo_root: str | Path, payload: dict[str, Any]) -> list[Diagnostic]:
    return _run_validator(repo_root, "scripts/validate-ce-architect-stage-intake.py", payload, "PG_A2C_CE_OFFICIAL_VALIDATOR_FAILED")


def _run_validator(repo_root: str | Path, script_rel: str, payload: dict[str, Any], code: str) -> list[Diagnostic]:
    root = Path(repo_root).resolve()
    script = root / script_rel
    if not script.exists():
        return [diagnostic(code, "error", "Official validator script is missing.", "$", validator=str(script))]
    with tempfile.TemporaryDirectory(prefix="ev4-pg-validator-") as td:
        payload_path = Path(td) / "payload.json"
        write_canonical_json(payload_path, payload)
        env = {"LC_ALL": "C.UTF-8", "LANG": "C.UTF-8", "PYTHONHASHSEED": "0", **{k: v for k, v in os.environ.items() if k in {"PATH", "PYTHONPATH", "HOME"}}}
        completed = subprocess.run(
            ["python", str(script), "--repo-root", str(root), "--file", str(payload_path), "--format", "json"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            env=env,
            timeout=30,
        )
    if completed.returncode == 0:
        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return [diagnostic(code, "error", "Official validator returned non-JSON success output.", "$")]
        if result.get("status") == "valid":
            return []
    if completed.returncode == 2:
        try:
            result = json.loads(completed.stdout)
            return [diagnostic(code, "insufficient_evidence", "Official validator returned insufficient evidence.", "$", validator_status=result.get("status"), diagnostics=result.get("diagnostics", []))]
        except json.JSONDecodeError:
            pass
    details: dict[str, Any] = {"returncode": completed.returncode, "stderr": completed.stderr[:1000]}
    try:
        details["validator_result"] = json.loads(completed.stdout)
    except json.JSONDecodeError:
        details["stdout"] = completed.stdout[:1000]
    return [diagnostic(code, "error", "Official validator rejected the payload.", "$", **details)]
