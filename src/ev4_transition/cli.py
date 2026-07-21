from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .behavioral_coverage import CoverageSourceError, inspect_coverage_source, validate_coverage_source
from .bundle_validator import BundleValidator
from .canonical_json import canonical_dumps, load_json_file
from .io.secure_snapshot import capture_json_snapshot
from .presentation.status_mapping import exit_code_for_status
from .reports import render_plain_summary
from .service import GateRequest, RepoPaths, run_gate_request

_CAPABILITY_STATUS_PATH = Path(__file__).resolve().parent / "data" / "capability-status.v1.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ev4-transition")
    parser.add_argument("--schema-root", default="schemas")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate", help="Validate a Stage Evidence Bundle.")
    validate_parser.add_argument("bundle")
    validate_parser.add_argument("--require-evidence", action="append", default=[])
    validate_parser.add_argument("--format", choices=["json", "persian"], default="json")

    transition_parser = sub.add_parser("transition", help="Run a deterministic Project Gate transition.")
    transition_parser.add_argument("transition_name", choices=["architect-to-ce", "ce-to-builder", "builder-to-responsive", "final-evidence-gate"])
    transition_parser.add_argument("bundle")
    transition_parser.add_argument("--architect-repo")
    transition_parser.add_argument("--ce-repo")
    transition_parser.add_argument("--builder-repo")
    transition_parser.add_argument("--responsive-repo")
    transition_parser.add_argument("--project-gate-repo")
    transition_parser.add_argument("--kernel-repo")
    transition_parser.add_argument("--lock")
    transition_parser.add_argument("--output")
    transition_parser.add_argument("--receipt-output")
    transition_parser.add_argument("--format", choices=["json", "persian"], default="json")
    transition_parser.add_argument("--acquisition-mode", choices=["pinned_owner_file_computation", "producer_emitted_gate_artifact"], default="pinned_owner_file_computation")

    coverage_parser = sub.add_parser("coverage", help="Inspect or validate Behavioral Rule Coverage.")
    coverage_sub = coverage_parser.add_subparsers(dest="coverage_command", required=True)
    coverage_inspect = coverage_sub.add_parser("inspect", help="Inspect behavioral coverage without running a transition.")
    coverage_inspect.add_argument("source", nargs="?", default="docs/BEHAVIORAL_RULE_COVERAGE.md")
    coverage_inspect.add_argument("--schema", default="schemas/behavioral-coverage/behavioral-coverage.v1.schema.json")
    coverage_validate = coverage_sub.add_parser("validate", help="Validate behavioral coverage thresholds.")
    coverage_validate.add_argument("source", nargs="?", default="docs/BEHAVIORAL_RULE_COVERAGE.md")
    coverage_validate.add_argument("--schema", default="schemas/behavioral-coverage/behavioral-coverage.v1.schema.json")

    inspect_parser = sub.add_parser("inspect", help="Inspect deterministic core metadata and layered capability truth.")
    inspect_parser.add_argument("--format", choices=["json", "persian"], default="json")

    args = parser.parse_args(argv)
    if args.command == "validate":
        validator = BundleValidator(args.schema_root)
        result = validator.validate_file(args.bundle, required_evidence_ids=args.require_evidence)
        _emit(result, args.format)
        return _exit_for_status(result["status"])

    if args.command == "transition":
        preflight_failure = _transition_preflight(args)
        if preflight_failure is not None:
            _emit(preflight_failure, args.format)
            return _exit_for_status(preflight_failure["status"])

        snapshot = None
        if args.acquisition_mode == "producer_emitted_gate_artifact":
            try:
                snapshot = capture_json_snapshot(args.bundle)
            except Exception as exc:
                payload = _simple_invalid(
                    "CLI_PRODUCER_SOURCE_CAPTURE_FAILED",
                    "The original producer source file could not be captured immutably.",
                    error_type=type(exc).__name__,
                    error=str(exc),
                )
                _emit(payload, args.format)
                return _exit_for_status(payload["status"])

        request = GateRequest(
            transition_choice=_service_choice(args.transition_name),  # type: ignore[arg-type]
            input_json_path=args.bundle,
            input_snapshot=snapshot,
            repo_paths=RepoPaths(
                project_gate_repo_path=args.project_gate_repo or ".",
                architect_repo_path=args.architect_repo,
                ce_repo_path=args.ce_repo,
                builder_repo_path=args.builder_repo,
                responsive_repo_path=args.responsive_repo,
            ),
            acquisition_mode=args.acquisition_mode,
            schema_root=args.schema_root,
            lock_path=args.lock,
            output_path=args.output,
            receipt_path=args.receipt_output,
        )
        response = run_gate_request(request)
        payload = _cli_payload(response.to_dict())
        _emit(payload, args.format)
        return _exit_for_status(str(payload.get("status", "invalid")))

    if args.command == "coverage":
        return _coverage_command(args)

    info = _load_capability_status()
    _emit(info, args.format)
    return 0


def _service_choice(transition_name: str) -> str:
    return {
        "architect-to-ce": "architect_to_ce",
        "ce-to-builder": "ce_to_builder",
        "builder-to-responsive": "builder_to_responsive",
        "final-evidence-gate": "final_gate",
    }[transition_name]


