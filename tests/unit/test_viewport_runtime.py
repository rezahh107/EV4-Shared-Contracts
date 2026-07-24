from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from ev4_transition.runners.records import (
    TimeoutPolicy,
    build_adapter_execution_record,
)
from ev4_transition.viewport_runtime import (
    RUNTIME_EVIDENCE_RECEIPT_SCHEMA,
    ViewportEvidenceRun,
    verify_viewport_evidence_run,
)

REPOSITORY = "rezahh107/EV4-Builder-Assistant-Repo"
TOOL = "scripts/capture-viewports.py"
SUBJECT = "desktop-proof"
VIEWPORT = "desktop"
RUN_ID = "RUN-1"


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.strip()


def _write_artifact(path: Path, value: object) -> str:
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _context(tmp_path: Path):
    root = tmp_path / "builder"
    root.mkdir()
    _git(root, "init", "--quiet")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "EV4 Tests")
    _git(root, "remote", "add", "origin", f"https://github.com/{REPOSITORY}.git")
    tool = root / TOOL
    tool.parent.mkdir(parents=True)
    tool.write_text("# official viewport capture adapter\n", encoding="utf-8")
    _git(root, "add", TOOL)
    _git(root, "commit", "--quiet", "-m", "add viewport adapter")
    commit = _git(root, "rev-parse", "HEAD")

    artifact = root / "runtime" / "desktop.json"
    artifact.parent.mkdir()
    digest = _write_artifact(
        artifact,
        {
            "evidence_ref": SUBJECT,
            "viewport": VIEWPORT,
            "run_id": RUN_ID,
            "status": "confirmed",
        },
    )
    record = build_adapter_execution_record(
        owner_repo=REPOSITORY,
        owner_commit=commit,
        adapter_path=TOOL,
        command_or_entrypoint=["python", TOOL],
        command=["python", TOOL],
        working_directory=str(root),
        exit_code=0,
        stdout_hash="1" * 64,
        stderr_hash="2" * 64,
        started_by="project_gate_test",
        timeout_policy=TimeoutPolicy(seconds=30),
        input_ref=SUBJECT,
        input_hash=None,
        output_ref="runtime/desktop.json",
        output_hash=digest,
        validator_after_adapter_ref=None,
    )
    run = ViewportEvidenceRun(
        run_id=RUN_ID,
        producer_repository=REPOSITORY,
        producer_commit=commit,
        producer_tool=TOOL,
        subject_ref=SUBJECT,
        viewport=VIEWPORT,
        artifact_path=artifact,
        artifact_sha256=digest,
        capture_status="completed",
        validation_status="accepted",
        execution_record=record,
    )
    return root, commit, artifact, run


def _verify(root: Path, commit: str, run: ViewportEvidenceRun):
    return verify_viewport_evidence_run(
        run=run,
        producer_checkout=root,
        expected_repository=REPOSITORY,
        expected_commit=commit,
        expected_tool=TOOL,
        expected_subject_ref=SUBJECT,
        expected_viewport=VIEWPORT,
    )


def _codes(result) -> set[str]:
    return {item["code"] for item in result.diagnostics}


def test_observed_typed_runtime_result_is_verified_and_receipt_is_derived(tmp_path: Path):
    root, commit, _, run = _context(tmp_path)
    result = _verify(root, commit, run)
    assert result.classification == "real_verified", result.diagnostics
    assert result.positive_proof_verified is True
    assert result.derived_receipt is not None
    assert result.derived_receipt["schema"] == RUNTIME_EVIDENCE_RECEIPT_SCHEMA
    assert result.derived_receipt["execution_record_digest"] == run.execution_record.execution_record_hash
    assert not (run.artifact_path.with_name(run.artifact_path.name + ".receipt.json")).exists()


