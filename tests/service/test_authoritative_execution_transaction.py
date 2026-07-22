from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest

import ev4_transition.service.execution_transaction as transaction_module
from ev4_transition.service import (
    GateRequest,
    PreflightResult,
    RepoPaths,
    execute_authoritative_gate_transaction,
    prepare_authoritative_gate_transaction,
    run_authoritative_preflight_and_gate,
)


def _preflight(status: str, fingerprint: str | None = None) -> PreflightResult:
    return PreflightResult(
        status=status,  # type: ignore[arg-type]
        transition_choice="architect_to_ce",
        checks=[],
        summary_fa=status,
        request_fingerprint=fingerprint,
    )


def _request() -> GateRequest:
    return GateRequest(
        transition_choice="architect_to_ce",
        input_data={"stage": "architect"},
        repo_paths=RepoPaths(
            project_gate_repo_path="/project-gate",
            architect_repo_path="/architect",
            ce_repo_path="/ce",
            builder_repo_path="/irrelevant-builder",
        ),
        output_dir="/outputs",
        preflight_mode="service_immediate",
        preflight_fingerprint="reusable-old-token",
    )


def test_ready_preflight_binds_fingerprint_to_same_logical_request(monkeypatch) -> None:
    observed = {}

    def fake_preflight(request):
        observed["preflight_request"] = request
        return _preflight("ready", "fresh-token")

    def fake_run(request):
        observed["run_request"] = request
        return SimpleNamespace(status="accepted")

    monkeypatch.setattr(transaction_module, "run_preflight", fake_preflight)
    monkeypatch.setattr(transaction_module, "run_gate_request", fake_run)

    result = run_authoritative_preflight_and_gate(_request())

    assert result.dispatch_started is True
    assert observed["preflight_request"].preflight_mode == "external_token"
    assert observed["preflight_request"].preflight_fingerprint is None
    assert observed["run_request"] == replace(
        observed["preflight_request"],
        preflight_fingerprint="fresh-token",
    )


@pytest.mark.parametrize("status", ["blocked", "warnings"])
def test_non_ready_preflight_never_calls_dispatcher(monkeypatch, status: str) -> None:
    called = {"dispatch": False}
    monkeypatch.setattr(transaction_module, "run_preflight", lambda request: _preflight(status))

    def forbidden_dispatch(request):
        called["dispatch"] = True
        raise AssertionError("dispatcher must not run")

    monkeypatch.setattr(transaction_module, "run_gate_request", forbidden_dispatch)
    result = run_authoritative_preflight_and_gate(_request())

    assert result.response is None
    assert called["dispatch"] is False


def test_ready_without_fingerprint_fails_closed(monkeypatch) -> None:
    called = {"dispatch": False}
    monkeypatch.setattr(transaction_module, "run_preflight", lambda request: _preflight("ready", None))
    monkeypatch.setattr(
        transaction_module,
        "run_gate_request",
        lambda request: called.__setitem__("dispatch", True),
    )

    prepared = prepare_authoritative_gate_transaction(_request())
    result = execute_authoritative_gate_transaction(prepared)

    assert prepared.authorization_ready is False
    assert result.response is None
    assert called["dispatch"] is False


def test_transaction_never_preserves_service_immediate_bypass(monkeypatch) -> None:
    observed = []

    def fake_preflight(request):
        observed.append(request)
        return _preflight("blocked")

    monkeypatch.setattr(transaction_module, "run_preflight", fake_preflight)
    prepare_authoritative_gate_transaction(_request())

    assert observed[0].preflight_mode == "external_token"
    assert observed[0].preflight_fingerprint is None
