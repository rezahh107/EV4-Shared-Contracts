#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from ev4_transition.canonical_json import canonical_dumps, load_json_file, bytes_sha256
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.transitions.ce_to_builder import BUILDER_REPO, CE_REPO, EXPECTED_CE_TO_BUILDER_DEPENDENCIES, LOCK_SCHEMA_VERSION, TRANSITION_ID


def compute_lock(lock: dict[str, Any], ce_repo: Path, builder_repo: Path) -> dict[str, Any]:
    source = LocalCheckoutContractSource({CE_REPO: ce_repo, BUILDER_REPO: builder_repo})
    computed = dict(lock)
    computed["schema_version"] = LOCK_SCHEMA_VERSION
    computed["transition_id"] = TRANSITION_ID
    computed["status"] = "computed_from_pinned_owner_file_bytes"
    computed["hash_algorithm"] = "sha256_file_bytes"
    computed["note"] = "Computed from exact pinned owner checkout file bytes by scripts/compute-ce-to-builder-lock.py."
    files = []
    seen = set()
    for item in lock.get("files", []):
        role = item.get("role") if isinstance(item, dict) else None
        if role not in EXPECTED_CE_TO_BUILDER_DEPENDENCIES:
            raise SystemExit(f"Unexpected CE-to-Builder lock role: {role!r}")
        if role in seen:
            raise SystemExit(f"Duplicate CE-to-Builder lock role: {role}")
        seen.add(role)
        expected = EXPECTED_CE_TO_BUILDER_DEPENDENCIES[role]
        content = source.read_bytes(expected.repository, expected.accepted_commit, expected.path)
        files.append({
            "role": expected.role,
            "repository": expected.repository,
            "accepted_commit": expected.accepted_commit,
            "path": expected.path,
            "contract_or_schema_id": expected.contract_or_schema_id,
            "sha256_file_bytes": bytes_sha256(content),
        })
    missing = sorted(set(EXPECTED_CE_TO_BUILDER_DEPENDENCIES) - seen)
    if missing:
        raise SystemExit(f"Missing CE-to-Builder lock roles: {missing}")
    computed["files"] = files
    return computed


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute exact CE→Builder lock hashes from pinned owner checkouts.")
    parser.add_argument("--lock", default="contracts/locks/ce-to-builder-transition.v1.lock.json")
    parser.add_argument("--ce-repo", required=True)
    parser.add_argument("--builder-repo", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    lock = load_json_file(args.lock)
    computed = compute_lock(lock, Path(args.ce_repo), Path(args.builder_repo))
    Path(args.output).write_text(canonical_dumps(computed) + "\n", encoding="utf-8")
    print(canonical_dumps({"status": "computed", "output": args.output, "roles": [item["role"] for item in computed["files"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
