from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from ev4_transition.canonical_json import bytes_sha256, canonical_sha256, load_json_file, write_canonical_json
from ev4_transition.contract_source import ContractSource, LocalCheckoutContractSource
from ev4_transition.diagnostics import Diagnostic, diagnostic, project_gate_status_from_diagnostics, sort_diagnostics

TRANSITION_ID = "ev4-builder-to-responsive-transition@1.0.0"
TRANSITION_VERSION = "1.0.0"
LOCK_SCHEMA_VERSION = "builder-to-responsive-transition-lock.v1"
BUILDER_REPO = "rezahh107/EV4-Builder-Assistant-Repo"
RESPONSIVE_REPO = "rezahh107/EV4-Responsive-Architect"
BUILDER_COMMIT = "69a2c61edf6d06b4418ad770fcefbfdffcf275d6"
RESPONSIVE_COMMIT = "main"
RESPONSIVE_INPUT_SCHEMA = "ev4-builder-responsive-input@0.1.0"
RESPONSIVE_INPUT_SCHEMA_PATH = "schemas/ev4-builder-responsive-input.schema.json"
RESPONSIVE_INPUT_VALIDATOR = "validation/e2e/run_builder_responsive_input_boundary_check.py"

FORBIDDEN_CLAIMS = {
    "production_ready",
    "release_ready",
    "pixel_perfect",
    "live_render_validated",
    "export_json_validated",
    "accessibility_passed",
    "responsive_correctness_validated",
    "ci_success_as_frontend_evidence",
    "frontend_correctness",
    "production_readiness",
    "responsive_correctness",
}


@dataclass(frozen=True)
class ExpectedDependency:
    role: str
    repository: str
    accepted_commit: str
    path: str
    contract_or_schema_id: str
    identity_marker: str


_EXPECTED_ITEMS = [
    ExpectedDependency("builder_handoff_boundary", BUILDER_REPO, BUILDER_COMMIT, "docs/BUILDER_TO_RESPONSIVE_HANDOFF_BOUNDARY.md", "builder-to-responsive-handoff-boundary@0.1.0", "Builder"),
    ExpectedDependency("builder_context_schema", BUILDER_REPO, BUILDER_COMMIT, "schemas/builder-context-package.schema.json", "ev4-builder-context-package@1.0.0", "ev4-builder-context-package"),
    ExpectedDependency("builder_context_validator", BUILDER_REPO, BUILDER_COMMIT, "scripts/validate-package.mjs", "builder-context-validator", "validate"),
    ExpectedDependency("builder_action_batch_schema", BUILDER_REPO, BUILDER_COMMIT, "schemas/action-batch.schema.json", "ev4-action-batch@1.0.0", "action"),
    ExpectedDependency("builder_action_batch_validator", BUILDER_REPO, BUILDER_COMMIT, "scripts/validate-action-batch.mjs", "validate-action-batch", "action"),
    ExpectedDependency("builder_layout_check_schema", BUILDER_REPO, BUILDER_COMMIT, "schemas/layout-check.schema.json", "ev4-layout-check@0.1.0", "layout"),
    ExpectedDependency("builder_layout_check_validator", BUILDER_REPO, BUILDER_COMMIT, "scripts/validate-layout-check.mjs", "validate-layout-check", "layout"),
    ExpectedDependency("builder_completion_gate_schema", BUILDER_REPO, BUILDER_COMMIT, "schemas/completion-gate.schema.json", "ev4-completion-gate@0.1.0", "completion"),
    ExpectedDependency("builder_completion_gate_validator", BUILDER_REPO, BUILDER_COMMIT, "scripts/validate-completion-gate.mjs", "validate-completion-gate", "completion"),
    ExpectedDependency("builder_execution_evidence_schema", BUILDER_REPO, BUILDER_COMMIT, "schemas/real-elementor-execution-evidence.schema.json", "ev4-real-elementor-execution-evidence@1.0.0", "evidence"),
    ExpectedDependency("builder_execution_evidence_validator", BUILDER_REPO, BUILDER_COMMIT, "scripts/validate-real-elementor-execution-evidence.mjs", "validate-real-elementor-execution-evidence", "evidence"),
    ExpectedDependency("responsive_input_boundary", RESPONSIVE_REPO, RESPONSIVE_COMMIT, "contracts/BUILDER_TO_RESPONSIVE_INPUT_BOUNDARY.md", "builder-responsive-input-boundary", "Builder"),
    ExpectedDependency("responsive_input_schema", RESPONSIVE_REPO, RESPONSIVE_COMMIT, RESPONSIVE_INPUT_SCHEMA_PATH, RESPONSIVE_INPUT_SCHEMA, "builder-responsive"),
    ExpectedDependency("responsive_input_validator", RESPONSIVE_REPO, RESPONSIVE_COMMIT, RESPONSIVE_INPUT_VALIDATOR, "builder-responsive-input-boundary-validator", "boundary"),
]
EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES = {item.role: item for item in _EXPECTED_ITEMS}
REQUIRED_ROLES = set(EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES)


