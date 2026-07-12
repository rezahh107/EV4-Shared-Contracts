#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ev4_transition.canonical_json import bytes_sha256, write_canonical_json
from ev4_transition.kernel_decision_dependencies import (
    EXPECTED_KERNEL_SEMANTIC_DEPENDENCIES,
    KERNEL_ACCEPTED_COMMIT,
    KERNEL_INTAKE_SCHEMA_ID,
    KERNEL_LOCK_SCHEMA_VERSION,
    KERNEL_REPOSITORY,
)


def _resolve_inside(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"Dependency path escapes Kernel checkout: {relative_path}")
    return candidate


def _verify_identity(content: bytes, *, kind: str, value: str, path: str) -> None:
    text = content.decode("utf-8")
    if kind == "text_marker":
        if value not in text:
            raise ValueError(f"Identity marker not found in {path}: {value}")
        return
    if kind != "json_field" or "=" not in value:
        raise ValueError(f"Unsupported identity rule for {path}: {kind} {value}")
    field, expected = value.split("=", 1)
    parsed = json.loads(text)
    if not isinstance(parsed, dict) or parsed.get(field) != expected:
        actual = parsed.get(field) if isinstance(parsed, dict) else type(parsed).__name__
        raise ValueError(f"Identity mismatch for {path}: expected {field}={expected}, observed {actual!r}")


def compute_lock(kernel_root: Path) -> dict:
    root = kernel_root.resolve()
    files: list[dict] = []
    for role in sorted(EXPECTED_KERNEL_SEMANTIC_DEPENDENCIES):
        dependency = EXPECTED_KERNEL_SEMANTIC_DEPENDENCIES[role]
        file_path = _resolve_inside(root, dependency.path)
        content = file_path.read_bytes()
        _verify_identity(
            content,
            kind=dependency.identity_kind,
            value=dependency.identity_value,
            path=dependency.path,
        )
        files.append(
            {
                "role": dependency.role,
                "repository": dependency.repository,
                "accepted_commit": dependency.accepted_commit,
                "path": dependency.path,
                "contract_or_schema_id": dependency.contract_or_schema_id,
                "sha256_file_bytes": bytes_sha256(content),
            }
        )
    return {
        "schema_version": KERNEL_LOCK_SCHEMA_VERSION,
        "intake_schema_id": KERNEL_INTAKE_SCHEMA_ID,
        "kernel_pin": {
            "repository": KERNEL_REPOSITORY,
            "accepted_commit": KERNEL_ACCEPTED_COMMIT,
        },
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute the Project Gate KROAD-011 semantic lock from a pinned Kernel checkout.")
    parser.add_argument("--kernel-repo", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    lock = compute_lock(args.kernel_repo)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_canonical_json(args.output, lock)
    print(args.output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
