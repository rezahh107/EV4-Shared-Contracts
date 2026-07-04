#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ev4_transition.architect_to_ce import ARCHITECT_REPO, CE_REPO
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.external_lock import load_lock, verify_external_contract_lock
from ev4_transition.canonical_json import canonical_dumps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", default="contracts/locks/architect-to-ce-transition.v1.lock.json")
    parser.add_argument("--architect-repo", required=True)
    parser.add_argument("--ce-repo", required=True)
    args = parser.parse_args()
    lock = load_lock(args.lock)
    source = LocalCheckoutContractSource({ARCHITECT_REPO: Path(args.architect_repo), CE_REPO: Path(args.ce_repo)})
    diagnostics = verify_external_contract_lock(lock, source)
    payload = {"status": "valid" if not any(d.severity == "error" for d in diagnostics) else "invalid", "diagnostics": [d.to_dict() for d in diagnostics]}
    print(canonical_dumps(payload))
    return 0 if payload["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
