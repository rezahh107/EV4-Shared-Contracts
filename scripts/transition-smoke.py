#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from ev4_transition.canonical_json import canonical_dumps


def source_bundle(payload: dict) -> dict:
    status = "insufficient_evidence" if payload["payload_status"] == "insufficient_evidence" else "complete"
    bundle = {
        "schema_version": "stage-evidence-bundle.v1",
        "bundle_id": "synthetic-architect-a2c-smoke",
        "stage": "architect",
        "payload_schema": {"id": "ev4-architect-stage-payload@1.0.0", "version": "1.0.0", "owner_repository": "rezahh107/EV4-Architect-Repo"},
        "produced_by": {"repository": "rezahh107/EV4-Architect-Repo", "ref": "synthetic-fixture", "commit_sha": "b0651668b97f682bb17f66840c8e8c503fd3935d"},
        "evidence_status": status,
        "payload": {"schema_id": "ev4-architect-stage-payload@1.0.0", "data": payload},
        "evidence": [{"id": "architect-payload", "kind": "fixture", "state": "validated", "description": "Synthetic Architect payload fixture.", "artifact_hash": {"algorithm": "sha256", "value": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef", "scope": "canonical_json"}, "source": {"type": "synthetic_fixture", "reference": "Architect pinned fixture"}}],
        "provenance": {"source": "synthetic-fixture", "created_by": "project-gate-smoke"},
        "synthetic": True,
    }
    if status == "insufficient_evidence":
        bundle["missing_evidence"] = [{"id": item["unresolved_id"], "owner": item["owner"], "reason": item["reason"]} for item in payload.get("unresolved_evidence", [])]
    return bundle


def run_cli(bundle_path: Path, architect_repo: str, ce_repo: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([
        sys.executable, "-m", "ev4_transition.cli", "transition", "architect-to-ce", str(bundle_path),
        "--architect-repo", architect_repo,
        "--ce-repo", ce_repo,
        "--format", "json",
    ], text=True, capture_output=True, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--architect-repo", required=True)
    parser.add_argument("--ce-repo", required=True)
    args = parser.parse_args()
    payload = json.loads((Path(args.architect_repo) / "fixtures/architect-stage-payload/valid/minimal-complete.v1.json").read_text(encoding="utf-8"))
    path = Path(".a2c-smoke-bundle.json")
    path.write_text(canonical_dumps(source_bundle(payload)) + "\n", encoding="utf-8")
    completed = run_cli(path, args.architect_repo, args.ce_repo)
    print(completed.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    if completed.returncode != 0:
        return completed.returncode
    result = json.loads(completed.stdout)
    if result["status"] != "valid":
        return 1
    if result["output"]["stage"] != "ce":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
