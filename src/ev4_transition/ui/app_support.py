from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

from ev4_transition.presentation.theme_tokens import THEME_TOKENS, css_custom_properties
from ev4_transition.runners.native_dialog import select_directory
from ev4_transition.runners.open_output_folder import open_directory
from ev4_transition.service import (
    PreparedAuthoritativeGateTransaction,
    effective_repository_fields,
    execute_authoritative_gate_transaction,
    prepare_authoritative_gate_transaction,
)

from .adapters import build_capability_rows, build_gate_request, ui_output_from_response
from .components import CAPABILITY_HEADERS, DIAGNOSTIC_HEADERS
from .operator_settings import load_settings, reset_settings, save_settings, settings_path
from .preflight_components import preflight_diagnostic_rows, preflight_result_html
from .source_preflight import classify_source_file
from .state import (
    WORKFLOW_LABELS_FA,
    OperatorWorkflowState,
    begin_workflow,
    block_workflow,
    complete_workflow,
    initial_workflow_state,
    invalidate_workflow,
    mark_running,
    operation_is_current,
    option_for_label,
    record_preview,
    transition_choices,
)

HEADER_WARNING_FA = (
    "این پنل gate runner است و Elementor، Responsive یا specialist repository را اجرا نمی‌کند؛ "
    "فقط authoritative Project Gate را با validator و publication تأییدشده اجرا می‌کند."
)
HEADER_HELPER_FA = (
    "فایل اصلی JSON را بارگذاری کنید، مسیر تشخیص‌داده‌شده و checkoutهای local را بازبینی کنید، سپس دکمه اصلی را بزنید. "
    "همان اقدام ابتدا Authoritative Project Gate و فقط در صورت ready بودن اجرای backend را انجام می‌دهد."
)
PREFLIGHT_HELPER_FA = (
    "این دکمه فقط preview تشخیصی Preflight است و مجوز اجرای ماندگار ذخیره نمی‌کند. "
    "وضعیت warnings مانند blocked مجوز dispatch نمی‌دهد."
)


@dataclass(frozen=True)
class PreparedUiOperation:
    operation_id: int
    input_revision: int
    acquisition_mode: str
    transaction: PreparedAuthoritativeGateTransaction


@dataclass(frozen=True)
class ExecutedUiOperation:
    operation_id: int
    input_revision: int
    acquisition_mode: str
    output: Any | None = None
    blocked: bool = False
    stale: bool = False
    failed: bool = False
    error_type: str | None = None


def operator_header_html() -> str:
    return f"""
<section lang="fa" dir="rtl" class="ev4-app ev4-rtl">
  <header class="ev4-header ev4-shell" aria-label="EV4 Project Gate local operator panel">
    <div class="ev4-header-kicker">Local Operator Panel</div>
    <div class="ev4-header-title-row">
      <h1 class="ev4-header-title"><bdi dir="ltr">EV4 Project Gate</bdi></h1>
      <span class="ev4-header-badge">authoritative gate runner</span>
    </div>
    <p class="ev4-header-subtitle">پنل محلی بررسی گذارها</p>
    <p class="ev4-warning">⚠️ {HEADER_WARNING_FA}</p>
    <p class="ev4-helper">{HEADER_HELPER_FA}</p>
  </header>
</section>
"""


def operator_gradio_theme(gr: Any) -> Any:
    light = THEME_TOKENS["light"]
    dark = THEME_TOKENS["dark"]
    return gr.themes.Base(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate",
        spacing_size="md",
        radius_size="lg",
        text_size="md",
        font=["Vazirmatn", "Vazir", "IRANSansX", "Tahoma", "system-ui", "sans-serif"],
        font_mono=["Cascadia Code", "JetBrains Mono", "Consolas", "monospace"],
    ).set(
        body_background_fill=light["surface.base"],
        body_background_fill_dark=dark["surface.base"],
        body_text_color=light["text.primary"],
        body_text_color_dark=dark["text.primary"],
        block_background_fill=light["surface.raised"],
        block_background_fill_dark=dark["surface.raised"],
        block_border_color=light["border.default"],
        block_border_color_dark=dark["border.default"],
        input_background_fill=light["input.bg"],
        input_background_fill_dark=dark["input.bg"],
        input_border_color=light["input.border"],
        input_border_color_dark=dark["input.border"],
        button_primary_background_fill=light["button.primary.bg"],
        button_primary_background_fill_dark=dark["button.primary.bg"],
        button_primary_background_fill_hover=light["button.primary.hover.bg"],
        button_primary_background_fill_hover_dark=dark["button.primary.hover.bg"],
        button_primary_text_color=light["button.primary.text"],
        button_primary_text_color_dark=dark["button.primary.text"],
        button_secondary_background_fill=light["button.secondary.bg"],
        button_secondary_background_fill_dark=dark["button.secondary.bg"],
        button_secondary_text_color=light["button.secondary.text"],
        button_secondary_text_color_dark=dark["button.secondary.text"],
        code_background_fill=light["code.bg"],
        code_background_fill_dark=dark["code.bg"],
    )


