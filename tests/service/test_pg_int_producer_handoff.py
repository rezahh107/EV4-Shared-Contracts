from __future__ import annotations

import json
from pathlib import Path

import ev4_transition.cli_handoff as cli_handoff
import ev4_transition.producer_integration.facade as facade
import ev4_transition.service.producer_handoff as service_module
from ev4_transition.io.secure_snapshot import capture_json_snapshot
from ev4_transition.service.models import RepoPaths
from ev4_transition.service.producer_handoff import (
    ProducerHandoffRequest,
    ProducerHandoffResponse,
    run_producer_handoff_request,
)


ROOT = Path(__file__).resolve().parents[2]


def _load_fixture(name: str) -> dict:
    return json.loads((ROOT / f"fixtures/producer-emitted/valid/{name}-export.v1.json").read_text(encoding="utf-8"))


def test_inspection_routes_architect_and_ce_from_validated_export_data():
    architect = facade.inspect_producer_handoff(ROOT / "fixtures/producer-emitted/valid/architect-export.v1.json", project_gate_repo=ROOT)
    ce = facade.inspect_producer_handoff(ROOT / "fixtures/producer-emitted/valid/ce-export.v1.json", project_gate_repo=ROOT)

    assert architect["status"] == "accepted"
    assert architect["resolved_transition"] == "architect-to-ce"
    assert architect["routing"]["required_repository_roles"] == ["architect", "ce"]
    assert architect["routing"]["filename_used_for_routing"] is False
    assert architect["routing"]["operator_transition_selection_used"] is False

    assert ce["status"] == "accepted"
    assert ce["resolved_transition"] == "ce-to-builder"
    assert ce["routing"]["required_repository_roles"] == ["ce", "builder"]


