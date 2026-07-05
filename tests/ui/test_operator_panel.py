from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from ev4_transition.ui.adapters import (
    CAPABILITY_STATUS_PATH,
    build_capability_rows,
    load_capability_payload,
    render_download_artifacts,
    run_operator_check,
)
from ev4_transition.ui.components import diagnostics_to_rows, ltr_token, status_summary_markdown


def test_malformed_json_returns_safe_ui_error(tmp_path: Path):
    output = run_operator_check(
        "Validate Stage Evidence Bundle",
        pasted_json='{"schema_version": ',
        output_dir=tmp_path,
    )

    assert output.result["status"] == "invalid"
    assert output.result["diagnostics"][0]["code"] == "MALFORMED_JSON"
    assert "JSON واردشده معتبر نیست" in output.result["diagnostics"][0]["message"]
    assert output.download_paths


def test_status_mapping_for_project_gate_statuses():
    cases = {
        "accepted": "✅",
        "valid": "✅",
        "invalid": "❌",
        "insufficient_evidence": "⚠️",
        "repair_needed": "🛠️",
    }

    for status, icon in cases.items():
        rendered = status_summary_markdown({"status": status, "diagnostics": []})
        assert icon in rendered
        assert "وضعیت" in rendered
        assert status in rendered


def test_diagnostics_rendering_preserves_code_severity_and_path():
    rows = diagnostics_to_rows(
        [
            {
                "code": "PG_UI_TEST",
                "severity": "insufficient_evidence",
                "path": "$.evidence[0].artifact_hash.value",
                "message": "Missing evidence.",
                "details": {"repository": "rezahh107/EV4-Project-Gate", "next_action": "Add evidence."},
            }
        ]
    )

    assert len(rows) == 1
    row_text = " ".join(rows[0])
    assert "PG_UI_TEST" in row_text
    assert "insufficient_evidence" in row_text
    assert "$.evidence[0].artifact_hash.value" in row_text
    assert "rezahh107/EV4-Project-Gate" in row_text


def test_ltr_isolation_helper_wraps_technical_tokens():
    token = ltr_token("schemas/stage-bundle/stage-bundle.v1.schema.json")

    assert token.startswith("\u2066")
    assert token.endswith("\u2069")
    assert "schemas/stage-bundle/stage-bundle.v1.schema.json" in token


def test_capability_inspector_reads_without_mutating_source_file():
    before = CAPABILITY_STATUS_PATH.read_text(encoding="utf-8")
    payload = load_capability_payload()
    rows = build_capability_rows()
    after = CAPABILITY_STATUS_PATH.read_text(encoding="utf-8")

    assert payload["schema_version"] == "ev4-project-gate-capability-status.v1"
    assert rows
    assert before == after


def test_unavailable_transition_is_marked_and_does_not_fake_execution(tmp_path: Path):
    output = run_operator_check("CE → Builder", pasted_json='{"schema_version": "x"}', output_dir=tmp_path)

    assert output.result["status"] == "insufficient_evidence"
    assert output.result["diagnostics"][0]["code"] == "UI_TRANSITION_NOT_WIRED"
    assert output.result["output"] is None
    assert "Prompt 2" in output.result["diagnostics"][0]["message"]


def test_report_and_result_rendering_does_not_mutate_original_result(tmp_path: Path):
    result = {
        "schema_version": "ev4-project-gate-ui-result.v1",
        "result_type": "ui_guard",
        "status": "repair_needed",
        "diagnostics": [
            {
                "code": "PG_UI_REPAIR",
                "severity": "warning",
                "message": "Repair is needed.",
                "path": "$.payload",
            }
        ],
        "output": {"path": "fixtures/example.json"},
    }
    before = deepcopy(result)

    paths = render_download_artifacts(result, tmp_path)

    assert result == before
    assert {Path(path).name for path in paths} == {"result.json", "report.md", "report.html"}
    loaded = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert loaded == before