def operator_panel_css() -> str:
    return css_custom_properties() + """
    .gradio-container { color-scheme: light dark; background: var(--ev4-surface-base) !important; color: var(--ev4-text-primary) !important; font-family: var(--ev4-font-fa-ui); font-size: 16px; line-height: 1.7; }
    .ev4-app, .ev4-shell, .ev4-rtl, .ev4-rtl textarea, .ev4-rtl input { direction: rtl; text-align: right; font-family: var(--ev4-font-fa-ui); line-height: 1.75; letter-spacing: normal; }
    .ev4-shell { max-width: 1120px; margin: 0 auto 0.75rem; }
    .ev4-header, .ev4-section, .ev4-dataframe, .ev4-download, .ev4-status-content, .ev4-preflight-result { background: var(--ev4-surface-raised); border: 1px solid var(--ev4-border-default); border-radius: 16px; padding: 0.75rem; box-shadow: 0 14px 34px var(--ev4-shadow-raised); }
    .ev4-header { padding: 1.15rem 1.25rem; }
    body.dark .ev4-header, .dark .ev4-header, :root[data-theme="dark"] .ev4-header { background: linear-gradient(145deg, var(--ev4-surface-raised), var(--ev4-surface-overlay)) !important; color: var(--ev4-text-primary) !important; border-color: var(--ev4-border-default) !important; }
    @media (prefers-color-scheme: dark) { body:not(.light) .ev4-header { background: linear-gradient(145deg, var(--ev4-surface-raised), var(--ev4-surface-overlay)) !important; color: var(--ev4-text-primary) !important; } }
    .ev4-header-title-row { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: .65rem 1rem; }
    .ev4-header-title { margin: 0; color: var(--ev4-text-primary); }
    .ev4-header-kicker, .ev4-header-subtitle, .ev4-helper { color: var(--ev4-text-secondary); }
    .ev4-header-badge { color: var(--ev4-info); background: var(--ev4-info-bg); border-radius: 999px; padding: .18rem .55rem; }
    .ev4-warning { color: var(--ev4-status-warning-fg); background: var(--ev4-status-warning-bg); border-radius: 12px; padding: .6rem .75rem; font-weight: 650; }
    .ev4-ltr textarea, .ev4-ltr input, .ev4-ltr code, .ev4-ltr pre, code, pre { direction: ltr; text-align: left; unicode-bidi: isolate; font-family: var(--ev4-font-code); }
    .gradio-container input[type="radio"] { appearance: none; -webkit-appearance: none; inline-size: 1.1rem; block-size: 1.1rem; border: 2px solid var(--ev4-control-indicator-border) !important; border-radius: 999px; background: var(--ev4-control-indicator-bg) !important; }
    .gradio-container input[type="radio"]:checked { border-color: var(--ev4-control-indicator-checked-bg) !important; background: radial-gradient(circle, var(--ev4-control-indicator-checked-dot) 34%, transparent 36%), var(--ev4-control-indicator-checked-bg) !important; }
    .gradio-container input[type="radio"]:focus-visible { outline: 3px solid var(--ev4-control-indicator-focus-ring) !important; outline-offset: 3px; }
    .gradio-container button.primary, .gradio-container button[variant="primary"] { background: var(--ev4-button-primary-bg) !important; color: var(--ev4-button-primary-text) !important; font-weight: 700; }
    .gradio-container button.primary:hover, .gradio-container button[variant="primary"]:hover { background: var(--ev4-button-primary-hover-bg) !important; color: var(--ev4-button-primary-hover-text) !important; }
    .gradio-container button:not(.primary):not([variant="primary"]) { background: var(--ev4-button-secondary-bg) !important; color: var(--ev4-button-secondary-text) !important; }
    .gradio-container button:not(.primary):not([variant="primary"]):hover { background: var(--ev4-button-secondary-hover-bg) !important; color: var(--ev4-button-secondary-hover-text) !important; }
    .gradio-container :disabled, .gradio-container [aria-disabled="true"] { background: var(--ev4-disabled-bg) !important; color: var(--ev4-disabled-text) !important; cursor: not-allowed; opacity: 1 !important; }
    .ev4-classification { border-inline-start: 5px solid var(--ev4-info); }
    .ev4-status-card { background: var(--ev4-surface-raised); border: 1px solid var(--ev4-border-subtle); }
    .ev4-code, code, pre { background: var(--ev4-code-bg); }
    """


def operator_run_outputs(output: Any) -> tuple[Any, Any, Any, str, Any]:
    return output.status_markdown, output.diagnostics_rows, output.capability_rows, output.json_preview, output.download_paths


