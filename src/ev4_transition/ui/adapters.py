from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import logging
from pathlib import Path
import shutil
import tempfile
from typing import Any

from ev4_transition.canonical_json import canonical_dumps, load_json_file
from ev4_transition.presentation.rtl import bdi_ltr, escape_html, ltr_code_block
from ev4_transition.service import GateRequest, RepoPaths, ServiceDiagnostic, run_gate_request
from ev4_transition.service.guidance import build_operator_guidance
from ev4_transition.service.json_input import parse_json_input

from .components import capability_rows_from_payload, diagnostics_to_rows, status_summary_markdown
from .state import option_for_label

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CAPABILITY_STATUS_PATH = PACKAGE_ROOT / "data" / "capability-status.v1.json"
LOGGER = logging.getLogger(__name__)

_EXPECTED_SOURCE_STAGE_BY_TRANSITION = {
    "architect_to_ce": "architect",
    "ce_to_builder": "ce",
    "builder_to_responsive": "builder",
    "final_gate": "responsive",
}


@dataclass(frozen=True)
class UiRunOutput:
    result: dict[str, Any]
    status_markdown: str
    diagnostics_rows: list[list[str]]
    capability_rows: list[list[str]]
    json_preview: str
    download_paths: list[str]


@dataclass(frozen=True)
class ErrorState:
    code: str
    message_fa: str
    next_action_fa: str
    error_type: str

    def to_result(self, transition_choice: str) -> dict[str, Any]:
        return {
            "schema_version": "ev4-project-gate-ui-result.v1",
            "result_type": "ui_error_state",
            "transition_choice": transition_choice,
            "status": "invalid",
            "diagnostics": [
                {
                    "code": self.code,
                    "severity": "error",
                    "message": self.message_fa,
                    "path": "$",
                    "details": {"error_type": self.error_type, "next_action": self.next_action_fa},
                }
            ],
            "output": None,
        }


def run_operator_check(
    transition_label: str | None,
    pasted_json: str | None = None,
    uploaded_file: Any | None = None,
    project_gate_repo_path: str | None = None,
    architect_repo_path: str | None = None,
    ce_repo_path: str | None = None,
    builder_repo_path: str | None = None,
    responsive_repo_path: str | None = None,
    *,
    acquisition_mode: str = "pinned_owner_file_computation",
    output_dir: str | Path | None = None,
    output_path: str | Path | None = None,
    receipt_path: str | Path | None = None,
) -> UiRunOutput:
    """Run the selected UI action through the authoritative Project Gate service."""

    option = option_for_label(transition_label)
    choice = option.service_choice
    try:
        request = build_gate_request(
            transition_label,
            pasted_json=pasted_json,
            uploaded_file=uploaded_file,
            project_gate_repo_path=project_gate_repo_path,
            architect_repo_path=architect_repo_path,
            ce_repo_path=ce_repo_path,
            builder_repo_path=builder_repo_path,
            responsive_repo_path=responsive_repo_path,
            acquisition_mode=acquisition_mode,
            output_dir=output_dir,
            output_path=output_path,
            receipt_path=receipt_path,
        )
        preflight_diagnostics = _ui_preflight_diagnostics(request)
        if preflight_diagnostics:
            result = _preflight_result(choice, preflight_diagnostics)
        else:
            response = run_gate_request(request)
            result = _result_from_response(response)
            result["ui_acquisition_mode"] = acquisition_mode
    except Exception as exc:  # Defensive UI boundary; primary view must not expose traceback.
        LOGGER.exception("Unhandled exception in UI operator check")
        result = ErrorState(
            code="PG.UI.UNHANDLED_EXCEPTION",
            message_fa="اجرای UI با خطای کنترل‌شده متوقف شد و traceback خام در نمای اصلی نمایش داده نشد.",
            next_action_fa="گزارش فنی را دانلود کن و correlation ID یا خطای مسیر و وابستگی محلی را بررسی کن.",
            error_type=type(exc).__name__,
        ).to_result(choice)
    try:
        return _finalize(result, output_dir)
    except Exception as exc:  # Final rendering containment.
        LOGGER.exception("Critical failure while finalizing UI operator output")
        fallback = ErrorState(
            code="PG.UI.CRITICAL_FINALIZATION_FAILURE",
            message_fa="آماده‌سازی خروجی UI با خطای کنترل‌شده متوقف شد و traceback خام در نمای اصلی نمایش داده نشد.",
            next_action_fa="گزارش technical/log را بررسی کن و مسیر خروجی را اصلاح کن.",
            error_type=type(exc).__name__,
        ).to_result(choice)
        return _minimal_output(fallback)


