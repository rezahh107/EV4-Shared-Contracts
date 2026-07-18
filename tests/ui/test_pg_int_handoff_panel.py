from __future__ import annotations

from pathlib import Path

import ev4_transition.ui.handoff_app as handoff_app
from ev4_transition.service.producer_handoff import ProducerHandoffResponse


ROOT = Path(__file__).resolve().parents[2]


def test_ui_detects_architect_and_ce_routes_without_operator_transition_choice():
    architect = handoff_app.inspect_uploaded_route(
        str(ROOT / "fixtures/producer-emitted/valid/architect-export.v1.json"),
        str(ROOT),
    )
    ce = handoff_app.inspect_uploaded_route(
        str(ROOT / "fixtures/producer-emitted/valid/ce-export.v1.json"),
        str(ROOT),
    )

    assert architect["resolved_transition"] == "architect-to-ce"
    assert architect["routing"]["required_repository_roles"] == ["architect", "ce"]
    assert ce["resolved_transition"] == "ce-to-builder"
    assert ce["routing"]["required_repository_roles"] == ["ce", "builder"]


def test_route_summary_escapes_untrusted_values():
    rendered = handoff_app.route_summary_html(
        {
            "status": "invalid",
            "resolved_transition": "<script>alert(1)</script>",
            "routing": {"producer_stage": "architect", "target_stage": "ce"},
            "user_message_fa": "<img src=x onerror=alert(1)>",
        }
    )

    assert "<script>" not in rendered
    assert "<img" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "&lt;img" in rendered


def test_ui_returns_standalone_output_and_receipt_downloads(monkeypatch, tmp_path: Path):
    output = tmp_path / "ce-input.json"
    receipt = tmp_path / "project-gate-a2c-receipt.json"
    output.write_text("{}", encoding="utf-8")
    receipt.write_text("{}", encoding="utf-8")
    response = ProducerHandoffResponse(
        status="accepted",
        resolved_transition="architect-to-ce",
        routing={"producer_stage": "architect", "target_stage": "ce"},
        diagnostics=[],
        engine_result={
            "status": "accepted",
            "resolved_transition": "architect-to-ce",
            "handoff_allowed": True,
            "diagnostics": [],
            "operator_artifacts": {
                "next_stage": {"path": str(output), "downloadable": True},
                "receipt": {"path": str(receipt), "downloadable": True},
            },
        },
        artifact_metadata={
            "next_stage": {"path": str(output), "downloadable": True},
            "receipt": {"path": str(receipt), "downloadable": True},
        },
        download_paths=[str(output), str(receipt)],
        user_message_fa="accepted",
        next_action_fa="فایل ce-input.json را به CE بدهید.",
    )
    monkeypatch.setattr(handoff_app, "run_producer_handoff_request", lambda request: response)

    status, diagnostics, preview, downloads = handoff_app.run_uploaded_handoff(
        "architect-project-gate.json",
        str(ROOT),
        "/local/architect",
        "/local/ce",
        None,
        str(tmp_path),
    )

    assert "پذیرفته شد" in status
    assert diagnostics == []
    assert "architect-to-ce" in preview
    assert downloads == [str(output), str(receipt)]


def test_ui_does_not_offer_blocked_next_stage_artifact(monkeypatch, tmp_path: Path):
    receipt = tmp_path / "project-gate-c2b-receipt.json"
    receipt.write_text("{}", encoding="utf-8")
    response = ProducerHandoffResponse(
        status="insufficient_evidence",
        resolved_transition="ce-to-builder",
        routing={"producer_stage": "ce", "target_stage": "builder"},
        diagnostics=[
            {
                "code": "PG_C2B_SOURCE_HANDOFF_NOT_ALLOWED",
                "severity": "insufficient_evidence",
                "path": "$.handoff.allowed",
                "message": "blocked",
            }
        ],
        engine_result={
            "status": "insufficient_evidence",
            "resolved_transition": "ce-to-builder",
            "handoff_allowed": False,
            "diagnostics": [],
        },
        artifact_metadata={
            "next_stage": {"path": str(tmp_path / "builder-input.json"), "downloadable": False},
            "receipt": {"path": str(receipt), "downloadable": True},
        },
        download_paths=[str(receipt)],
        user_message_fa="blocked",
        next_action_fa="diagnostics را بررسی کنید.",
    )
    monkeypatch.setattr(handoff_app, "run_producer_handoff_request", lambda request: response)

    status, diagnostics, preview, downloads = handoff_app.run_uploaded_handoff(
        "ce-project-gate.json",
        str(ROOT),
        None,
        "/local/ce",
        "/local/builder",
        str(tmp_path),
    )

    assert "شواهد کافی نیست" in status
    assert diagnostics
    assert "handoff_allowed" in preview
    assert downloads == [str(receipt)]