def _cli_payload(response: dict[str, Any]) -> dict[str, Any]:
    engine = response.get("engine_result")
    if isinstance(engine, dict):
        payload = dict(engine)
        if response.get("service_diagnostics"):
            existing = list(payload.get("diagnostics") or [])
            payload["diagnostics"] = existing + list(response["service_diagnostics"])
        return payload
    return {
        "schema_version": "project-gate-service-result.v1",
        "result_type": "service_layer_failure",
        "status": response.get("status", "invalid"),
        "transition_choice": response.get("transition_choice"),
        "diagnostics": list(response.get("service_diagnostics") or []),
        "handoff_allowed": False,
        "output": None,
    }


def _service_choice(transition_name: str) -> str:
    return {
        "architect-to-ce": "architect_to_ce",
        "ce-to-builder": "ce_to_builder",
        "builder-to-responsive": "builder_to_responsive",
        "final-evidence-gate": "final_gate",
    }[transition_name]


def _default_lock_for_transition(transition_name: str) -> str:
    return {
        "architect-to-ce": "contracts/locks/architect-to-ce-transition.v1.lock.json",
        "ce-to-builder": "contracts/locks/ce-to-builder-transition.v1.lock.json",
        "builder-to-responsive": "contracts/locks/builder-to-responsive-transition.v1.lock.json",
        "final-evidence-gate": "contracts/locks/final-gate.v1.lock.json",
    }[transition_name]


def _transition_preflight(args: argparse.Namespace) -> dict[str, Any] | None:
    required_by_transition = {
        "architect-to-ce": ["architect_repo", "ce_repo"],
        "ce-to-builder": ["ce_repo", "builder_repo"],
        "builder-to-responsive": ["builder_repo", "responsive_repo"],
        "final-evidence-gate": ["project_gate_repo", "responsive_repo", "kernel_repo"],
    }
    for field in required_by_transition.get(args.transition_name, []):
        value = getattr(args, field, None)
        if isinstance(value, str):
            value = value.strip()
            setattr(args, field, value)
        option = "--" + field.replace("_", "-")
        if not value:
            return _simple_insufficient("CLI_LOCAL_PATH_REQUIRED", "A local checkout path is required for this guarded transition.", option=option, transition_name=args.transition_name)
        if _looks_like_url(value):
            return _simple_insufficient("CLI_GITHUB_URL_REJECTED", "GitHub URLs are rejected; provide a local checkout path.", option=option, transition_name=args.transition_name)
        if not Path(value).is_dir():
            return _simple_insufficient("CLI_LOCAL_PATH_NOT_FOUND", "Local checkout path was not found.", option=option, path=value, transition_name=args.transition_name)
    return None


def _looks_like_url(value: str) -> bool:
    lowered = value.lower()
    return lowered.startswith(("http://", "https://", "git@")) or "github.com" in lowered


def _simple_insufficient(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"status": "insufficient_evidence", "diagnostics": [{"code": code, "severity": "insufficient_evidence", "message": message, "path": "$", "details": details}]}


def _load_capability_status() -> dict[str, Any]:
    payload = load_json_file(_CAPABILITY_STATUS_PATH)
    capabilities = payload.get("capabilities")
    ce_to_builder = capabilities.get("ce_to_builder") if isinstance(capabilities, dict) else None
    expected = {
        "orchestration_baseline": "implemented",
        "cli_exposure": "guarded",
        "owner_fixture_integration": "verified",
        "real_non_synthetic_handoff": "insufficient_evidence",
    }
    if payload.get("schema_version") != "ev4-project-gate-capability-status.v1" or ce_to_builder != expected:
        raise ValueError("packaged capability truth is invalid")
    for guarded_name in ["ce-to-builder", "builder-to-responsive", "final-evidence-gate"]:
        if guarded_name not in payload.get("public_cli_transitions", []):
            raise ValueError(f"{guarded_name} guarded CLI exposure is not recorded")
    return payload


def _coverage_command(args: argparse.Namespace) -> int:
    try:
        if args.coverage_command == "inspect":
            report = inspect_coverage_source(args.source, args.schema)
            print(canonical_dumps(report.to_dict()))
            return 0
        if args.coverage_command == "validate":
            report = validate_coverage_source(args.source, args.schema)
            print(canonical_dumps(report.to_dict()))
            return 0 if report.status == "thresholds_met" else 1
    except CoverageSourceError as exc:
        payload = {
            "schema_version": "behavioral-coverage-report.v1",
            "source": getattr(args, "source", None),
            "status": "source_unparseable",
            "rule_count": 0,
            "diagnostics": [{"code": "PG_BRC_SOURCE_UNPARSEABLE", "severity": "error", "message": str(exc), "path": "$"}],
        }
        print(canonical_dumps(payload))
        return 2
    raise AssertionError(f"unknown coverage command: {args.coverage_command}")


def _simple_invalid(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"status": "invalid", "diagnostics": [{"code": code, "severity": "error", "message": message, "path": "$", "details": details}]}


def _exit_for_status(status: str) -> int:
    return exit_code_for_status(status)


def _emit(payload: dict[str, Any], fmt: str) -> None:
    if fmt == "persian":
        if "status" in payload:
            print(render_plain_summary(payload), end="")
        else:
            print("هسته قطعی و گذارهای guarded از service مشترک استفاده می‌کنند.")
        return
    print(canonical_dumps(payload))


if __name__ == "__main__":
    raise SystemExit(main())
