from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ev4_transition.io.secure_snapshot import JsonInputSnapshot, SnapshotError, capture_json_snapshot

from .intake import intake_producer_export, transition_producer_export

_SUPPORTED_ROUTES: dict[str, dict[str, Any]] = {
    "architect-to-ce": {
        "producer_stage": "architect",
        "target_stage": "ce",
        "required_repo_fields": ("architect_repo", "ce_repo"),
        "required_repository_roles": ("architect", "ce"),
        "output_filename": "ce-input.json",
        "receipt_filename": "project-gate-a2c-receipt.json",
        "lock_filename": "contracts/locks/architect-to-ce-transition.v1.lock.json",
        "next_action_fa": "فایل ce-input.json را به CE بدهید.",
    },
    "ce-to-builder": {
        "producer_stage": "ce",
        "target_stage": "builder",
        "required_repo_fields": ("ce_repo", "builder_repo"),
        "required_repository_roles": ("ce", "builder"),
        "output_filename": "builder-input.json",
        "receipt_filename": "project-gate-c2b-receipt.json",
        "lock_filename": "contracts/locks/ce-to-builder-transition.v1.lock.json",
        "next_action_fa": "فایل builder-input.json را به Builder بدهید.",
    },
}


def inspect_producer_handoff(
    source_path: str | Path,
    *,
    project_gate_repo: str | Path = ".",
) -> dict[str, Any]:
    """Validate immutable source bytes and resolve a PG-INT route from contract data."""

    snapshot, result = _capture_and_inspect(source_path, Path(project_gate_repo).expanduser())
    del snapshot
    return result


def execute_producer_handoff(
    source_path: str | Path,
    *,
    project_gate_repo: str | Path = ".",
    architect_repo: str | Path | None = None,
    ce_repo: str | Path | None = None,
    builder_repo: str | Path | None = None,
    output_dir: str | Path | None = None,
    output_path: str | Path | None = None,
    receipt_path: str | Path | None = None,
    schema_root: str | Path = "schemas",
    lock_path: str | Path | None = None,
) -> dict[str, Any]:
    """Reuse the existing A2C/C2B dispatchers through one validated routing facade."""

    project_gate_root = Path(project_gate_repo).expanduser()
    snapshot, inspection = _capture_and_inspect(source_path, project_gate_root)
    if snapshot is None or inspection.get("status") != "accepted":
        return _with_operator_artifacts(inspection)

    resolved = str(inspection["resolved_transition"])
    route = _SUPPORTED_ROUTES[resolved]
    supplied = {
        "architect_repo": architect_repo,
        "ce_repo": ce_repo,
        "builder_repo": builder_repo,
    }
    path_diagnostics: list[dict[str, Any]] = []
    for field in route["required_repo_fields"]:
        path_diagnostics.extend(_validate_repo_path(field, supplied.get(field)))
    if path_diagnostics:
        result = deepcopy(inspection)
        result["status"] = _status_from_diagnostics(path_diagnostics)
        result["diagnostics"] = sorted(path_diagnostics, key=_diagnostic_key)
        result["handoff_allowed"] = False
        result["failure_class"] = "repository_path_validation_failed"
        return _with_operator_artifacts(result)

    publication_root = Path(output_dir).expanduser() if output_dir is not None else snapshot.path.parent
    try:
        publication_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return _with_operator_artifacts(
            _failure_from_inspection(
                inspection,
                "invalid",
                "publication_failed",
                _diag(
                    "PG_INT_OUTPUT_DIRECTORY_UNAVAILABLE",
                    "error",
                    "$.output_dir",
                    "The requested output directory could not be prepared.",
                    error_type=type(exc).__name__,
                ),
            )
        )

    selected_output = _resolve_publication_path(output_path, publication_root, route["output_filename"])
    selected_receipt = _resolve_publication_path(receipt_path, publication_root, route["receipt_filename"])
    selected_schema_root = _resolve_project_gate_path(schema_root, project_gate_root)
    selected_lock = _resolve_project_gate_path(lock_path or route["lock_filename"], project_gate_root)

    result = transition_producer_export(
        resolved,
        snapshot.value,
        join_packet_path=project_gate_root / "docs/evidence/JOIN_EVIDENCE_PACKET_v1.json",
        snapshot=snapshot,
        schema_root=selected_schema_root,
        lock_path=selected_lock,
        architect_repo=architect_repo,
        ce_repo=ce_repo,
        builder_repo=builder_repo,
        project_gate_repo=project_gate_root,
        output_path=selected_output,
        receipt_path=selected_receipt,
        registry_path=project_gate_root / "contracts/producer-adoption/ev4-producer-adoption-set.v1.json",
        targets_path=project_gate_root / "contracts/transition-targets/ev4-transition-targets.v1.json",
        repository_root=project_gate_root,
    )
    result["routing"] = deepcopy(inspection["routing"])
    result["source_snapshot"] = deepcopy(inspection["source_snapshot"])
    return _with_operator_artifacts(result)


