from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ev4_transition.bundle_validator import ResultValidationError
from ev4_transition.canonical_json import CANONICAL_JSON_VERSION, canonical_sha256, load_json_file
from ev4_transition.io.safe_publication import (
    PublicationError,
    StagedJson,
    discard_staged_json,
    publish_staged_json,
    resolve_publication_paths,
    stage_canonical_json,
)
from ev4_transition.io.secure_snapshot import JsonInputSnapshot, SnapshotError, verify_snapshot_unchanged
from ev4_transition.presentation.status_mapping import normalize_status
from ev4_transition.runners.official_tools import execute_builder_output_validator
from ev4_transition.runners.repository_identity import inspect_checkout
from ev4_transition.transitions.ce_to_builder import (
    BUILDER_COMMIT,
    BUILDER_CONTEXT_SCHEMA,
    BUILDER_REPO,
    CE_COMMIT,
    CE_REPO,
    PG_REPO,
    TRANSITION_ID,
    TRANSITION_VERSION,
    transition_from_local_paths,
)

RECEIPT_SCHEMA_ID = "project-gate-c2b-receipt.v1"
BUILDER_OUTPUT_VALIDATOR_PATH = "scripts/validate-package.mjs"


def dispatch_ce_export(
    artifact: dict[str, Any],
    intake_result: dict[str, Any],
    *,
    snapshot: JsonInputSnapshot,
    schema_root: str | Path,
    lock_path: str | Path,
    ce_repo: str | Path,
    builder_repo: str | Path,
    project_gate_repo: str | Path,
    output_path: str | Path,
    receipt_path: str | Path,
) -> dict[str, Any]:
    """Run the authoritative CE→Builder transition and publish separate artifacts."""

    identities = {
        "project_gate": inspect_checkout(project_gate_repo, expected_repository=PG_REPO),
        "ce": inspect_checkout(ce_repo, expected_repository=CE_REPO, expected_commit=CE_COMMIT),
        "builder": inspect_checkout(builder_repo, expected_repository=BUILDER_REPO, expected_commit=BUILDER_COMMIT),
    }
    identity_diagnostics = [
        diagnostic
        for identity in identities.values()
        for diagnostic in identity.get("diagnostics", [])
        if isinstance(diagnostic, dict)
    ]
    if identity_diagnostics:
        status = "invalid" if any(item.get("severity") == "error" for item in identity_diagnostics) else "insufficient_evidence"
        return _base_result(intake_result, status, identity_diagnostics, identities=identities)

    final_bundle = artifact.get("final_stage_bundle")
    if not isinstance(final_bundle, dict):
        return _base_result(
            intake_result,
            "invalid",
            [_diag("PG_C2B_FINAL_STAGE_BUNDLE_MISSING", "error", "$.final_stage_bundle", "The validated Producer Gate Export does not contain a CE Stage Evidence Bundle.")],
            identities=identities,
        )

    try:
        transition_result = transition_from_local_paths(
            final_bundle,
            schema_root,
            lock_path,
            ce_repo,
            builder_repo,
            require_real_evidence=True,
        )
    except (OSError, json.JSONDecodeError) as exc:
        return _base_result(
            intake_result,
            "invalid",
            [_lock_read_diag(exc)],
            identities=identities,
        )
    except ResultValidationError as exc:
        return _base_result(
            intake_result,
            "invalid",
            [_diag("TRANSITION_RESULT_SCHEMA_VALIDATION_FAILED", "error", "$", "The CE→Builder transition result failed its Project Gate schema.", error=str(exc))],
            identities=identities,
        )

    transition_status = normalize_status(str(transition_result.get("status")))
    diagnostics = list(transition_result.get("diagnostics") or [])
    source_handoff_allowed = bool((artifact.get("handoff") or {}).get("allowed"))
    if transition_status == "accepted" and not source_handoff_allowed:
        transition_status = "insufficient_evidence"
        diagnostics.append(
            _diag(
                "PG_C2B_SOURCE_HANDOFF_NOT_ALLOWED",
                "insufficient_evidence",
                "$.handoff.allowed",
                "The CE producer export does not authorize a Builder handoff.",
            )
        )

    builder_input = transition_result.get("output")
    handoff_allowed = (
        transition_status == "accepted"
        and source_handoff_allowed
        and isinstance(builder_input, dict)
        and builder_input.get("schema") == BUILDER_CONTEXT_SCHEMA
        and (builder_input.get("input_authorization") or {}).get("decision") == "approved"
    )
    if not handoff_allowed or not isinstance(builder_input, dict):
        return _base_result(
            intake_result,
            transition_status,
            diagnostics,
            identities=identities,
            transition_result=transition_result,
        )

    try:
        output, receipt = resolve_publication_paths(
            source_path=snapshot.path,
            output_path=output_path,
            receipt_path=receipt_path,
        )
    except PublicationError as exc:
        diagnostics.append(_publication_diag(exc))
        result = _base_result(
            intake_result,
            "invalid",
            diagnostics,
            identities=identities,
            transition_result=transition_result,
        )
        result["failure_class"] = "publication_failed"
        return result

    staged_output: StagedJson | None = None
    output_publication: dict[str, Any] | None = None
    try:
        staged_output = stage_canonical_json(output, builder_input)
        verify_snapshot_unchanged(snapshot)
        output_publication = publish_staged_json(staged_output)
        staged_output = None
    except (PublicationError, SnapshotError) as exc:
        cleanup_diagnostics: list[dict[str, Any]] = []
        try:
            discard_staged_json(staged_output)
        except PublicationError as cleanup_exc:
            cleanup_diagnostics.append(_publication_diag(cleanup_exc))
        diagnostics.append(_publication_diag(exc))
        diagnostics.extend(cleanup_diagnostics)
        result = _base_result(
            intake_result,
            "invalid",
            diagnostics,
            identities=identities,
            transition_result=transition_result,
        )
        result["publication"] = {
            "builder_input": output_publication or {"path": str(output), "state": "not_published"},
            "receipt": {"path": str(receipt), "state": "not_published"},
        }
        result["failure_class"] = "publication_failed"
        return result

    try:
        published_builder_input = load_json_file(output)
    except Exception as exc:
        diagnostics.append(
            _diag(
                "PG_C2B_POST_WRITE_READ_FAILED",
                "error",
                "$.publication.builder_input",
                "The published Builder input could not be read back as strict JSON.",
                error_type=type(exc).__name__,
            )
        )
        result = _base_result(intake_result, "invalid", diagnostics, identities=identities, transition_result=transition_result)
        result["publication"] = {
            "builder_input": output_publication,
            "receipt": {"path": str(receipt), "state": "not_published"},
        }
        result["failure_class"] = "publication_failed"
        return result

    if canonical_sha256(published_builder_input) != canonical_sha256(builder_input):
        diagnostics.append(
            _diag(
                "PG_C2B_POST_WRITE_CONTENT_MISMATCH",
                "error",
                "$.publication.builder_input",
                "The published Builder input does not match the accepted transition output.",
            )
        )
        result = _base_result(intake_result, "invalid", diagnostics, identities=identities, transition_result=transition_result)
        result["publication"] = {
            "builder_input": output_publication,
            "receipt": {"path": str(receipt), "state": "not_published"},
        }
        result["failure_class"] = "publication_failed"
        return result

    post_write_outcome = execute_builder_output_validator(
        repo_root=builder_repo,
        owner_repo=BUILDER_REPO,
        owner_commit=BUILDER_COMMIT,
        validator_path=BUILDER_OUTPUT_VALIDATOR_PATH,
        builder_context_package=published_builder_input,
    )
    diagnostics.extend(item.to_dict() for item in post_write_outcome.diagnostics)
    if post_write_outcome.status != "accepted":
        result = _base_result(
            intake_result,
            normalize_status(post_write_outcome.status),
            diagnostics,
            identities=identities,
            transition_result=transition_result,
            post_write_validator=_outcome_record(post_write_outcome),
        )
        result["publication"] = {
            "builder_input": output_publication,
            "receipt": {"path": str(receipt), "state": "not_published"},
        }
        result["failure_class"] = "owner_tool_failed"
        return result

    staged_receipt: StagedJson | None = None
    try:
        verify_snapshot_unchanged(snapshot)
        lock = load_json_file(lock_path)
        receipt_payload = _build_receipt(
            artifact=artifact,
            snapshot=snapshot,
            identities=identities,
            transition_result=transition_result,
            diagnostics=diagnostics,
            builder_input=published_builder_input,
            output_path=output,
            lock=lock,
            post_write_validator=_outcome_record(post_write_outcome),
        )
        staged_receipt = stage_canonical_json(receipt, receipt_payload)
        receipt_publication = publish_staged_json(staged_receipt)
        staged_receipt = None
    except (PublicationError, SnapshotError, OSError, json.JSONDecodeError) as exc:
        cleanup_diagnostics: list[dict[str, Any]] = []
        try:
            discard_staged_json(staged_receipt)
        except PublicationError as cleanup_exc:
            cleanup_diagnostics.append(_publication_diag(cleanup_exc))
        diagnostics.append(_receipt_failure_diag(exc))
        diagnostics.extend(cleanup_diagnostics)
        result = _base_result(
            intake_result,
            "invalid",
            diagnostics,
            identities=identities,
            transition_result=transition_result,
            post_write_validator=_outcome_record(post_write_outcome),
        )
        result["publication"] = {
            "builder_input": output_publication,
            "receipt": {"path": str(receipt), "state": "not_published"},
        }
        result["failure_class"] = "publication_failed"
        return result

    result = _base_result(
        intake_result,
        "accepted",
        diagnostics,
        identities=identities,
        transition_result=transition_result,
        post_write_validator=_outcome_record(post_write_outcome),
    )
    result.update(
        {
            "handoff_allowed": True,
            "downstream_artifact": {
                "status": "published_verified",
                "schema_id": builder_input.get("schema"),
                "path": str(output),
                "canonical_sha256": canonical_sha256(builder_input),
                "sha256_file_bytes": output_publication["sha256_file_bytes"],
            },
            "receipt": {
                "status": "published_verified",
                "schema_id": RECEIPT_SCHEMA_ID,
                "path": str(receipt),
                "receipt_id": receipt_payload["receipt_id"],
                "canonical_sha256": canonical_sha256(receipt_payload),
                "sha256_file_bytes": receipt_publication["sha256_file_bytes"],
            },
            "publication": {"builder_input": output_publication, "receipt": receipt_publication},
        }
    )
    return result


