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
        "next_action_fa": "فایل ce-input.json را به CE بدهید.",
    },
    "ce-to-builder": {
        "producer_stage": "ce",
        "target_stage": "builder",
        "required_repo_fields": ("ce_repo", "builder_repo"),
        "required_repository_roles": ("ce", "builder"),
        "output_filename": "builder-input.json",
        "receipt_filename": "project-gate-c2b-receipt.json",
        "next_action_fa": "فایل builder-input.json را به Builder بدهید.",
    },
}


def inspect_producer_handoff(
    source_path: str | Path,
    *,
    project_gate_repo: str | Path = ".",
) -> dict[str, Any]:
    """Validate immutable Producer Gate Export bytes and resolve a supported route.

    Routing authority is the validated export plus Project Gate adoption/target
    registries. The source filename and any operator-selected transition are ignored.
    """

    project_gate_root = Path(project_gate_repo).expanduser()
    try:
        snapshot = capture_json_snapshot(source_path)
    except SnapshotError as exc:
        return _snapshot_failure(exc)

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
    if result.get("status") != "accepted":
        result["routing"] = _routing_metadata(result, route)
        result["handoff_allowed"] = False
        return result
    if route is None:
        result["status"] = "invalid"
        result["failure_class"] = "unsupported"
        result["handoff_allowed"] = False
        result.setdefault("diagnostics", []).append(
            _diag(
                "PG_INT_UNSUPPORTED_TRANSITION",
                "error",
                "$.handoff.target",
                "The validated Producer Gate Export resolves to a transition outside S-003 / PG-INT.",
                resolved_transition=resolved,
                supported_transitions=sorted(_SUPPORTED_ROUTES),
            )
        )
    result["routing"] = _routing_metadata(result, route)
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
    """Execute the validated A2C or C2B producer handoff through existing dispatchers."""

    inspection = inspect_producer_handoff(source_path, project_gate_repo=project_gate_repo)
    if inspection.get("status") != "accepted":
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
        result["diagnostics"] = sorted(path_diagnostics, key=lambda item: (item.get("path", "$"), item.get("code", "")))
        result["handoff_allowed"] = False
        result["failure_class"] = "repository_path_validation_failed"
        return _with_operator_artifacts(result)

    source = Path(source_path).expanduser()
    project_gate_root = Path(project_gate_repo).expanduser()
    publication_root = Path(output_dir).expanduser() if output_dir is not None else source.parent
    try:
        publication_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        result = deepcopy(inspection)
        result["status"] = "invalid"
        result["handoff_allowed"] = False
        result["failure_class"] = "publication_failed"
        result["diagnostics"] = [
            _diag(
                "PG_INT_OUTPUT_DIRECTORY_UNAVAILABLE",
                "error",
                "$.output_dir",
                "The requested output directory could not be prepared.",
                error_type=type(exc).__name__,
            )
        ]
        return _with_operator_artifacts(result)

    selected_output = Path(output_path).expanduser() if output_path is not None else publication_root / route["output_filename"]
    selected_receipt = Path(receipt_path).expanduser() if receipt_path is not None else publication_root / route["receipt_filename"]
    selected_schema_root = Path(schema_root).expanduser()
    if not selected_schema_root.is_absolute():
        selected_schema_root = project_gate_root / selected_schema_root
    selected_lock = Path(lock_path).expanduser() if lock_path is not None else project_gate_root / (
        "contracts/locks/architect-to-ce-transition.v1.lock.json"
        if resolved == "architect-to-ce"
        else "contracts/locks/ce-to-builder-transition.v1.lock.json"
    )

    snapshot = _snapshot_from_inspection(inspection, source)
    if snapshot is None:
        try:
            snapshot = capture_json_snapshot(source)
        except SnapshotError as exc:
            return _with_operator_artifacts(_snapshot_failure(exc))

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


def _snapshot_from_inspection(inspection: dict[str, Any], source: Path) -> JsonInputSnapshot | None:
    metadata = inspection.get("source_snapshot")
    if not isinstance(metadata, dict):
        return None
    try:
        return capture_json_snapshot(source)
    except SnapshotError:
        return None


def _routing_metadata(result: dict[str, Any], route: dict[str, Any] | None) -> dict[str, Any]:
    producer = result.get("producer") if isinstance(result.get("producer"), dict) else {}
    return {
        "authority": "validated_producer_gate_export",
        "producer_stage": producer.get("stage"),
        "producer_repository": producer.get("repository"),
        "handoff_target": ((result.get("handoff") or {}).get("target") if isinstance(result.get("handoff"), dict) else None),
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
    artifact_published = artifact.get("status") == "published_verified" and isinstance(artifact.get("path"), str)
    receipt_published = receipt.get("status") == "published_verified" and isinstance(receipt.get("path"), str)
    result["operator_artifacts"] = {
        "next_stage": {
            "filename": route.get("output_filename") if route else None,
            "path": artifact.get("path"),
            "publication_state": artifact.get("status", "not_generated"),
            "downloadable": bool(artifact_published and result.get("handoff_allowed") is True and result.get("status") == "accepted"),
            "consumable": bool(artifact_published and result.get("handoff_allowed") is True and result.get("status") == "accepted"),
        },
        "receipt": {
            "filename": route.get("receipt_filename") if route else None,
            "path": receipt.get("path"),
            "publication_state": receipt.get("status", "not_generated"),
            "downloadable": bool(receipt_published),
        },
        "next_action_fa": route.get("next_action_fa") if route and result.get("handoff_allowed") is True else "diagnostics را بررسی و مانع فعلی را رفع کنید.",
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


def _snapshot_metadata(snapshot: JsonInputSnapshot) -> dict[str, Any]:
    return {
        "path": str(snapshot.path),
        "filename": snapshot.path.name,
        "sha256_file_bytes": snapshot.sha256_file_bytes,
    }


def _status_from_diagnostics(diagnostics: list[dict[str, Any]]) -> str:
    severities = {item.get("severity") for item in diagnostics}
    return "invalid" if "error" in severities else "insufficient_evidence"


def _diag(code: str, severity: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "path": path,
        "message": message,
        "details": details,
        "repair_owner": "Project Gate",
    }