def workflow_state_html(state: OperatorWorkflowState) -> str:
    label = WORKFLOW_LABELS_FA[state.status]
    return (
        '<section class="ev4-status-content" lang="fa" dir="rtl" role="status" aria-live="polite">'
        '<h3>وضعیت جریان اجرا</h3>'
        f'<p><strong>{escape(label)}</strong> · <bdi dir="ltr">{escape(state.status)}</bdi></p>'
        f'<p>{escape(state.detail_fa)}</p>'
        f'<p><span dir="ltr">input_revision:</span> <bdi dir="ltr">{state.input_revision}</bdi> · '
        f'<span dir="ltr">operation_id:</span> <bdi dir="ltr">{state.operation_id}</bdi></p>'
        '</section>'
    )


def stale_preflight_html() -> str:
    return (
        '<section class="ev4-preflight-result" lang="fa" dir="rtl" role="status" aria-live="polite">'
        '<p><strong>stale:</strong> یک ورودی مؤثر تغییر کرد؛ preview یا نتیجه قبلی دیگر مجوز اجرا نیست.</p>'
        '</section>'
    )


def run_authoritative_preflight(
    selected_transition: str,
    selected_mode: str,
    pasted: str | None,
    uploaded: Any | None,
    project_gate: str | None,
    architect: str | None,
    ce: str | None,
    builder: str | None,
    responsive: str | None,
    kernel: str | None,
    output: str | None,
):
    """Compatibility helper for diagnostic-only Preflight preview."""

    request = build_gate_request(
        selected_transition,
        pasted_json=pasted,
        uploaded_file=uploaded,
        project_gate_repo_path=project_gate,
        architect_repo_path=architect,
        ce_repo_path=ce,
        builder_repo_path=builder,
        responsive_repo_path=responsive,
        kernel_repo_path=kernel,
        acquisition_mode=selected_mode,
        output_dir=output,
    )
    prepared = prepare_authoritative_gate_transaction(request)
    token = prepared.preflight.request_fingerprint if prepared.authorization_ready else None
    return prepared.preflight, token


def repository_field_affects_request(
    selected_transition: str,
    selected_mode: str,
    field_name: str,
) -> bool:
    option = option_for_label(selected_transition)
    return field_name in effective_repository_fields(option.service_choice, selected_mode)


def invalidate_preflight_state(
    state: OperatorWorkflowState | None = None,
    *,
    relevant: bool = True,
):
    """Compatibility wrapper returning the new explicit workflow invalidation state."""

    current = state or initial_workflow_state()
    updated = invalidate_workflow(current, relevant=relevant)
    return updated, {"interactive": not current.active}, stale_preflight_html(), None, {"interactive": False}


def _path_row(gr: Any, label: str, value: str):
    with gr.Row():
        textbox = gr.Textbox(label=label, value=value, elem_classes=["ev4-ltr"], scale=8)
        button = gr.Button("Browse…", scale=1)
    return textbox, button


def browse_directory(current: str | None) -> str:
    return select_directory(current, timeout_seconds=120.0)


def _save_settings_callback(project_gate, architect, ce, builder, responsive, kernel, output, transition, mode):
    path = save_settings(
        {
            "project_gate_repo_path": project_gate,
            "architect_repo_path": architect,
            "ce_repo_path": ce,
            "builder_repo_path": builder,
            "responsive_repo_path": responsive,
            "kernel_repo_path": kernel,
            "default_output_directory": output,
            "default_transition": transition,
            "default_acquisition_mode": mode,
        }
    )
    return f"✅ تنظیمات محلی ذخیره شد: `{path}`"


def _reset_settings_callback(current_state: OperatorWorkflowState):
    value = reset_settings()
    updated = invalidate_workflow(current_state, relevant=True, detail_fa="تنظیمات reset شد؛ نتیجه قبلی stale است.")
    return (
        value["project_gate_repo_path"],
        value["architect_repo_path"],
        value["ce_repo_path"],
        value["builder_repo_path"],
        value["responsive_repo_path"],
        value["kernel_repo_path"],
        value["default_output_directory"],
        value["default_transition"],
        value["default_acquisition_mode"],
        "تنظیمات به defaults بازگردانده شد.",
        updated,
        workflow_state_html(updated),
        stale_preflight_html(),
        None,
        None,
        None,
        {"interactive": False},
        {"interactive": not current_state.active},
    )


def open_output_folder(attempt_directory: str | None) -> str:
    try:
        if not attempt_directory or not str(attempt_directory).strip():
            return "پوشه خروجی معتبر هنوز ایجاد نشده است."
        directory = Path(str(attempt_directory)).resolve(strict=True)
        if not directory.is_dir() or not directory.name.startswith("run-"):
            return "پوشه خروجی معتبر وجود ندارد."
        open_directory(directory)
        return f"پوشه باز شد: `{directory}`"
    except Exception as exc:
        return f"باز کردن پوشه ممکن نشد: `{type(exc).__name__}`"