@dataclass(frozen=True)
class BuilderToResponsiveTransitionConfig:
    schema_root: Path
    lock: dict[str, Any]
    builder_repo_root: Path | None = None
    responsive_repo_root: Path | None = None
    timeout_seconds: float = 30
    require_real_evidence: bool = True


def verify_builder_to_responsive_lock(lock: dict[str, Any], source: ContractSource) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not isinstance(lock, dict):
        return [diagnostic("PG.B2R.LOCK_NOT_OBJECT", "error", "Builder→Responsive lock manifest must be an object.", "$")]
    if lock.get("schema_version") != LOCK_SCHEMA_VERSION:
        diagnostics.append(diagnostic("PG.B2R.LOCK_VERSION_MISMATCH", "error", "Builder→Responsive lock schema version is missing or unknown.", "$.schema_version", expected=LOCK_SCHEMA_VERSION, actual=lock.get("schema_version")))
    if lock.get("transition_id") != TRANSITION_ID:
        diagnostics.append(diagnostic("PG.B2R.LOCK_TRANSITION_ID_MISMATCH", "error", "Builder→Responsive lock transition id does not match this transition.", "$.transition_id", expected=TRANSITION_ID, actual=lock.get("transition_id")))
    files = lock.get("files")
    if not isinstance(files, list):
        diagnostics.append(diagnostic("PG.B2R.LOCK_FILES_NOT_ARRAY", "error", "Builder→Responsive lock files must be an array.", "$.files"))
        return sort_diagnostics(diagnostics)
    seen: set[str] = set()
    for index, item in enumerate(files):
        path = f"$.files[{index}]"
        if not isinstance(item, dict):
            diagnostics.append(diagnostic("PG.B2R.LOCK_ENTRY_NOT_OBJECT", "error", "Lock entry must be an object.", path))
            continue
        role = item.get("role")
        expected = EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES.get(role)
        if expected is None:
            diagnostics.append(diagnostic("PG.B2R.LOCK_ROLE_UNEXPECTED", "error", "Unexpected lock role.", f"{path}.role", role=role))
            continue
        if role in seen:
            diagnostics.append(diagnostic("PG.B2R.LOCK_ROLE_DUPLICATE", "error", "Duplicate lock role.", f"{path}.role", role=role))
        seen.add(role)
        for field, expected_value, code in [
            ("repository", expected.repository, "PG.B2R.LOCK_REPOSITORY_MISMATCH"),
            ("accepted_commit", expected.accepted_commit, "PG.B2R.LOCK_COMMIT_MISMATCH"),
            ("path", expected.path, "PG.B2R.LOCK_PATH_MISMATCH"),
            ("contract_or_schema_id", expected.contract_or_schema_id, "PG.B2R.LOCK_IDENTITY_MISMATCH"),
        ]:
            if item.get(field) != expected_value:
                diagnostics.append(diagnostic(code, "error", "Lock entry does not match expected dependency.", f"{path}.{field}", expected=expected_value, actual=item.get(field), role=role))
        try:
            content = source.read_bytes(expected.repository, expected.accepted_commit, expected.path)
        except Exception as exc:
            diagnostics.append(diagnostic("PG.B2R.OWNER_FILE_READ_FAILED", "insufficient_evidence", "Pinned owner file could not be read.", path, role=role, repository=expected.repository, file_path=expected.path, error_type=type(exc).__name__))
            continue
        if item.get("sha256_file_bytes") != bytes_sha256(content):
            diagnostics.append(diagnostic("PG.B2R.EXTERNAL_HASH_MISMATCH", "error", "Pinned owner file hash does not match lock manifest.", path, role=role, repository=expected.repository, file_path=expected.path))
        if expected.identity_marker not in content.decode("utf-8", errors="replace"):
            diagnostics.append(diagnostic("PG.B2R.EXTERNAL_IDENTITY_MISMATCH", "error", "Pinned owner file identity marker was not found.", path, role=role, repository=expected.repository, file_path=expected.path, expected_marker=expected.identity_marker))
    missing = sorted(REQUIRED_ROLES - seen)
    if missing:
        diagnostics.append(diagnostic("PG.B2R.LOCK_ROLE_MISSING", "error", "Builder→Responsive lock is missing required owner dependency roles.", "$.files", missing_roles=missing))
    return sort_diagnostics(diagnostics)


