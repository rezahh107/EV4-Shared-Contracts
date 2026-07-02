from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .canonical_json import load_json_file
from .diagnostics import Diagnostic, aggregate_status, diagnostic


class BundleValidator:
    def __init__(self, schema_root: str | Path = "schemas") -> None:
        self.schema_root = Path(schema_root)
        schema = load_json_file(self.schema_root / "stage-bundle" / "stage-bundle.v1.schema.json")
        self.validator = Draft202012Validator(schema)

    def validate_bundle(self, bundle: dict[str, Any], transition_definition: dict[str, Any] | None = None) -> dict[str, Any]:
        diagnostics: list[Diagnostic] = []
        for err in sorted(self.validator.iter_errors(bundle), key=lambda e: list(e.path)):
            diagnostics.append(diagnostic("error", "SCHEMA_VALIDATION_FAILED", err.message, _path(list(err.path))))
        if diagnostics:
            return _result(diagnostics)
        if bundle.get("evidence_status") == "insufficient_evidence" or bundle.get("missing_evidence"):
            diagnostics.append(diagnostic("insufficient_evidence", "BUNDLE_INSUFFICIENT_EVIDENCE", "The bundle does not contain enough evidence for a safe transition.", "$.evidence_status", missing_evidence=bundle.get("missing_evidence", [])))
        if transition_definition:
            expected = transition_definition["source_stage"]
            if bundle["stage"] != expected:
                diagnostics.append(diagnostic("error", "UNSUPPORTED_SOURCE_STAGE", f"Transition expects {expected}, got {bundle['stage']}.", "$.stage", expected=expected, actual=bundle["stage"]))
            ids = {item["id"] for item in bundle.get("evidence", [])}
            missing = [item for item in transition_definition.get("required_evidence_ids", []) if item not in ids]
            if missing:
                diagnostics.append(diagnostic("insufficient_evidence", "TRANSITION_REQUIRED_EVIDENCE_MISSING", "Required transition evidence is missing.", "$.evidence", missing_evidence=missing))
        return _result(diagnostics)

    def validate_file(self, path: str | Path, transition_definition: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.validate_bundle(load_json_file(path), transition_definition)


def _path(parts: list[Any]) -> str:
    out = "$"
    for part in parts:
        out += f"[{part}]" if isinstance(part, int) else f".{part}"
    return out


def _result(items: list[Diagnostic]) -> dict[str, Any]:
    return {"status": aggregate_status(items), "diagnostics": [item.to_dict() for item in items]}
