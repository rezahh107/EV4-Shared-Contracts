from __future__ import annotations

from ev4_transition.presentation.rtl import bdi_ltr, escape_html
from ev4_transition.service.preflight import PreflightCheck, PreflightResult

from .components import ltr_token


def preflight_result_html(result: PreflightResult) -> str:
    """Render a read-only preflight result as an RTL Persian checklist."""

    items = "".join(_check_html(check) for check in result.checks)
    first = next(
        (check for check in result.checks if check.status in {"error", "warning", "unknown"}),
        None,
    )
    actionable = ""
    if first is not None:
        action = first.next_action_fa or "diagnostic را بررسی و ورودی مؤثر را اصلاح کنید."
        actionable = (
            '<p class="ev4-warning"><strong>اولین مورد قابل اقدام:</strong> '
            f'{escape_html(first.message_fa)} — {escape_html(action)}</p>'
        )
    authorization = (
        "این preview آماده است، اما مجوز اجرای ماندگار ذخیره نمی‌شود؛ دکمه اصلی Preflight تازه اجرا می‌کند."
        if result.status == "ready"
        else "این وضعیت مجوز dispatch نمی‌دهد."
    )
    return "\n".join(
        [
            '<section lang="fa" dir="rtl" role="status" aria-live="polite" class="ev4-preflight-result">',
            "<h3>بررسی آماده‌سازی مسیرها / Preflight</h3>",
            f"<p><strong>وضعیت آماده‌سازی:</strong> {escape_html(result.summary_fa)}</p>",
            f'<p><span dir="ltr">preflight_status:</span> {bdi_ltr(result.status)} · <span dir="ltr">transition:</span> {bdi_ltr(result.transition_choice)}</p>',
            actionable,
            f'<p class="ev4-helper-block">{escape_html(authorization)}</p>',
            "<p class=\"ev4-helper-block\">Preflight اجرای کامل Project Gate نیست، repositoryها یا JSON را تغییر نمی‌دهد، و جایگزین hash/schema/validator checks اجرای واقعی Gate نیست.</p>",
            f'<ul class="ev4-preflight-list">{items}</ul>',
            "</section>",
        ]
    )


def preflight_diagnostic_rows(result: PreflightResult) -> list[list[str]]:
    """Expose non-success Preflight checks in the standard diagnostics table."""

    rows: list[list[str]] = []
    for check in result.checks:
        if check.status in {"ok", "not_required"}:
            continue
        rows.append(
            [
                ltr_token(check.id),
                ltr_token(check.status),
                ltr_token("$.preflight"),
                check.message_fa,
                "",
                check.next_action_fa or "",
            ]
        )
    return rows


def _check_html(check: PreflightCheck) -> str:
    icon = {"ok": "✓", "warning": "⚠️", "error": "❌", "not_required": "↷", "unknown": "؟"}.get(check.status, "؟")
    css_class = f"ev4-preflight-{escape_html(str(check.status))}"
    detail = f"<div><strong>جزئیات فنی:</strong> {bdi_ltr(check.technical_detail)}</div>" if check.technical_detail else ""
    classification = f"<div><strong>classification:</strong> {bdi_ltr(check.classification)}</div>" if check.classification else ""
    action = f"<div><strong>اقدام پیشنهادی:</strong> {escape_html(check.next_action_fa)}</div>" if check.next_action_fa else ""
    return (
        f'<li class="{css_class}">'
        f'<span class="ev4-preflight-icon">{icon}</span> '
        f'<strong>{escape_html(check.label_fa)}</strong>: {escape_html(check.message_fa)}'
        f"{detail}{classification}{action}</li>"
    )