def required_repository_fields(resolved_transition: str) -> tuple[str, ...]:
    route = _SUPPORTED_ROUTES.get(resolved_transition)
    return tuple(route["required_repo_fields"]) if route else ()


def _capture_and_inspect(
    source_path: str | Path,
    project_gate_root: Path,
) -> tuple[JsonInputSnapshot | None, dict[str, Any]]:
    try:
        snapshot = capture_json_snapshot(source_path)
    except SnapshotError as exc:
        return None, _snapshot_failure(exc)

    intake = intake_producer_export(
        snapshot.value,
        registry_path=project_gate_root / "contracts/producer-adoption/ev4-producer-adoption-set.v1.json",
        targets_path=project_gate_root / "contracts/transition-targets/ev4-transition-targets.v1.json",
        repository_root=project_gate_root,
    )
    result = deepcopy(intake)
    result["source_snapshot"] = _snapshot_metadata(snapshot)
    resolved = result.get("resolved_transition")
    route = _SUPPORTED_ROUTES.get(str(resolved))
    result["routing"] = _routing_metadata(snapshot.value, result, route)

    if result.get("status") != "accepted":
        result["handoff_allowed"] = False
        return snapshot, result
    if route is None:
        result["status"] = "invalid"
        result["failure_class"] = "unsupported"
        result["handoff_allowed"] = False
        result.setdefault("diagnostics", []).append(
            _diag(
                "PG_INT_UNSUPPORTED_TRANSITION",
                "error",
                "$.handoff.target",
                "The validated Producer Gate Export resolves outside S-003 / PG-INT.",
                resolved_transition=resolved,
                supported_transitions=sorted(_SUPPORTED_ROUTES),
            )
        )
        return snapshot, result

    producer = result.get("producer") if isinstance(result.get("producer"), dict) else {}
    observed_stage = producer.get("stage")
    if observed_stage != route["producer_stage"]:
        result["status"] = "invalid"
        result["failure_class"] = "unsupported"
        result["handoff_allowed"] = False
        result.setdefault("diagnostics", []).append(
            _diag(
                "PG_INT_PRODUCER_TARGET_MISMATCH",
                "error",
                "$.handoff.target",
                "Producer stage and handoff target do not form a supported transition pair.",
                producer_stage=observed_stage,
                expected_producer_stage=route["producer_stage"],
                resolved_transition=resolved,
            )
        )
    result["diagnostics"] = sorted(result.get("diagnostics", []), key=_diagnostic_key)
    return snapshot, result


def _routing_metadata(
    artifact: dict[str, Any],
    result: dict[str, Any],
    route: dict[str, Any] | None,
) -> dict[str, Any]:
    producer = result.get("producer") if isinstance(result.get("producer"), dict) else {}
    handoff = artifact.get("handoff") if isinstance(artifact.get("handoff"), dict) else {}
    return {
        "authority": "validated_producer_gate_export",
        "producer_stage": producer.get("stage"),
        "producer_repository": producer.get("repository"),
        "handoff_target": handoff.get("target"),
        "resolved_transition": result.get("resolved_transition"),
        "target_stage": route.get("target_stage") if route else None,
        "required_repository_roles": list(route.get("required_repository_roles", ())) if route else [],
        "filename_used_for_routing": False,
        "operator_transition_selection_used": False,
    }


def _with_operator_artifacts(result: dict[str, Any]) -> dict[str, Any]:
    route = _SUPPORTED_ROUTES.get(str(result.get("resolved_transition")))
    artifact = result.get("downstream_artifact") if isinstance(result.get("downstream_artifact"), dict) else {}
    receipt = result.get("receipt") if isinstance(result.get("receipt"), dict) else {}
    publication = result.get("publication") if isinstance(result.get("publication"), dict) else {}
    artifact_publication = publication.get("ce_input") or publication.get("builder_input")
    receipt_publication = publication.get("receipt")
    artifact_state = artifact.get("status") or (
        artifact_publication.get("state") if isinstance(artifact_publication, dict) else "not_generated"
    )
    receipt_state = receipt.get("status") or (
        receipt_publication.get("state") if isinstance(receipt_publication, dict) else "not_generated"
    )
    artifact_path = artifact.get("path") or (
        artifact_publication.get("path") if isinstance(artifact_publication, dict) else None
    )
    receipt_path = receipt.get("path") or (
        receipt_publication.get("path") if isinstance(receipt_publication, dict) else None
    )
    accepted = result.get("status") == "accepted" and result.get("handoff_allowed") is True
    result["operator_artifacts"] = {
        "next_stage": {
            "filename": route.get("output_filename") if route else None,
            "path": artifact_path,
            "publication_state": artifact_state,
            "downloadable": bool(accepted and artifact_state == "published_verified"),
            "consumable": bool(accepted and artifact_state == "published_verified"),
        },
        "receipt": {
            "filename": route.get("receipt_filename") if route else None,
            "path": receipt_path,
            "publication_state": receipt_state,
            "downloadable": bool(receipt_state == "published_verified"),
        },
        "next_action_fa": (
            route.get("next_action_fa")
            if route and accepted
            else "diagnostics را بررسی و مانع فعلی را رفع کنید."
        ),
    }
    return result


