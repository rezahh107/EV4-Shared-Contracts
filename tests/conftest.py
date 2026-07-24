from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from ev4_transition.evidence_truth import RUNTIME_EVIDENCE_RECEIPT_SCHEMA
from ev4_transition.transitions.builder_to_responsive import BUILDER_COMMIT
from ev4_transition.transitions.final_gate import RESPONSIVE_COMMIT


def pytest_configure(config):
    """Keep GitHub Actions diagnostics concise without changing execution."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        config.option.verbose = -1
        config.option.tbstyle = "line"
        config.option.disable_warnings = True


@pytest.fixture(autouse=True)
def _emit_runtime_receipts_for_transition_fixture_builders(monkeypatch, request):
    """Make legacy transition fixture builders emit the new positive proof.

    The production resolver never fabricates receipts. This test-only wrapper
    upgrades the two local fixture builders so their viewport artifacts model
    the runtime producer contract explicitly.
    """

    module = request.module
    module_name = getattr(module, "__name__", "")
    if not (
        module_name.endswith("test_builder_to_responsive")
        or module_name.endswith("test_final_gate")
    ):
        return

    original = getattr(module, "_json_file", None)
    if original is None:
        return

    producer_commit = (
        BUILDER_COMMIT
        if module_name.endswith("test_builder_to_responsive")
        else RESPONSIVE_COMMIT
    )

    def write_with_receipt(path: Path, value: dict) -> str:
        runtime_value = value
        is_viewport = (
            isinstance(value, dict)
            and isinstance(value.get("evidence_ref"), str)
            and value.get("viewport") in {"desktop", "tablet", "mobile"}
            and value.get("status") == "confirmed"
        )
        if is_viewport:
            runtime_value = dict(value)
            runtime_value.setdefault("run_id", "TEST-RUNTIME-RUN-1")

        digest = original(path, runtime_value)
        if not is_viewport:
            return digest

        repository_root = path.parent.parent
        artifact_ref = path.relative_to(repository_root).as_posix()
        receipt_path = path.with_name(path.name + ".receipt.json")
        receipt = {
            "schema": RUNTIME_EVIDENCE_RECEIPT_SCHEMA,
            "evidence_type": "viewport_artifact",
            "viewport": runtime_value["viewport"],
            "run_id": runtime_value["run_id"],
            "subject_ref": runtime_value["evidence_ref"],
            "artifact_ref": artifact_ref,
            "artifact_sha256": digest,
            "producer_commit": producer_commit,
            "capture_status": "completed",
            "validation_status": "accepted",
        }
        receipt_path.write_text(
            json.dumps(receipt, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        return digest

    monkeypatch.setattr(module, "_json_file", write_with_receipt)
