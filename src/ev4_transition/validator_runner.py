from __future__ import annotations

from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic
from .runners import diagnostics_from_outcome, execute_validator

ARCHITECT_REPO = "rezahh107/EV4-Architect-Repo"
CE_REPO = "rezahh107/EV4-Constructability-Engineer-Repo"
UNKNOWN_COMMIT = "unknown"


def run_architect_validator(repo_root: str | Path, payload: dict[str, Any]) -> list[Diagnostic]:
    outcome = execute_validator(
        repo_root=repo_root,
        owner_repo=ARCHITECT_REPO,
        owner_commit=UNKNOWN_COMMIT,
        validator_path="scripts/check-architect-stage-payload.py",
        payload=payload,
    )
    return diagnostics_from_outcome(outcome)


def run_ce_validator(repo_root: str | Path, payload: dict[str, Any], source_bundle: dict[str, Any]) -> list[Diagnostic]:
    outcome = execute_validator(
        repo_root=repo_root,
        owner_repo=CE_REPO,
        owner_commit=UNKNOWN_COMMIT,
        validator_path="scripts/validate-ce-architect-stage-intake.py",
        payload=payload,
        source_bundle=source_bundle,
    )
    return diagnostics_from_outcome(outcome)