def _validate_repo_path(field: str, value: str | Path | None) -> list[dict[str, Any]]:
    path_expr = f"$.repository_paths.{field}"
    if value is None or not str(value).strip():
        return [_diag("PG_INT_REPOSITORY_PATH_REQUIRED", "insufficient_evidence", path_expr, "A required local repository checkout path is missing.", field=field)]
    text = str(value).strip()
    if _looks_like_url(text):
        return [_diag("PG_INT_GITHUB_URL_REJECTED", "insufficient_evidence", path_expr, "A local checkout directory is required; GitHub URLs are not accepted.", field=field)]
    try:
        path = Path(text).expanduser()
        if not path.exists():
            return [_diag("PG_INT_REPOSITORY_PATH_NOT_FOUND", "insufficient_evidence", path_expr, "The required local repository checkout does not exist.", field=field)]
        if not path.is_dir():
            return [_diag("PG_INT_REPOSITORY_PATH_NOT_DIRECTORY", "insufficient_evidence", path_expr, "The required local repository checkout path is not a directory.", field=field)]
    except (OSError, ValueError) as exc:
        return [_diag("PG_INT_REPOSITORY_PATH_UNSAFE", "insufficient_evidence", path_expr, "The required local repository checkout path is invalid or inaccessible.", field=field, error_type=type(exc).__name__)]
    return []


def _resolve_publication_path(value: str | Path | None, root: Path, default_name: str) -> Path:
    if value is None:
        return root / default_name
    candidate = Path(value).expanduser()
    return candidate if candidate.is_absolute() else root / candidate


def _resolve_project_gate_path(value: str | Path, root: Path) -> Path:
    candidate = Path(value).expanduser()
    return candidate if candidate.is_absolute() else root / candidate


def _looks_like_url(value: str) -> bool:
    lowered = value.lower()
    if lowered.startswith(("git@", "github.com/", "www.github.com/")):
        return True
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return bool(parsed.scheme and parsed.netloc)


def _snapshot_failure(exc: SnapshotError) -> dict[str, Any]:
    return {
        "schema_version": "producer-emitted-transition-result.v1",
        "status": exc.status,
        "acquisition_mode": "producer_emitted_gate_artifact",
        "producer": {},
        "resolved_transition": None,
        "handoff_allowed": False,
        "failure_class": "source_snapshot_failed",
        "diagnostics": [
            _diag(
                exc.code,
                "insufficient_evidence" if exc.status == "insufficient_evidence" else "error",
                "$",
                str(exc),
                **exc.details,
            )
        ],
        "routing": {
            "authority": "validated_producer_gate_export",
            "resolved_transition": None,
            "filename_used_for_routing": False,
            "operator_transition_selection_used": False,
            "required_repository_roles": [],
        },
    }


def _failure_from_inspection(
    inspection: dict[str, Any],
    status: str,
    failure_class: str,
    diagnostic: dict[str, Any],
) -> dict[str, Any]:
    result = deepcopy(inspection)
    result["status"] = status
    result["handoff_allowed"] = False
    result["failure_class"] = failure_class
    result["diagnostics"] = [diagnostic]
    return result


def _snapshot_metadata(snapshot: JsonInputSnapshot) -> dict[str, Any]:
    return {
        "path": str(snapshot.path),
        "filename": snapshot.path.name,
        "sha256_file_bytes": snapshot.sha256_file_bytes,
    }


def _status_from_diagnostics(diagnostics: list[dict[str, Any]]) -> str:
    return "invalid" if any(item.get("severity") == "error" for item in diagnostics) else "insufficient_evidence"


def _diagnostic_key(item: Any) -> tuple[str, str]:
    return (item.get("path", "$"), item.get("code", "")) if isinstance(item, dict) else ("$", "")


def _diag(code: str, severity: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "path": path,
        "message": message,
        "details": details,
        "repair_owner": "Project Gate",
    }
