#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ev4_transition.behavioral_coverage import CoverageSourceError, validate_coverage_source
from ev4_transition.canonical_json import canonical_dumps


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate EV4 Project Gate behavioral rule coverage.")
    parser.add_argument("source", nargs="?", default="docs/BEHAVIORAL_RULE_COVERAGE.md")
    parser.add_argument("--schema", default="schemas/behavioral-coverage/behavioral-coverage.v1.schema.json")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args(argv)

    try:
        report = validate_coverage_source(Path(args.source), Path(args.schema))
    except CoverageSourceError as exc:
        payload = {
            "schema_version": "behavioral-coverage-report.v1",
            "source": args.source,
            "status": "source_unparseable",
            "rule_count": 0,
            "diagnostics": [
                {"code": "PG_BRC_SOURCE_UNPARSEABLE", "severity": "error", "message": str(exc), "path": "$"}
            ],
        }
        _emit(payload, args.format)
        return 2

    payload = report.to_dict()
    _emit(payload, args.format)
    return 0 if report.status == "thresholds_met" else 1


def _emit(payload: dict, fmt: str) -> None:
    if fmt == "json":
        print(canonical_dumps(payload))
        return
    print(f"status: {payload['status']}")
    print(f"rule_count: {payload['rule_count']}")
    for diagnostic in payload["diagnostics"]:
        print(f"{diagnostic['code']} {diagnostic['path']}: {diagnostic['message']}")


if __name__ == "__main__":
    raise SystemExit(main())