def transition_from_local_paths(builder_input: Any, schema_root: str | Path, lock_path: str | Path, builder_repo: str | Path, responsive_repo: str | Path, *, timeout_seconds: float = 30, require_real_evidence: bool = True) -> dict[str, Any]:
    config = BuilderToResponsiveTransitionConfig(Path(schema_root), load_json_file(lock_path), Path(builder_repo), Path(responsive_repo), timeout_seconds, require_real_evidence)
    source = LocalCheckoutContractSource({BUILDER_REPO: Path(builder_repo), RESPONSIVE_REPO: Path(responsive_repo)})
    return transition_builder_to_responsive(builder_input, source, config)


def transition_builder_to_responsive(builder_input: Any, contract_source: ContractSource, config: BuilderToResponsiveTransitionConfig, progress_sink: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    diagnostics: list[Diagnostic] = []
    accepted_requires = {
        "builder_evidence_refs_present": False,
        "builder_lock_hashes_match": False,
        "responsive_input_schema_verified": False,
        "responsive_input_validator_passed": False,
        "viewport_evidence_present": False,
        "no_forbidden_claim": False,
        "synthetic_only_evidence_not_used_as_real_evidence": False,
        "result_schema_valid": False,
    }

    if not isinstance(builder_input, dict):
        diagnostics.append(diagnostic("PG.B2R.INPUT_NOT_OBJECT", "error", "Builder→Responsive input must be an object.", "$", observed_type=type(builder_input).__name__))
        return _result(builder_input, None, diagnostics, accepted_requires, config)

    responsive_input = builder_input.get("responsive_input") if isinstance(builder_input.get("responsive_input"), dict) else builder_input
    if not isinstance(responsive_input, dict):
        diagnostics.append(diagnostic("PG.B2R.RESPONSIVE_INPUT_MISSING", "insufficient_evidence", "Responsive input packet is missing.", "$.responsive_input"))
        return _result(builder_input, None, diagnostics, accepted_requires, config)

    lock_diags = verify_builder_to_responsive_lock(config.lock, contract_source)
    diagnostics.extend(lock_diags)
    accepted_requires["builder_lock_hashes_match"] = not any(d.severity in {"error", "insufficient_evidence"} for d in lock_diags)

    forbidden = _find_forbidden_claims(builder_input)
    if forbidden:
        diagnostics.append(diagnostic("PG.B2R.FORBIDDEN_CLAIM", "error", "Builder→Responsive input contains forbidden readiness/correctness claims.", "$", forbidden_claims=forbidden))
    accepted_requires["no_forbidden_claim"] = not forbidden

    if _contains_key_or_value(builder_input, "ci_success_as_frontend_evidence"):
        diagnostics.append(diagnostic("PG.B2R.CI_FRONTEND_CORRECTNESS_CLAIM", "error", "CI success is not frontend correctness evidence.", "$"))
    if _contains_key_or_value(builder_input, "raw_screenshot") or _contains_key_or_value(builder_input, "screenshot_only"):
        diagnostics.append(diagnostic("PG.B2R.RAW_SCREENSHOT_CORRECTNESS_CLAIM", "insufficient_evidence", "Raw screenshots alone do not prove responsive correctness.", "$"))

    evidence_missing = _missing_builder_evidence(responsive_input)
    if evidence_missing:
        diagnostics.append(diagnostic("PG.B2R.BUILDER_EVIDENCE_MISSING", "insufficient_evidence", "Required Builder evidence references are missing.", "$.builder_evidence", missing_evidence=evidence_missing))
    accepted_requires["builder_evidence_refs_present"] = not evidence_missing

    viewport_missing = _missing_viewport_evidence(responsive_input)
    if viewport_missing:
        diagnostics.append(diagnostic("PG.B2R.VIEWPORT_EVIDENCE_MISSING", "insufficient_evidence", "Viewport evidence is required before accepted Responsive intake.", "$.viewport_evidence", missing_viewports=viewport_missing))
    accepted_requires["viewport_evidence_present"] = not viewport_missing

    if _synthetic_only(builder_input):
        diagnostics.append(diagnostic("PG.B2R.SYNTHETIC_ONLY_EVIDENCE", "insufficient_evidence", "Synthetic fixtures cannot be used as real Responsive evidence.", "$"))
    accepted_requires["synthetic_only_evidence_not_used_as_real_evidence"] = not _synthetic_only(builder_input)

    schema = _load_responsive_schema(contract_source, diagnostics)
    if schema is not None:
        accepted_requires["responsive_input_schema_verified"] = True
        for err in sorted(Draft202012Validator(schema).iter_errors(responsive_input), key=lambda item: (list(item.path), item.message)):
            diagnostics.append(diagnostic("PG.B2R.RESPONSIVE_SCHEMA_VALIDATION_FAILED", "error", err.message, _json_path(list(err.path))))

    validator_ok = _run_responsive_validator(config, responsive_input, diagnostics)
    accepted_requires["responsive_input_validator_passed"] = validator_ok

    return _result(builder_input, responsive_input, diagnostics, accepted_requires, config)


def _load_responsive_schema(source: ContractSource, diagnostics: list[Diagnostic]) -> dict[str, Any] | None:
    try:
        raw = source.read_bytes(RESPONSIVE_REPO, RESPONSIVE_COMMIT, RESPONSIVE_INPUT_SCHEMA_PATH)
        schema = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        diagnostics.append(diagnostic("PG.B2R.RESPONSIVE_SCHEMA_UNAVAILABLE", "insufficient_evidence", "Responsive-owned input schema is absent or unreadable.", "$.responsive_schema", error_type=type(exc).__name__))
        return None
    return schema if isinstance(schema, dict) else None


def _run_responsive_validator(config: BuilderToResponsiveTransitionConfig, responsive_input: dict[str, Any], diagnostics: list[Diagnostic]) -> bool:
    if config.responsive_repo_root is None:
        diagnostics.append(diagnostic("PG.B2R.RESPONSIVE_VALIDATOR_MISSING", "insufficient_evidence", "Responsive repository checkout is required to run the official input boundary validator.", "$.responsive_validator"))
        return False
    validator = Path(config.responsive_repo_root) / RESPONSIVE_INPUT_VALIDATOR
    if not validator.exists():
        diagnostics.append(diagnostic("PG.B2R.RESPONSIVE_VALIDATOR_MISSING", "insufficient_evidence", "Official Responsive input boundary validator is absent.", "$.responsive_validator", validator_path=RESPONSIVE_INPUT_VALIDATOR))
        return False
    with tempfile.TemporaryDirectory(prefix="ev4-b2r-") as td:
        payload = Path(td) / "builder-responsive-input.json"
        write_canonical_json(payload, responsive_input)
        completed = subprocess.run([sys.executable, str(validator), str(payload)], cwd=config.responsive_repo_root, text=True, capture_output=True, timeout=config.timeout_seconds, check=False)
    if completed.returncode != 0:
        diagnostics.append(diagnostic("PG.B2R.RESPONSIVE_VALIDATOR_FAILED", "insufficient_evidence", "Official Responsive input boundary validator did not pass.", "$.responsive_validator", exit_code=completed.returncode))
        return False
    return True


def _result(original: Any, responsive_input: dict[str, Any] | None, diagnostics: list[Diagnostic], accepted_requires: dict[str, bool], config: BuilderToResponsiveTransitionConfig) -> dict[str, Any]:
    ordered = sort_diagnostics(diagnostics)
    if not ordered and not all(accepted_requires.values()):
        missing = sorted(k for k, v in accepted_requires.items() if not v and k != "result_schema_valid")
        ordered = sort_diagnostics([diagnostic("PG.B2R.ACCEPTED_REQUIRES_MISSING", "insufficient_evidence", "Accepted status requires every accepted_requires item to be true.", "$.accepted_requires", missing=missing)])
    status = project_gate_status_from_diagnostics(ordered)
    result = {
        "schema_version": "builder-to-responsive-transition-result.v1",
        "result_type": "builder_to_responsive_transition",
        "transition_id": TRANSITION_ID,
        "transition_version": TRANSITION_VERSION,
        "status": status,
        "diagnostics": [d.to_dict() for d in ordered],
        "accepted_requires": {**accepted_requires, "result_schema_valid": True},
        "hashes": {"source_input_hash": {"algorithm": "sha256", "canonicalization": "ev4-canonical-json.v1", "scope": "source_input", "value": _safe_hash(original)}},
        "output": responsive_input if status == "accepted" else None,
    }
    _validate_result_schema(config.schema_root, result)
    return result


def _validate_result_schema(schema_root: Path, result: dict[str, Any]) -> None:
    path = schema_root / "builder-to-responsive-transition-result" / "builder-to-responsive-transition-result.v1.schema.json"
    if not path.exists():
        return
    errors = sorted(Draft202012Validator(load_json_file(path)).iter_errors(result), key=lambda item: (list(item.path), item.message))
    if errors:
        raise RuntimeError("; ".join(f"{_json_path(list(e.path))}: {e.message}" for e in errors))


def _missing_builder_evidence(value: dict[str, Any]) -> list[str]:
    evidence = value.get("builder_evidence") if isinstance(value.get("builder_evidence"), dict) else {}
    required = ["action_batch_ref", "execution_evidence_ref", "layout_check_ref", "completion_gate_ref"]
    return [key for key in required if not evidence.get(key)]


def _missing_viewport_evidence(value: dict[str, Any]) -> list[str]:
    viewport = value.get("viewport_evidence") if isinstance(value.get("viewport_evidence"), dict) else {}
    return [key for key in ["desktop", "tablet", "mobile"] if not isinstance(viewport.get(key), dict) or not viewport[key].get("evidence_ref")]


def _find_forbidden_claims(value: Any) -> list[str]:
    found: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                if isinstance(key, str) and key in FORBIDDEN_CLAIMS:
                    found.add(key)
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, str):
            token = node.strip()
            if token in FORBIDDEN_CLAIMS:
                found.add(token)

    walk(value)
    return sorted(found)


def _contains_key_or_value(value: Any, needle: str) -> bool:
    if isinstance(value, dict):
        return any(k == needle or _contains_key_or_value(v, needle) for k, v in value.items())
    if isinstance(value, list):
        return any(_contains_key_or_value(v, needle) for v in value)
    return value == needle


def _synthetic_only(value: Any) -> bool:
    return _contains_key_or_value(value, "synthetic_only") or _contains_key_or_value(value, "synthetic_fixture")


def _safe_hash(value: Any) -> str:
    try:
        return canonical_sha256(value)
    except Exception:
        return bytes_sha256(b"unhashable")


def _json_path(parts: list[Any]) -> str:
    out = "$"
    for part in parts:
        out += f"[{part}]" if isinstance(part, int) else f".{part}"
    return out