@pytest.mark.parametrize(
    ("mutator", "expected_code"),
    [
        (lambda run: replace(run, producer_repository="other/repo"), "PG.EVIDENCE.RUNTIME_REPOSITORY_MISMATCH"),
        (lambda run: replace(run, producer_commit="0" * 40), "PG.EVIDENCE.RUNTIME_COMMIT_MISMATCH"),
        (lambda run: replace(run, producer_tool="scripts/other.py"), "PG.EVIDENCE.RUNTIME_TOOL_MISMATCH"),
        (lambda run: replace(run, execution_record=None), "PG.EVIDENCE.RUNTIME_EXECUTION_RECORD_REQUIRED"),
        (lambda run: replace(run, capture_status="started"), "PG.EVIDENCE.RUNTIME_CAPTURE_INCOMPLETE"),
        (lambda run: replace(run, validation_status="rejected"), "PG.EVIDENCE.RUNTIME_VALIDATION_NOT_ACCEPTED"),
        (lambda run: replace(run, run_id="RUN-OTHER"), "PG.EVIDENCE.RUNTIME_ARTIFACT_BINDING_MISMATCH"),
        (lambda run: replace(run, subject_ref="other-subject"), "PG.EVIDENCE.RUNTIME_SUBJECT_MISMATCH"),
        (lambda run: replace(run, viewport="tablet"), "PG.EVIDENCE.RUNTIME_VIEWPORT_MISMATCH"),
    ],
)
def test_runtime_context_mismatches_are_rejected(tmp_path: Path, mutator, expected_code: str):
    root, commit, _, run = _context(tmp_path)
    result = _verify(root, commit, mutator(run))
    assert result.classification == "insufficient_evidence"
    assert result.positive_proof_verified is False
    assert expected_code in _codes(result)


def test_failed_process_exit_is_rejected(tmp_path: Path):
    root, commit, _, run = _context(tmp_path)
    failed_record = replace(run.execution_record, exit_code=1, failure_code="capture_failed")
    result = _verify(root, commit, replace(run, execution_record=failed_record))
    assert result.classification == "insufficient_evidence"
    assert "PG.EVIDENCE.RUNTIME_EXECUTION_FAILED" in _codes(result)


def test_missing_artifact_is_rejected(tmp_path: Path):
    root, commit, _, run = _context(tmp_path)
    result = _verify(root, commit, replace(run, artifact_path=root / "runtime/missing.json"))
    assert result.classification == "insufficient_evidence"
    assert "PG.EVIDENCE.RUNTIME_ARTIFACT_MISSING" in _codes(result)


def test_recorded_hash_mismatch_is_rejected(tmp_path: Path):
    root, commit, _, run = _context(tmp_path)
    result = _verify(root, commit, replace(run, artifact_sha256="a" * 64))
    assert result.classification == "insufficient_evidence"
    assert "PG.EVIDENCE.RUNTIME_ARTIFACT_MUTATED" in _codes(result)


def test_execution_record_output_hash_mismatch_is_rejected(tmp_path: Path):
    root, commit, _, run = _context(tmp_path)
    record = replace(run.execution_record, output_hash="b" * 64)
    result = _verify(root, commit, replace(run, execution_record=record))
    assert result.classification == "insufficient_evidence"
    assert "PG.EVIDENCE.RUNTIME_EXECUTION_OUTPUT_HASH_MISMATCH" in _codes(result)


def test_artifact_mutation_after_execution_is_rejected(tmp_path: Path):
    root, commit, artifact, run = _context(tmp_path)
    _write_artifact(
        artifact,
        {
            "evidence_ref": SUBJECT,
            "viewport": VIEWPORT,
            "run_id": RUN_ID,
            "status": "confirmed",
            "mutated": True,
        },
    )
    result = _verify(root, commit, run)
    assert result.classification == "insufficient_evidence"
    assert "PG.EVIDENCE.RUNTIME_ARTIFACT_MUTATED" in _codes(result)


def test_invalid_artifact_json_is_rejected(tmp_path: Path):
    root, commit, artifact, run = _context(tmp_path)
    digest = _write_artifact(artifact, "not-json")
    record = replace(run.execution_record, output_hash=digest)
    result = _verify(
        root,
        commit,
        replace(run, artifact_sha256=digest, execution_record=record),
    )
    assert result.classification == "insufficient_evidence"
    assert "PG.EVIDENCE.RUNTIME_ARTIFACT_JSON_INVALID" in _codes(result)


def test_synthetic_runtime_artifact_is_rejected(tmp_path: Path):
    root, commit, artifact, run = _context(tmp_path)
    digest = _write_artifact(
        artifact,
        {
            "evidence_ref": SUBJECT,
            "viewport": VIEWPORT,
            "run_id": RUN_ID,
            "status": "confirmed",
            "provenance": {"source": "synthetic_fixture"},
        },
    )
    record = replace(run.execution_record, output_hash=digest)
    result = _verify(
        root,
        commit,
        replace(run, artifact_sha256=digest, execution_record=record),
    )
    assert result.classification == "synthetic"
    assert result.positive_proof_verified is False
    assert "PG.EVIDENCE.SYNTHETIC_DERIVED" in _codes(result)