def _build_receipt(
    *,
    artifact: dict[str, Any],
    snapshot: JsonInputSnapshot,
    identities: dict[str, dict[str, Any]],
    transition_result: dict[str, Any],
    diagnostics: list[dict[str, Any]],
    builder_input: dict[str, Any],
    output_path: Path,
    lock: dict[str, Any],
    post_write_validator: dict[str, Any],
) -> dict[str, Any]:
    final_bundle = artifact["final_stage_bundle"]
    base: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_ID,
        "transition": {"id": TRANSITION_ID, "version": TRANSITION_VERSION},
        "project_gate": {"repository": PG_REPO, "commit": identities["project_gate"].get("commit")},
        "source_export": {
            "path": snapshot.path.name,
            "sha256_file_bytes": snapshot.sha256_file_bytes,
            "export_id": artifact.get("export_id"),
            "producer_repository": (artifact.get("producer") or {}).get("repository"),
            "producer_commit": (artifact.get("producer") or {}).get("commit_sha"),
        },
        "source_bundle": {
            "bundle_id": final_bundle.get("bundle_id"),
            "canonical_sha256": canonical_sha256(final_bundle),
        },
        "owner_checkouts": {name: _stable_identity(value) for name, value in sorted(identities.items())},
        "owner_tools": {
            **dict(transition_result.get("execution_records") or {}),
            "builder_post_write_validator": post_write_validator,
        },
        "external_lock": {
            "schema_version": lock.get("schema_version"),
            "canonicalization": CANONICAL_JSON_VERSION,
            "canonical_sha256": canonical_sha256(lock),
        },
        "transition_status": transition_result.get("status"),
        "handoff_allowed": True,
        "builder_input": {
            "path": _workspace_relative(output_path),
            "schema_id": builder_input.get("schema"),
            "canonical_sha256": canonical_sha256(builder_input),
            "publication_state": "published_verified",
        },
        "diagnostics": sorted(diagnostics, key=lambda item: (item.get("path", "$"), item.get("code", ""))),
        "evidence_classification": "cross_repository_integration",
        "synthetic": bool(final_bundle.get("synthetic")),
        "acquisition_mode": "producer_emitted_gate_artifact",
    }
    base["receipt_id"] = "pg-c2b-receipt-" + canonical_sha256(base)[:24]
    return base


