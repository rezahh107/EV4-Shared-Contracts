from __future__ import annotations

import json
from typing import Any

from .canonical_json import bytes_sha256
from .contract_source import ContractSource
from .diagnostics import Diagnostic, diagnostic, sort_diagnostics
from .kernel_decision_dependencies import (
    EXPECTED_KERNEL_SEMANTIC_DEPENDENCIES,
    KERNEL_ACCEPTED_COMMIT,
    KERNEL_INTAKE_SCHEMA_ID,
    KERNEL_LOCK_SCHEMA_VERSION,
    KERNEL_REPOSITORY,
    REQUIRED_KERNEL_SEMANTIC_ROLES,
)


def verify_kernel_semantic_lock(lock: Any, source: ContractSource) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not isinstance(lock, dict):
        return [diagnostic("PG.KERNEL_INTAKE.LOCK_NOT_OBJECT", "error", "Kernel semantic lock must be an object.", "$")]
    for field, expected in (("schema_version", KERNEL_LOCK_SCHEMA_VERSION), ("intake_schema_id", KERNEL_INTAKE_SCHEMA_ID)):
        if lock.get(field) != expected:
            diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_IDENTITY_MISMATCH", "error", "Kernel semantic lock identity does not match Project Gate configuration.", f"$.{field}", expected=expected, actual=lock.get(field)))
    pin = lock.get("kernel_pin")
    if not isinstance(pin, dict) or pin.get("repository") != KERNEL_REPOSITORY or pin.get("accepted_commit") != KERNEL_ACCEPTED_COMMIT:
        diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_PIN_MISMATCH", "error", "Kernel semantic lock pin does not match Project Gate configuration.", "$.kernel_pin"))
    files = lock.get("files")
    if not isinstance(files, list):
        return sort_diagnostics([*diagnostics, diagnostic("PG.KERNEL_INTAKE.LOCK_FILES_NOT_ARRAY", "error", "Kernel semantic lock files must be an array.", "$.files")])
    seen: set[str] = set()
    for index, item in enumerate(files):
        path = f"$.files[{index}]"
        if not isinstance(item, dict):
            diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_ENTRY_NOT_OBJECT", "error", "Kernel semantic lock entry must be an object.", path))
            continue
        role = item.get("role")
        expected = EXPECTED_KERNEL_SEMANTIC_DEPENDENCIES.get(role) if isinstance(role, str) else None
        if expected is None:
            diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_ROLE_UNEXPECTED", "error", "Kernel semantic lock contains an unexpected role.", f"{path}.role", role=role))
            continue
        if role in seen:
            diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_ROLE_DUPLICATE", "error", "Kernel semantic lock contains a duplicate role.", f"{path}.role", role=role))
            continue
        seen.add(role)
        for field in ("repository", "accepted_commit", "path", "contract_or_schema_id"):
            expected_value = getattr(expected, field)
            if item.get(field) != expected_value:
                diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_ENTRY_MISMATCH", "error", "Kernel semantic lock entry does not match Project Gate-owned dependency configuration.", f"{path}.{field}", role=role, expected=expected_value, actual=item.get(field)))
        try:
            content = source.read_bytes(expected.repository, expected.accepted_commit, expected.path)
        except Exception as exc:
            diagnostics.append(diagnostic("PG.KERNEL_INTAKE.KERNEL_CHECKOUT_UNAVAILABLE", "insufficient_evidence", "Pinned Kernel artifact could not be read.", path, role=role, repository=expected.repository, commit=expected.accepted_commit, file_path=expected.path, error_type=type(exc).__name__))
            continue
        if item.get("sha256_file_bytes") != bytes_sha256(content):
            diagnostics.append(diagnostic("PG.KERNEL_INTAKE.KERNEL_ARTIFACT_HASH_MISMATCH", "error", "Pinned Kernel artifact hash does not match the semantic lock.", path, role=role))
        diagnostics.extend(_identity_diagnostics(content, expected.identity_kind, expected.identity_value, path, role))
    missing = sorted(REQUIRED_KERNEL_SEMANTIC_ROLES - seen)
    if missing:
        diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_ROLE_MISSING", "error", "Kernel semantic lock is missing required roles.", "$.files", missing_roles=missing))
    if len(files) != 6:
        diagnostics.append(diagnostic("PG.KERNEL_INTAKE.LOCK_FILE_COUNT_INVALID", "error", "Kernel semantic lock must contain exactly the six approved semantic dependencies.", "$.files", expected_count=6, actual_count=len(files)))
    return sort_diagnostics(diagnostics)


def _identity_diagnostics(content: bytes, kind: str, value: str, path: str, role: str) -> list[Diagnostic]:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return [diagnostic("PG.KERNEL_INTAKE.KERNEL_ARTIFACT_IDENTITY_MISMATCH", "error", "Pinned Kernel artifact is not UTF-8.", path, role=role)]
    ok = value in text if kind == "text_marker" else False
    if kind == "json_field" and "=" in value:
        field, expected = value.split("=", 1)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        ok = isinstance(parsed, dict) and parsed.get(field) == expected
    return [] if ok else [diagnostic("PG.KERNEL_INTAKE.KERNEL_ARTIFACT_IDENTITY_MISMATCH", "error", "Pinned Kernel artifact identity does not match Project Gate configuration.", path, role=role)]
