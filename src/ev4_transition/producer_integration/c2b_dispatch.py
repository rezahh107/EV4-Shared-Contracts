from __future__ import annotations

from pathlib import Path
from typing import Any

from ev4_transition.bundle_validator import ResultValidationError
from ev4_transition.canonical_json import CANONICAL_JSON_VERSION, canonical_sha256, load_json_file
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.io.safe_publication import (
    PublicationError,
    StagedJson,
    discard_staged_json,
    publish_staged_json,
    resolve_publication_paths,
    stage_canonical_json,
)
from ev4_transition.io.secure_snapshot import (
    JsonInputSnapshot,
    SnapshotError,
    capture_json_snapshot,
    verify_snapshot_unchanged,
)
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
    CeToBuilderTransitionConfig,
    transition_ce_to_builder,
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
        lock_snapshot = capture_json_snapshot(lock_path)
    except SnapshotError as exc:
        return _base_result(
            intake_result,
            "invalid",
            [_lock_read_diag(exc)],
            identities=identities,
        )

    try:
        transition_result = _transition_from_lock_snapshot(
            final_bundle,
            schema_root=schema_root,
            lock=lock_snapshot.value,
            ce_repo=ce_repo,
            builder_repo=builder_repo,
        )
    except ResultValidationError as exc:
        return _base_result(
            intake_result,
            "invalid",
            [_diag("TRANSITION_RESULT_SCHEMA_VALIDATION_FAILED", "error", "$", "The CE→Builder transition result failed its Project Gate schema.", error=str(exc))],
            identities=identities,
        )

    lock_identity_diagnostic = _transition_lock_identity_diagnostic(transition_result, lock_snapshot.value)
    if lock_identity_diagnostic is not None:
        result = _base_result(
            intake_result,
            "invalid",
            list(transition_result.get("diagnostics") or []) + [lock_identity_diagnostic],
            identities=identities,
            transition_result=transition_result,
        )
        result["failure_class"] = "lock_verification_failed"
        return result

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
    post_write_record = _outcome_record(post_write_outcome)
    if post_write_outcome.status != "accepted":
        result = _base_result(
            intake_result,
            normalize_status(post_write_outcome.status),
            diagnostics,
            identities=identities,
            transition_result=transition_result,
            post_write_validator=post_write_record,
        )
        result["publication"] = {
            "builder_input": output_publication,
            "receipt": {"path": str(receipt), "state": "not_published"},
        }
        result["failure_class"] = "owner_tool_failed"
        return result

    staged_receipt: StagedJson | None = None
    try:
        receipt_payload = _build_receipt(
            artifact=artifact,
            snapshot=snapshot,
            identities=identities,
            transition_result=transition_result,
            diagnostics=diagnostics,
            builder_input=published_builder_input,
            output_path=output,
            lock=lock_snapshot.value,
            post_write_validator=post_write_record,
        )
        staged_receipt = stage_canonical_json(receipt, receipt_payload)
        verify_snapshot_unchanged(snapshot)
        try:
            verify_snapshot_unchanged(lock_snapshot)
        except SnapshotError as exc:
            raise _LockMutationError(exc) from exc
        lock_identity_diagnostic = _transition_lock_identity_diagnostic(transition_result, lock_snapshot.value)
        if lock_identity_diagnostic is not None:
            raise _LockIdentityError(lock_identity_diagnostic)
        receipt_publication = publish_staged_json(staged_receipt)
        staged_receipt = None
    except (PublicationError, SnapshotError, _LockIdentityError, _LockMutationError) as exc:
        cleanup_diagnostics: list[dict[str, Any]] = []
        try:
            discard_staged_json(staged_receipt)
        except PublicationError as cleanup_exc:
            cleanup_diagnostics.append(_publication_diag(cleanup_exc))
        diagnostics.append(_receipt_failure_diag(exc, lock_snapshot=lock_snapshot))
        diagnostics.extend(cleanup_diagnostics)
        result = _base_result(
            intake_result,
            "invalid",
            diagnostics,
            identities=identities,
            transition_result=transition_result,
            post_write_validator=post_write_record,
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
        post_write_validator=post_write_record,
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


def _transition_from_lock_snapshot(
    final_bundle: dict[str, Any],
    *,
    schema_root: str | Path,
    lock: dict[str, Any],
    ce_repo: str | Path,
    builder_repo: str | Path,
) -> dict[str, Any]:
    config = CeToBuilderTransitionConfig(
        Path(schema_root),
        lock,
        Path(ce_repo),
        Path(builder_repo),
        30,
        True,
    )
    source = LocalCheckoutContractSource({CE_REPO: Path(ce_repo), BUILDER_REPO: Path(builder_repo)})
    return transition_ce_to_builder(final_bundle, source, config)


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
    lock_hash = _transition_lock_hash(transition_result)
    if not isinstance(lock_hash, str):
        raise _LockIdentityError(_lock_identity_diag(None, canonical_sha256(lock)))
    owner_tools = _stable_owner_tools(transition_result.get("execution_records"), post_write_validator)
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
        "owner_tools": owner_tools,
        "external_lock": {
            "schema_version": lock.get("schema_version"),
            "canonicalization": CANONICAL_JSON_VERSION,
            "canonical_sha256": lock_hash,
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


def _stable_owner_tools(records: Any, post_write_validator: dict[str, Any]) -> dict[str, Any]:
    stable: dict[str, Any] = {}
    if isinstance(records, dict):
        for name, record in sorted(records.items()):
            if isinstance(record, dict):
                stable[name] = _stable_execution_projection(record)
    stable["builder_post_write_validator"] = post_write_validator
    return stable


def _stable_execution_projection(record: dict[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("execution"), dict):
        projected = _stable_execution_projection(record["execution"])
        if record.get("status") is not None:
            projected = {"status": record.get("status"), "execution": projected}
        return projected

    tool_path = record.get("validator_path") or record.get("adapter_path") or record.get("entrypoint")
    timeout = record.get("timeout_policy")
    stable_timeout: dict[str, Any] | None = None
    if isinstance(timeout, dict):
        stable_timeout = {
            key: timeout.get(key)
            for key in ("seconds", "kill_process_tree")
            if timeout.get(key) is not None
        }
    elif record.get("timeout_seconds") is not None:
        stable_timeout = {"seconds": record.get("timeout_seconds")}

    projected: dict[str, Any] = {}
    values = {
        "status": record.get("status"),
        "tool_kind": record.get("tool_kind"),
        "owner_repository": record.get("owner_repository") or record.get("owner_repo"),
        "owner_commit": record.get("owner_commit"),
        "entrypoint": tool_path,
        "input_ref": record.get("input_ref"),
        "input_hash": record.get("input_hash"),
        "output_ref": record.get("output_ref"),
        "output_hash": record.get("output_hash"),
        "parsed_result_ref": record.get("parsed_result_ref"),
        "validator_after_adapter_ref": record.get("validator_after_adapter_ref"),
        "exit_code": record.get("exit_code"),
        "timeout_policy": stable_timeout,
        "stdout_hash": record.get("stdout_hash"),
        "stderr_hash": record.get("stderr_hash"),
        "failure_code": record.get("failure_code"),
    }
    for key, value in values.items():
        if value is not None:
            projected[key] = value
    projected["evidence_hash"] = canonical_sha256(projected)
    return projected


def _outcome_record(outcome: Any) -> dict[str, Any]:
    record = outcome.execution_record
    raw = {
        "tool_kind": getattr(record, "tool_kind", None),
        "owner_repo": getattr(record, "owner_repo", None),
        "owner_commit": getattr(record, "owner_commit", None),
        "validator_path": getattr(record, "validator_path", None),
        "adapter_path": getattr(record, "adapter_path", None),
        "input_ref": getattr(record, "input_ref", None),
        "input_hash": getattr(record, "input_hash", None),
        "output_ref": getattr(record, "output_ref", None),
        "output_hash": getattr(record, "output_hash", None),
        "parsed_result_ref": getattr(record, "parsed_result_ref", None),
        "validator_after_adapter_ref": getattr(record, "validator_after_adapter_ref", None),
        "exit_code": getattr(record, "exit_code", None),
        "timeout_seconds": getattr(getattr(record, "timeout_policy", None), "seconds", None),
        "stdout_hash": outcome.stdout_hash,
        "stderr_hash": outcome.stderr_hash,
        "failure_code": getattr(record, "failure_code", None),
    }
    return {
        "status": normalize_status(outcome.status),
        "execution": _stable_execution_projection(raw),
    }


def _workspace_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _transition_lock_hash(transition_result: dict[str, Any]) -> Any:
    hashes = transition_result.get("hashes")
    if not isinstance(hashes, dict):
        return None
    lock_hash = hashes.get("external_contract_lock")
    if not isinstance(lock_hash, dict):
        return None
    return lock_hash.get("value")


def _transition_lock_identity_diagnostic(transition_result: dict[str, Any], lock: dict[str, Any]) -> dict[str, Any] | None:
    expected = canonical_sha256(lock)
    actual = _transition_lock_hash(transition_result)
    if actual == expected:
        return None
    return _lock_identity_diag(actual, expected)


def _lock_identity_diag(actual: Any, expected: str) -> dict[str, Any]:
    return _diag(
        "PG_C2B_LOCK_IDENTITY_MISMATCH",
        "error",
        "$.external_lock",
        "The transition result is not bound to the captured CE→Builder lock identity.",
        transition_lock_hash=actual,
        captured_lock_hash=expected,
    )


def _receipt_failure_diag(exc: Exception, *, lock_snapshot: JsonInputSnapshot) -> dict[str, Any]:
    del lock_snapshot
    if isinstance(exc, _LockIdentityError):
        return exc.diagnostic
    if isinstance(exc, _LockMutationError):
        return _lock_mutation_diag(exc.cause)
    if isinstance(exc, SnapshotError):
        return _publication_diag(exc)
    return _publication_diag(exc)


def _lock_read_diag(exc: Exception) -> dict[str, Any]:
    return _diag(
        "PG_C2B_LOCK_READ_FAILED",
        "error",
        "$.external_lock",
        "The CE→Builder lock file could not be captured as immutable strict JSON.",
        error_type=type(exc).__name__,
        source_code=getattr(exc, "code", None),
    )


def _lock_mutation_diag(exc: Exception) -> dict[str, Any]:
    return _diag(
        "PG_C2B_LOCK_MUTATED_BEFORE_RECEIPT",
        "error",
        "$.external_lock",
        "The CE→Builder lock changed after transition authorization and before receipt publication.",
        error_type=type(exc).__name__,
        source_code=getattr(exc, "code", None),
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


class _LockIdentityError(RuntimeError):
    def __init__(self, diagnostic: dict[str, Any]) -> None:
        self.diagnostic = diagnostic
        super().__init__(diagnostic["message"])


class _LockMutationError(RuntimeError):
    def __init__(self, cause: SnapshotError) -> None:
        self.cause = cause
        super().__init__(str(cause))
