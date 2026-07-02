from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .bundle_validator import BundleValidator
from .canonical_json import canonical_hash, load_json_file
from .diagnostics import diagnostic
from .provenance import transition_provenance


class TransitionEngine:
    def __init__(self, schema_root: str | Path = "schemas", transition_root: str | Path = "transitions") -> None:
        self.schema_root = Path(schema_root)
        self.transition_root = Path(transition_root)
        self.bundle_validator = BundleValidator(schema_root)
        self.target_validator = Draft202012Validator(load_json_file(self.schema_root / "target-inputs" / "target-input.v1.schema.json"))
        self.result_validator = Draft202012Validator(load_json_file(self.schema_root / "transition-result" / "transition-result.v1.schema.json"))

    def load_transition(self, transition_id: str) -> dict[str, Any]:
        matches = sorted(self.transition_root.glob(f"{transition_id}.json"))
        if len(matches) != 1:
            raise TransitionError(f"Expected exactly one transition definition for {transition_id!r}.")
        data = load_json_file(matches[0])
        if data.get("transition_id") != transition_id:
            raise TransitionError("Transition file id does not match requested id.")
        return data

    def inspect_transitions(self) -> list[dict[str, Any]]:
        rows = []
        for path in sorted(self.transition_root.glob("*.json")):
            data = load_json_file(path)
            rows.append({"transition_id": data["transition_id"], "version": data["version"], "source_stage": data["source_stage"], "target_stage": data["target_stage"], "path": str(path)})
        return rows

    def transition(self, bundle: dict[str, Any], transition_id: str, timestamp: str | None = None) -> dict[str, Any]:
        try:
            definition = self.load_transition(transition_id)
        except TransitionError as exc:
            return _failed(bundle, transition_id, [diagnostic("error", "TRANSITION_DEFINITION_NOT_FOUND", str(exc)).to_dict()])
        validation = self.bundle_validator.validate_bundle(bundle, definition)
        if validation["status"] == "invalid":
            return _failed(bundle, transition_id, validation["diagnostics"])
        if validation["status"] == "insufficient_evidence":
            return {"schema_version": "transition-result.v1", "status": "insufficient_evidence", "transition_id": transition_id, "source_stage": bundle.get("stage"), "target_stage": definition.get("target_stage"), "diagnostics": validation["diagnostics"], "source_hash": canonical_hash(bundle), "output_hash": None, "output": None}
        try:
            target = self._map(bundle, definition)
        except TransitionError as exc:
            return _failed(bundle, transition_id, [diagnostic("error", "TRANSITION_MAPPING_FAILED", str(exc)).to_dict()])
        package = {"schema_version": "target-input.v1", "package_id": f"{bundle['bundle_id']}::{transition_id}", "target_stage": definition["target_stage"], "source": {"bundle_id": bundle["bundle_id"], "stage": bundle["stage"], "source_hash": canonical_hash(bundle)}, "transition": {"id": transition_id, "version": definition["version"]}, "target": target, "evidence": deepcopy(bundle.get("evidence", []))}
        package["provenance"] = transition_provenance(bundle, definition, package, timestamp)
        errors = [diagnostic("error", "TARGET_INPUT_SCHEMA_FAILED", e.message).to_dict() for e in self.target_validator.iter_errors(package)]
        if errors:
            return _failed(bundle, transition_id, errors)
        return {"schema_version": "transition-result.v1", "status": "accepted", "transition_id": transition_id, "source_stage": bundle["stage"], "target_stage": definition["target_stage"], "diagnostics": [], "source_hash": canonical_hash(bundle), "output_hash": canonical_hash(package), "output": package}

    def transition_file(self, path: str | Path, transition_id: str, timestamp: str | None = None) -> dict[str, Any]:
        return self.transition(load_json_file(path), transition_id, timestamp)

    def _map(self, bundle: dict[str, Any], definition: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for rule in definition.get("field_mappings", []):
            value = _get(bundle, rule["from"])
            _set(out, rule["to"], deepcopy(value))
        return out


class TransitionError(RuntimeError):
    pass


def _failed(bundle: dict[str, Any], transition_id: str, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    return {"schema_version": "transition-result.v1", "status": "failed", "transition_id": transition_id, "source_stage": bundle.get("stage"), "target_stage": None, "diagnostics": diagnostics, "source_hash": canonical_hash(bundle), "output_hash": None, "output": None}


def _parts(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise TransitionError(f"Only absolute JSON Pointers are supported: {pointer}")
    return [p.replace("~1", "/").replace("~0", "~") for p in pointer.split("/")[1:]]


def _get(value: Any, pointer: str) -> Any:
    cur = value
    for part in _parts(pointer):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise TransitionError(f"Required source path missing: {pointer}")
    return cur


def _set(target: dict[str, Any], pointer: str, value: Any) -> None:
    cur = target
    parts = _parts(pointer)
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value