def test_filename_cannot_override_validated_architect_route(tmp_path: Path):
    misleading = tmp_path / "ce-project-gate.json"
    misleading.write_text(
        (ROOT / "fixtures/producer-emitted/valid/architect-export.v1.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = facade.inspect_producer_handoff(misleading, project_gate_repo=ROOT)

    assert result["status"] == "accepted"
    assert result["resolved_transition"] == "architect-to-ce"
    assert result["source_snapshot"]["filename"] == "ce-project-gate.json"
    assert result["routing"]["filename_used_for_routing"] is False


def test_unsupported_builder_route_fails_closed():
    result = facade.inspect_producer_handoff(
        ROOT / "fixtures/producer-emitted/valid/builder-export.v1.json",
        project_gate_repo=ROOT,
    )

    assert result["status"] == "invalid"
    assert result["failure_class"] == "unsupported"
    assert result["handoff_allowed"] is False
    assert any(item["code"] == "PG_INT_UNSUPPORTED_TRANSITION" for item in result["diagnostics"])


def test_producer_target_mismatch_fails_closed(monkeypatch, tmp_path: Path):
    source = tmp_path / "export.json"
    source.write_text('{"handoff":{"target":"ce-intake"}}', encoding="utf-8")

    monkeypatch.setattr(
        facade,
        "intake_producer_export",
        lambda *args, **kwargs: {
            "schema_version": "producer-emitted-transition-result.v1",
            "status": "accepted",
            "producer": {"stage": "ce", "repository": "rezahh107/EV4-Constructability-Engineer-Repo"},
            "resolved_transition": "architect-to-ce",
            "diagnostics": [],
            "handoff_allowed": False,
        },
    )

    result = facade.inspect_producer_handoff(source, project_gate_repo=ROOT)

    assert result["status"] == "invalid"
    assert result["failure_class"] == "unsupported"
    assert any(item["code"] == "PG_INT_PRODUCER_TARGET_MISMATCH" for item in result["diagnostics"])


def test_a2c_execution_requires_only_architect_and_ce_paths(monkeypatch, tmp_path: Path):
    source = tmp_path / "producer.json"
    source.write_text('{"handoff":{"target":"ce-intake"}}', encoding="utf-8")
    architect = tmp_path / "architect"
    ce = tmp_path / "ce"
    architect.mkdir()
    ce.mkdir()
    captured = {}

    monkeypatch.setattr(
        facade,
        "intake_producer_export",
        lambda *args, **kwargs: {
            "schema_version": "producer-emitted-transition-result.v1",
            "status": "accepted",
            "producer": {"stage": "architect", "repository": "rezahh107/EV4-Architect-Repo"},
            "resolved_transition": "architect-to-ce",
            "diagnostics": [],
            "handoff_allowed": False,
        },
    )

    def fake_transition(name, artifact, **kwargs):
        captured.update(name=name, artifact=artifact, kwargs=kwargs)
        return {
            "status": "accepted",
            "resolved_transition": name,
            "handoff_allowed": True,
            "diagnostics": [],
            "downstream_artifact": {
                "status": "published_verified",
                "path": str(kwargs["output_path"]),
            },
            "receipt": {
                "status": "published_verified",
                "path": str(kwargs["receipt_path"]),
            },
        }

    monkeypatch.setattr(facade, "transition_producer_export", fake_transition)
    result = facade.execute_producer_handoff(
        source,
        project_gate_repo=ROOT,
        architect_repo=architect,
        ce_repo=ce,
        output_dir=tmp_path / "out",
    )

    assert result["status"] == "accepted"
    assert captured["name"] == "architect-to-ce"
    assert captured["kwargs"]["architect_repo"] == architect
    assert captured["kwargs"]["ce_repo"] == ce
    assert captured["kwargs"]["builder_repo"] is None
    assert Path(captured["kwargs"]["output_path"]).name == "ce-input.json"
    assert Path(captured["kwargs"]["receipt_path"]).name == "project-gate-a2c-receipt.json"


def test_c2b_execution_requires_only_ce_and_builder_paths(monkeypatch, tmp_path: Path):
    source = tmp_path / "producer.json"
    source.write_text('{"handoff":{"target":"builder-intake"}}', encoding="utf-8")
    ce = tmp_path / "ce"
    builder = tmp_path / "builder"
    ce.mkdir()
    builder.mkdir()
    captured = {}

    monkeypatch.setattr(
        facade,
        "intake_producer_export",
        lambda *args, **kwargs: {
            "schema_version": "producer-emitted-transition-result.v1",
            "status": "accepted",
            "producer": {"stage": "ce", "repository": "rezahh107/EV4-Constructability-Engineer-Repo"},
            "resolved_transition": "ce-to-builder",
            "diagnostics": [],
            "handoff_allowed": False,
        },
    )

    def fake_transition(name, artifact, **kwargs):
        captured.update(name=name, kwargs=kwargs)
        return {"status": "insufficient_evidence", "resolved_transition": name, "handoff_allowed": False, "diagnostics": []}

    monkeypatch.setattr(facade, "transition_producer_export", fake_transition)
    result = facade.execute_producer_handoff(
        source,
        project_gate_repo=ROOT,
        ce_repo=ce,
        builder_repo=builder,
        output_dir=tmp_path / "out",
    )

    assert result["status"] == "insufficient_evidence"
    assert captured["name"] == "ce-to-builder"
    assert captured["kwargs"]["architect_repo"] is None
    assert captured["kwargs"]["ce_repo"] == ce
    assert captured["kwargs"]["builder_repo"] == builder
    assert Path(captured["kwargs"]["output_path"]).name == "builder-input.json"
    assert Path(captured["kwargs"]["receipt_path"]).name == "project-gate-c2b-receipt.json"


def test_service_downloads_only_consumable_artifact_but_preserves_receipt(monkeypatch, tmp_path: Path):
    output = tmp_path / "builder-input.json"
    receipt = tmp_path / "project-gate-c2b-receipt.json"
    output.write_text("{}", encoding="utf-8")
    receipt.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        service_module,
        "execute_producer_handoff",
        lambda *args, **kwargs: {
            "status": "insufficient_evidence",
            "resolved_transition": "ce-to-builder",
            "handoff_allowed": False,
            "diagnostics": [],
            "routing": {"producer_stage": "ce", "target_stage": "builder"},
            "operator_artifacts": {
                "next_stage": {"path": str(output), "downloadable": False, "publication_state": "published_verified"},
                "receipt": {"path": str(receipt), "downloadable": True, "publication_state": "published_verified"},
                "next_action_fa": "diagnostics را بررسی کنید.",
            },
        },
    )

    response = run_producer_handoff_request(ProducerHandoffRequest(source_path="source.json"))

    assert response.status == "insufficient_evidence"
    assert response.download_paths == [str(receipt)]
    assert response.artifact_metadata["next_stage"]["downloadable"] is False


def test_cli_has_no_transition_selector_and_emits_structured_result(monkeypatch, capsys):
    response = ProducerHandoffResponse(
        status="accepted",
        resolved_transition="architect-to-ce",
        routing={"producer_stage": "architect", "target_stage": "ce"},
        diagnostics=[],
        engine_result={"status": "accepted", "handoff_allowed": True},
        artifact_metadata={
            "next_stage": {"path": "ce-input.json"},
            "receipt": {"path": "project-gate-a2c-receipt.json"},
        },
        download_paths=["ce-input.json", "project-gate-a2c-receipt.json"],
        user_message_fa="accepted",
        next_action_fa="فایل ce-input.json را به CE بدهید.",
    )
    monkeypatch.setattr(cli_handoff, "run_producer_handoff_request", lambda request: response)

    exit_code = cli_handoff.main(["producer-export.json", "--format", "json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["resolved_transition"] == "architect-to-ce"
    assert payload["routing"]["producer_stage"] == "architect"
