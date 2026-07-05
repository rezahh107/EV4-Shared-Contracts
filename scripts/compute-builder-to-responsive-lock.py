#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ev4_transition.canonical_json import bytes_sha256, canonical_dumps
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.transitions.builder_to_responsive import (
    BUILDER_REPO,
    EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES,
    LOCK_SCHEMA_VERSION,
    RESPONSIVE_REPO,
    TRANSITION_ID,
)


def compute_lock(builder_repo: Path, responsive_repo: Path) -> dict:
    source = LocalCheckoutContractSource({BUILDER_REPO: builder_repo, RESPONSIVE_REPO: responsive_repo})
    files = []
    for role in sorted(EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES):
        expected = EXPECTED_BUILDER_TO_RESPONSIVE_DEPENDENCIES[role]
        content = source.read_bytes(expected.repository, expected.accepted_commit, expected.path)
        files.append({
            "role": expected.role,
            "repository": expected.repository,
            "accepted_commit": expected.accepted_commit,
            "path": expected.path,
            "contract_or_schema_id": expected.contract_or_schema_id,
            "sha256_file_bytes": bytes_sha256(content),
        })
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "transition_id": TRANSITION_ID,
        "hash_state": "computed_from_pinned_owner_file_bytes",
        "hash_algorithm": "sha256_file_bytes",
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute the exact Builder→Responsive owner-file lock.")
    parser.add_argument("--builder-repo", required=True)
    parser.add_argument("--responsive-repo", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = compute_lock(Path(args.builder_repo), Path(args.responsive_repo))
    Path(args.output).write_text(canonical_dumps(payload) + "\n", encoding="utf-8")
    print(canonical_dumps({"status": "computed", "output": args.output, "roles": [item["role"] for item in payload["files"]]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
