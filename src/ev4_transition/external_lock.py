from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canonical_json import bytes_sha256, load_json_file
from .contract_source import ContractSource
from .diagnostics import Diagnostic, diagnostic, sort_diagnostics

REQUIRED_ROLES = {
    "architect_payload_schema",
    "architect_payload_validator",
    "architect_valid_fixture",
    "architect_insufficient_fixture",
    "ce_intake_schema",
    "ce_intake_validator",
    "ce_mapping_contract",
    "ce_valid_fixture",
    "ce_insufficient_fixture",
}


def load_lock(path: str | Path) -> dict[str, Any]:
    return load_json_file(path)


def lock_file_hash(lock: dict[str, Any]) -> str:
    from .canonical_json import canonical_sha256
    return canonical_sha256(lock)


def verify_external_contract_lock(lock: dict[str, Any], source: ContractSource) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    files = lock.get("files", []) if isinstance(lock, dict) else []
    seen_roles: set[str] = set()
    for index, item in enumerate(files):
        path = f"$.files[{index}]"
        if not isinstance(item, dict):
            diagnostics.append(diagnostic("PG_A2C_LOCK_ENTRY_NOT_OBJECT", "error", "Lock entry must be an object.", path))
            continue
        role = item.get("role")
        seen_roles.add(role)
        try:
            content = source.read_bytes(item["repository"], item["accepted_commit"], item["path"])
        except Exception as exc:
            diagnostics.append(diagnostic("PG_A2C_EXTERNAL_FILE_READ_FAILED", "error", "Pinned external file could not be read.", path, repository=item.get("repository"), commit=item.get("accepted_commit"), file_path=item.get("path"), role=role, error_type=type(exc).__name__))
            continue
        actual = bytes_sha256(content)
        expected = item.get("sha256_file_bytes")
        if actual != expected:
            diagnostics.append(diagnostic("PG_A2C_EXTERNAL_HASH_MISMATCH", "error", "Pinned external file hash does not match lock manifest.", path, role=role, repository=item.get("repository"), commit=item.get("accepted_commit"), file_path=item.get("path"), expected_sha256=expected, actual_sha256=actual))
        diagnostics.extend(_identity_diagnostics(content, item, path))
    missing = sorted(REQUIRED_ROLES - seen_roles)
    if missing:
        diagnostics.append(diagnostic("PG_A2C_LOCK_ROLE_MISSING", "error", "External lock manifest is missing required roles.", "$.files", missing_roles=missing))
    return sort_diagnostics(diagnostics)


def _identity_diagnostics(content: bytes, item: dict[str, Any], path: str) -> list[Diagnostic]:
    role = item.get("role")
    expected = item.get("contract_or_schema_id")
    diagnostics: list[Diagnostic] = []
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return [diagnostic("PG_A2C_EXTERNAL_FILE_NOT_UTF8", "error", "Pinned external file is not valid UTF-8.", path, role=role)]
    if role in {"architect_payload_schema", "ce_intake_schema"}:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return [diagnostic("PG_A2C_EXTERNAL_JSON_INVALID", "error", "Pinned external JSON file is malformed.", path, role=role)]
        schema_id_const = (((data.get("properties") or {}).get("schema_id") or {}).get("const"))
        if schema_id_const != expected:
            diagnostics.append(diagnostic("PG_A2C_EXTERNAL_SCHEMA_ID_MISMATCH", "error", "Pinned external schema identity does not match lock manifest.", path, role=role, expected_schema_id=expected, actual_schema_id=schema_id_const))
    elif role in {"architect_valid_fixture", "architect_insufficient_fixture", "ce_valid_fixture", "ce_insufficient_fixture"}:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return [diagnostic("PG_A2C_EXTERNAL_JSON_INVALID", "error", "Pinned external JSON fixture is malformed.", path, role=role)]
        actual = data.get("schema_id")
        if actual != expected:
            diagnostics.append(diagnostic("PG_A2C_EXTERNAL_FIXTURE_SCHEMA_ID_MISMATCH", "error", "Pinned external fixture identity does not match lock manifest.", path, role=role, expected_schema_id=expected, actual_schema_id=actual))
    elif role == "ce_mapping_contract":
        if expected not in text:
            diagnostics.append(diagnostic("PG_A2C_EXTERNAL_MAPPING_ID_MISMATCH", "error", "Pinned CE mapping contract identity was not found.", path, role=role, expected_contract_id=expected))
    elif role in {"architect_payload_validator", "ce_intake_validator"}:
        if "--format" not in text or "json" not in text:
            diagnostics.append(diagnostic("PG_A2C_EXTERNAL_VALIDATOR_MODE_UNCONFIRMED", "warning", "Pinned validator does not visibly expose JSON format support.", path, role=role))
    return diagnostics
