from __future__ import annotations

import argparse
from typing import Any

from .bundle_validator import BundleValidator
from .canonical_json import canonical_dumps
from .diagnostics import persian_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ev4-transition")
    parser.add_argument("--schema-root", default="schemas")

    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate", help="Validate a Stage Evidence Bundle.")
    validate_parser.add_argument("bundle")
    validate_parser.add_argument("--require-evidence", action="append", default=[])
    validate_parser.add_argument("--format", choices=["json", "persian"], default="json")

    inspect_parser = sub.add_parser("inspect", help="Inspect deterministic core metadata.")
    inspect_parser.add_argument("--format", choices=["json", "persian"], default="json")

    args = parser.parse_args(argv)

    if args.command == "validate":
        validator = BundleValidator(args.schema_root)
        result = validator.validate_file(args.bundle, required_evidence_ids=args.require_evidence)
        _emit(result, args.format)
        if result["status"] == "valid":
            return 0
        if result["status"] == "insufficient_evidence":
            return 2
        return 1

    info = {
        "package": "ev4-project-gate",
        "implemented": [
            "canonical_json",
            "sha256",
            "structured_diagnostics",
            "stage_bundle_validation",
            "transition_result_schema_foundation",
            "minimal_cli"
        ],
        "not_implemented": [
            "architect-to-ce transition",
            "ce-to-builder transition",
            "builder-to-responsive transition",
            "real EV4 artifact validation",
            "UI"
        ]
    }
    _emit(info, args.format)
    return 0


def _emit(payload: dict[str, Any], fmt: str) -> None:
    if fmt == "persian":
        if "status" in payload:
            print(persian_summary(payload["status"]))
        else:
            print("هسته قطعی پایتون آماده است؛ انتقال‌های واقعی EV4 هنوز پیاده‌سازی نشده‌اند.")
        return
    print(canonical_dumps(payload))


if __name__ == "__main__":
    raise SystemExit(main())
