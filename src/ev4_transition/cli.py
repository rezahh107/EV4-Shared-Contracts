from __future__ import annotations

import argparse
from typing import Any

from .bundle_validator import BundleValidator
from .canonical_json import canonical_dumps, write_canonical_json
from .diagnostics import persian_summary
from .transition_engine import TransitionEngine


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ev4-transition")
    parser.add_argument("--schema-root", default="schemas")
    parser.add_argument("--transition-root", default="transitions")
    sub = parser.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("bundle")
    v.add_argument("--transition-id")
    v.add_argument("--format", choices=["json", "persian"], default="json")
    t = sub.add_parser("transition")
    t.add_argument("bundle")
    t.add_argument("--transition-id", required=True)
    t.add_argument("--output")
    t.add_argument("--timestamp")
    t.add_argument("--format", choices=["json", "persian"], default="json")
    i = sub.add_parser("inspect")
    i.add_argument("subject", choices=["transitions"])
    i.add_argument("--format", choices=["json", "persian"], default="json")
    args = parser.parse_args(argv)
    if args.cmd == "validate":
        definition = None
        if args.transition_id:
            definition = TransitionEngine(args.schema_root, args.transition_root).load_transition(args.transition_id)
        result = BundleValidator(args.schema_root).validate_file(args.bundle, definition)
        _emit(result, args.format)
        return 0 if result["status"] == "valid" else 2
    if args.cmd == "transition":
        result = TransitionEngine(args.schema_root, args.transition_root).transition_file(args.bundle, args.transition_id, args.timestamp)
        if args.output and result.get("output") is not None:
            write_canonical_json(args.output, result["output"])
        _emit(result, args.format)
        return 0 if result["status"] == "accepted" else 2
    result = {"transitions": TransitionEngine(args.schema_root, args.transition_root).inspect_transitions()}
    _emit(result, args.format)
    return 0


def _emit(result: dict[str, Any], fmt: str) -> None:
    if fmt == "persian":
        if "status" in result:
            print(persian_summary(result["status"]))
        else:
            print("تعریف‌های انتقال آماده بررسی هستند.")
            for item in result["transitions"]:
                print(f"- {item['transition_id']}: {item['source_stage']} → {item['target_stage']}")
    else:
        print(canonical_dumps(result))


if __name__ == "__main__":
    raise SystemExit(main())