def build_gate_request(
    transition_label: str | None,
    *,
    pasted_json: str | None = None,
    uploaded_file: Any | None = None,
    project_gate_repo_path: str | None = None,
    architect_repo_path: str | None = None,
    ce_repo_path: str | None = None,
    builder_repo_path: str | None = None,
    responsive_repo_path: str | None = None,
    acquisition_mode: str = "pinned_owner_file_computation",
    output_dir: str | Path | None = None,
    output_path: str | Path | None = None,
    receipt_path: str | Path | None = None,
) -> GateRequest:
    option = option_for_label(transition_label)
    input_text = pasted_json if pasted_json and pasted_json.strip() else None
    input_path = _uploaded_path(uploaded_file)
    if acquisition_mode != "producer_emitted_gate_artifact" and input_text is not None:
        input_path = None
    return GateRequest(
        transition_choice=option.service_choice,  # type: ignore[arg-type]
        input_json_path=input_path,
        input_json_text=input_text,
        repo_paths=RepoPaths(
            project_gate_repo_path=_clean_path(project_gate_repo_path) or str(REPOSITORY_ROOT),
            architect_repo_path=_clean_path(architect_repo_path),
            ce_repo_path=_clean_path(ce_repo_path),
            builder_repo_path=_clean_path(builder_repo_path),
            responsive_repo_path=_clean_path(responsive_repo_path),
        ),
        acquisition_mode=acquisition_mode,  # type: ignore[arg-type]
        output_dir=_clean_path(str(output_dir)) if output_dir is not None else None,
        output_path=_clean_path(str(output_path)) if output_path is not None else None,
        receipt_path=_clean_path(str(receipt_path)) if receipt_path is not None else None,
    )


def load_capability_payload(path: str | Path = CAPABILITY_STATUS_PATH) -> dict[str, Any]:
    payload = load_json_file(path)
    if not isinstance(payload, dict):
        raise ValueError("capability-status.v1.json must contain a JSON object")
    return payload


def build_capability_rows(path: str | Path = CAPABILITY_STATUS_PATH) -> list[list[str]]:
    return capability_rows_from_payload(load_capability_payload(path))


def render_download_artifacts(result: dict[str, Any], output_dir: str | Path | None = None) -> list[str]:
    directory = Path(output_dir) if output_dir is not None else Path(tempfile.mkdtemp(prefix="ev4_project_gate_ui_"))
    written_paths: list[Path] = []
    try:
        directory.mkdir(parents=True, exist_ok=True)
        files = {
            "result.json": canonical_dumps(deepcopy(result)),
            "report.md": _markdown_report(result),
            "report.html": _html_report(result),
        }
        paths: list[str] = []
        for name, content in files.items():
            path = directory / name
            path.write_text(content, encoding="utf-8")
            written_paths.append(path)
            paths.append(str(path))
        return paths
    except OSError as exc:
        LOGGER.error("Failed to render download artifacts: %s", exc)
        for path in written_paths:
            path.unlink(missing_ok=True)
        if output_dir is None:
            shutil.rmtree(directory, ignore_errors=True)
        return []


def _minimal_output(result: dict[str, Any]) -> UiRunOutput:
    return UiRunOutput(
        result=result,
        status_markdown=status_summary_markdown(result),
        diagnostics_rows=diagnostics_to_rows(result.get("diagnostics", [])),
        capability_rows=[],
        json_preview=canonical_dumps(result),
        download_paths=[],
    )


def _result_from_response(response: Any) -> dict[str, Any]:
    payload = response.to_dict()
    diagnostics = list(payload.get("service_diagnostics") or [])
    engine_result = payload.get("engine_result")
    if isinstance(engine_result, dict) and isinstance(engine_result.get("diagnostics"), list):
        known = {(item.get("code"), item.get("path")) for item in diagnostics if isinstance(item, dict)}
        diagnostics.extend(
            deepcopy(item)
            for item in engine_result["diagnostics"]
            if isinstance(item, dict) and (item.get("code"), item.get("path")) not in known
        )
    return {
        "schema_version": "ev4-project-gate-ui-result.v1",
        "result_type": "service_response",
        "transition_choice": payload.get("transition_choice"),
        "status": payload.get("status", "invalid"),
        "user_message_fa": payload.get("user_message_fa", ""),
        "next_action_fa": payload.get("next_action_fa", ""),
        "diagnostics": diagnostics,
        "engine_result": engine_result,
        "capabilities_snapshot": payload.get("capabilities_snapshot"),
        "download_filenames": payload.get("download_filenames", {}),
        "published_download_paths": list(payload.get("download_paths") or []),
        "report_bundle": payload.get("report_bundle", {}),
        "output": engine_result.get("output") if isinstance(engine_result, dict) else None,
    }