def _base_result(
    intake_result: dict[str, Any],
    status: str,
    diagnostics: list[dict[str, Any]],
    *,
    identities: dict[str, dict[str, Any]] | None = None,
    transition_result: dict[str, Any] | None = None,
    post_write_validator: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = dict(intake_result)
    result["status"] = status
    result["handoff_allowed"] = False
    result["diagnostics"] = sorted(diagnostics, key=lambda item: (item.get("path", "$"), item.get("code", "")))
    result["repository_identities"] = identities or {}
    result["transition_result"] = transition_result
    result["owner_tool_execution"] = {
        **dict((transition_result or {}).get("execution_records") or {}),
        **({"builder_post_write_validator": post_write_validator} if post_write_validator else {}),
    }
    result["producer_validation"] = {
        "status": "passed" if transition_result and transition_result.get("status") == "accepted" else "not_accepted",
        "official_validator_status": "executed" if transition_result else "not_run",
    }
    result["downstream_artifact"] = {"status": "not_published"}
    result["receipt"] = {"status": "not_published"}
    return result


def _stable_identity(identity: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": identity.get("status"),
        "repository": identity.get("repository"),
        "commit": identity.get("commit"),
    }


def _outcome_record(outcome: Any) -> dict[str, Any]:
    record = outcome.execution_record
    return {
        "status": normalize_status(outcome.status),
        "execution": {
            "owner_repository": record.owner_repo,
            "owner_commit": record.owner_commit,
            "validator_path": record.validator_path,
            "exit_code": record.exit_code,
            "timeout_seconds": record.timeout_policy.seconds,
            "stdout_hash": outcome.stdout_hash,
            "stderr_hash": outcome.stderr_hash,
        },
    }


def _workspace_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _receipt_failure_diag(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, SnapshotError):
        return _publication_diag(exc)
    if isinstance(exc, (OSError, json.JSONDecodeError)):
        return _lock_read_diag(exc)
    return _publication_diag(exc)


def _lock_read_diag(exc: Exception) -> dict[str, Any]:
    return _diag(
        "PG_C2B_LOCK_READ_FAILED",
        "error",
        "$.external_lock",
        "The CE→Builder lock file could not be read as valid JSON.",
        error_type=type(exc).__name__,
    )


def _publication_diag(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, PublicationError):
        return _diag(exc.code.replace("PG_A2C", "PG_C2B"), "error", "$", str(exc), **exc.details)
    if isinstance(exc, SnapshotError):
        return _diag(exc.code.replace("PG_A2C", "PG_C2B"), "insufficient_evidence" if exc.status == "insufficient_evidence" else "error", "$", str(exc), **exc.details)
    return _diag("PG_C2B_PUBLICATION_FAILED", "error", "$", "Publication failed.", error_type=type(exc).__name__)


def _diag(code: str, severity: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "path": path,
        "details": details,
        "repair_owner": "Project Gate",
    }
