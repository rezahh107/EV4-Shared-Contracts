#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ev4_transition.canonical_json import canonical_dumps, load_json_file
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.transitions.ce_to_builder import BUILDER_REPO, CE_REPO, verify_ce_to_builder_lock


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify CE→Builder pinned owner file lock.")
    parser.add_argument("--lock", default="contracts/locks/ce-to-builder-transition.v1.lock.json")
    parser.add_argument("--ce-repo", required=True)
    parser.add_argument("--builder-repo", required=True)
    args = parser.parse_args()
    lock = load_json_file(args.lock)
    source = LocalCheckoutContractSource({CE_REPO: Path(args.ce_repo), BUILDER_REPO: Path(args.builder_repo)})
    diagnostics = verify_ce_to_builder_lock(lock, source)
    status = "valid" if not any(item.severity in {"error", "insufficient_evidence"} for item in diagnostics) else "invalid"
    payload = {"status": status, "diagnostics": [item.to_dict() for item in diagnostics]}
    print(canonical_dumps(payload))
    return 0 if status == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