def _ui_preflight_diagnostics(request: GateRequest) -> list[ServiceDiagnostic]:
    choice = str(request.transition_choice)
    if choice in {"validate_bundle", "inspect_capabilities"}:
        return []
    if request.acquisition_mode == "producer_emitted_gate_artifact":
        if request.input_json_text is not None or request.input_data is not None or not request.input_json_path:
            return [
                ServiceDiagnostic(
                    "PG.UI.PRODUCER_SOURCE_FILE_REQUIRED",
                    "error",
                    "در حالت producer_emitted_gate_artifact باید فایل اصلی Producer Gate Export را بارگذاری کنید؛ paste متن JSON مجاز نیست.",
                    "$.input_json_path",
                    {"acquisition_mode": request.acquisition_mode},
                )
            ]
        parsed = parse_json_input(input_json_path=request.input_json_path)
    else:
        parsed = parse_json_input(
            input_json_path=request.input_json_path,
            input_json_text=request.input_json_text,
            input_data=request.input_data,
        )
    if parsed.diagnostics or not isinstance(parsed.value, dict):
        return []
    value = parsed.value
    if _looks_like_project_gate_result(value):
        return [
            ServiceDiagnostic(
                "PG.UI.RESULT_ARTIFACT_USED_AS_SOURCE",
                "error",
                "Project Gate result/report artifact cannot be used as a transition source.",
                "$",
                {"transition_choice": choice, "observed_result_type": value.get("result_type")},
            )
        ]
    schema = value.get("schema_version")
    if request.acquisition_mode == "producer_emitted_gate_artifact" and schema != "producer-gate-export.v1":
        return [
            ServiceDiagnostic(
                "PG.UI.SOURCE_SCHEMA_MODE_MISMATCH",
                "error",
                "The uploaded source schema is not compatible with producer_emitted_gate_artifact.",
                "$.schema_version",
                {"observed_schema": schema, "acquisition_mode": request.acquisition_mode},
            )
        ]
    if request.acquisition_mode != "producer_emitted_gate_artifact" and schema == "producer-gate-export.v1":
        return [
            ServiceDiagnostic(
                "PG.UI.SOURCE_SCHEMA_MODE_MISMATCH",
                "error",
                "Producer Gate Export requires producer_emitted_gate_artifact mode.",
                "$.schema_version",
                {"observed_schema": schema, "acquisition_mode": request.acquisition_mode},
            )
        ]
    expected_stage = _EXPECTED_SOURCE_STAGE_BY_TRANSITION.get(choice)
    observed_stage = value.get("stage")
    if expected_stage and isinstance(observed_stage, str) and observed_stage != expected_stage:
        return [
            ServiceDiagnostic(
                "PG.UI.SOURCE_SCHEMA_TRANSITION_MISMATCH",
                "error",
                "Input stage does not match the selected transition.",
                "$.stage",
                {"transition_choice": choice, "expected_stage": expected_stage, "observed_stage": observed_stage},
            )
        ]
    return []


def _looks_like_project_gate_result(value: dict[str, Any]) -> bool:
    result_type = value.get("result_type")
    if isinstance(result_type, str) and result_type.startswith(("service_", "ui_")):
        return True
    if "engine_result" in value and "transition_choice" in value and "diagnostics" in value:
        return True
    return value.get("schema_version") in {"ev4-project-gate-ui-result.v1", "project-gate-service-result.v1"}


def _preflight_result(choice: str, diagnostics: list[ServiceDiagnostic]) -> dict[str, Any]:
    return {
        "schema_version": "ev4-project-gate-ui-result.v1",
        "result_type": "ui_preflight_result",
        "transition_choice": choice,
        "status": _status_from_diagnostics(diagnostics),
        "user_message_fa": "❌ پیش‌بررسی UI قبل از اجرای transition متوقف شد.",
        "next_action_fa": "ورودی، acquisition mode یا transition را طبق diagnostic اصلاح کن و دوباره اجرا کن.",
        "diagnostics": [diagnostic.to_dict() for diagnostic in diagnostics],
        "engine_result": None,
        "capabilities_snapshot": None,
        "download_filenames": {},
        "published_download_paths": [],
        "report_bundle": {},
        "output": None,
    }


def _status_from_diagnostics(diagnostics: list[ServiceDiagnostic]) -> str:
    severities = {diagnostic.severity for diagnostic in diagnostics}
    if "error" in severities:
        return "invalid"
    if "insufficient_evidence" in severities:
        return "insufficient_evidence"
    if "warning" in severities:
        return "repair_needed"
    return "accepted"


def _uploaded_path(uploaded_file: Any | None) -> str | None:
    if uploaded_file is None:
        return None
    if isinstance(uploaded_file, str):
        return uploaded_file
    name = getattr(uploaded_file, "name", None)
    return str(name) if name else None


def _clean_path(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _markdown_report(result: dict[str, Any]) -> str:
    guidance = build_operator_guidance(result)
    safe_json = _neutralize_markdown_fences(canonical_dumps(result))
    raw_diagnostics = _neutralize_markdown_fences(json.dumps(result.get("diagnostics", []), ensure_ascii=False, indent=2))
    lines = [
        "# گزارش Project Gate Operator Panel",
        "",
        f"status: `{result.get('status', 'invalid')}`",
        "",
        "## راهنمای عملیاتی",
        "",
        f"- خلاصه: {guidance.headline_fa}",
        f"- کجا متوقف شد؟ {guidance.where_stopped_fa}",
        f"- مشکل فعلی چیست؟ {guidance.current_problem_fa}",
        f"- آیا خروجی مرحله بعد ساخته شد؟ {guidance.output_state_fa}",
        f"- safe_to_continue: `{str(guidance.safe_to_continue).lower()}`",
        "",
        "### چه چیزی درست پیش رفت؟",
    ]
    lines.extend(f"- {item}" for item in guidance.passed_steps_fa)
    lines.extend(["", "### اقدام بعدی دقیق"])
    lines.extend(f"{index}. {action}" for index, action in enumerate(guidance.next_actions_fa, start=1))
    lines.extend(["", "## Raw diagnostics", "", "```json", raw_diagnostics, "```", "", "## Raw JSON result", "", "```json", safe_json, "```", ""])
    return "\n".join(lines)


def _neutralize_markdown_fences(value: str) -> str:
    return value.replace("```", "``\u200b`")


def _html_report(result: dict[str, Any]) -> str:
    escaped_json = json.dumps(result, ensure_ascii=False, indent=2)
    escaped_diagnostics = json.dumps(result.get("diagnostics", []), ensure_ascii=False, indent=2)
    return (
        '<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>Project Gate Report</title></head><body>'
        '<main lang="fa" dir="rtl"><h1>گزارش Project Gate Operator Panel</h1>'
        f'<p><strong>status:</strong> {bdi_ltr(result.get("status", "invalid"))}</p>'
        '<h2>Raw diagnostics</h2>'
        f'{ltr_code_block(escaped_diagnostics)}'
        '<h2>Raw JSON result</h2>'
        f'{ltr_code_block(escaped_json)}'
        '</main></body></html>'
    )


def _finalize(result: dict[str, Any], output_dir: str | Path | None) -> UiRunOutput:
    published = [str(path) for path in result.get("published_download_paths", []) if _existing_file(path)]
    report_directory: str | Path | None = output_dir
    if published:
        report_directory = str(Path(published[0]).parent)
    reports = render_download_artifacts(result, report_directory)
    downloads = published + [path for path in reports if path not in published]
    if not reports:
        result = deepcopy(result)
        result.setdefault("diagnostics", []).append(
            {
                "code": "PG.UI.REPORT_WRITE_FAILED",
                "severity": "error",
                "message": "نوشتن فایل‌های گزارش انجام نشد؛ لینک دانلود موفق نمایش داده نمی‌شود.",
                "path": "$.downloads",
                "details": {"next_action": "مجوز نوشتن output directory را بررسی کن."},
            }
        )
        result["status"] = "invalid"
    capability_payload = result.get("capabilities_snapshot") if isinstance(result.get("capabilities_snapshot"), dict) else load_capability_payload()
    return UiRunOutput(
        result=result,
        status_markdown=status_summary_markdown(result),
        diagnostics_rows=diagnostics_to_rows(result.get("diagnostics", [])),
        capability_rows=capability_rows_from_payload(capability_payload),
        json_preview=canonical_dumps(result),
        download_paths=downloads,
    )


def _existing_file(value: Any) -> bool:
    if not isinstance(value, (str, Path)) or not str(value).strip():
        return False
    try:
        return Path(value).is_file()
    except (OSError, ValueError, RuntimeError):
        return False
