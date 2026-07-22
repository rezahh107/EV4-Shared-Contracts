from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Literal

from ev4_transition.presentation.status_mapping import ProjectGateStatus, normalize_status, presentation_for_status


OperatorWorkflowStatus = Literal[
    "not_checked",
    "checking",
    "blocked",
    "stale",
    "running",
    "completed",
    "failed",
]


@dataclass(frozen=True)
class OperatorWorkflowState:
    """Per-session UI workflow state, separate from the final Gate result status."""

    status: OperatorWorkflowStatus = "not_checked"
    input_revision: int = 0
    operation_id: int = 0
    operation_revision: int | None = None
    preview_revision: int | None = None
    detail_fa: str = "هنوز Authoritative Preflight اجرا نشده است."

    @property
    def active(self) -> bool:
        return self.status in {"checking", "running"}


WORKFLOW_LABELS_FA: dict[OperatorWorkflowStatus, str] = {
    "not_checked": "آماده بررسی",
    "checking": "در حال Authoritative Preflight",
    "blocked": "اجرا مسدود شد",
    "stale": "نتیجه نامعتبر شده است",
    "running": "در حال اجرای Project Gate",
    "completed": "تراکنش کامل شد",
    "failed": "تراکنش با خطای کنترل‌شده متوقف شد",
}


@dataclass(frozen=True)
class TransitionOption:
    transition_id: str
    service_choice: str
    label_en: str
    label_fa: str
    wired: bool
    required_json: bool
    pending_reason_fa: str = ""


TRANSITION_OPTIONS: tuple[TransitionOption, ...] = (
    TransitionOption(
        "validate_stage_evidence_bundle",
        "validate_bundle",
        "Validate Stage Evidence Bundle",
        "اعتبارسنجی Stage Evidence Bundle",
        True,
        True,
    ),
    TransitionOption(
        "architect_to_ce",
        "architect_to_ce",
        "Architect → CE",
        "Architect → CE",
        True,
        True,
    ),
    TransitionOption(
        "ce_to_builder",
        "ce_to_builder",
        "CE → Builder",
        "CE → Builder",
        True,
        True,
        "guarded/fail-closed؛ نیازمند شواهد واقعی و checkout محلی owner",
    ),
    TransitionOption(
        "builder_to_responsive",
        "builder_to_responsive",
        "Builder → Responsive",
        "Builder → Responsive",
        True,
        True,
        "guarded/fail-closed؛ نیازمند شواهد واقعی و checkout محلی owner",
    ),
    TransitionOption(
        "final_evidence_gate",
        "final_gate",
        "Final Evidence Gate",
        "Final Evidence Gate",
        True,
        True,
        "guarded/fail-closed؛ نیازمند شواهد واقعی و checkout محلی owner",
    ),
    TransitionOption(
        "inspect_capabilities",
        "inspect_capabilities",
        "Inspect Capabilities",
        "بازبینی قابلیت‌ها",
        True,
        False,
    ),
)


STATUS_MEANINGS_FA: dict[ProjectGateStatus, str] = {
    "accepted": "این بررسی در همین محدوده پذیرفته شد.",
    "invalid": "ساختار یا قرارداد نامعتبر است.",
    "insufficient_evidence": "شواهد کافی نیست.",
    "repair_needed": "بسته قابل فهم است ولی نیاز به اصلاح دارد.",
}

STATUS_NEXT_ACTION_FA: dict[ProjectGateStatus, str] = {
    "accepted": "نتیجه را فقط در محدوده همین بررسی استفاده کن؛ این تولید-ready یا frontend-ready نیست.",
    "invalid": "JSON، schema identity، مسیرها، hashها و diagnosticهای خطادار را اصلاح کن و دوباره اجرا کن.",
    "insufficient_evidence": "شواهد گمشده را از owner repository یا validator رسمی تهیه کن و دوباره اجرا کن.",
    "repair_needed": "موارد قابل اصلاح را از Diagnostics بردار و بسته را دوباره بساز.",
}


def initial_workflow_state() -> OperatorWorkflowState:
    return OperatorWorkflowState()


def begin_workflow(state: OperatorWorkflowState) -> OperatorWorkflowState:
    return replace(
        state,
        status="checking",
        operation_id=state.operation_id + 1,
        operation_revision=state.input_revision,
        detail_fa="ورودی فعلی freeze شد و Authoritative Preflight در حال اجرا است.",
    )


def invalidate_workflow(
    state: OperatorWorkflowState,
    *,
    relevant: bool,
    detail_fa: str = "یک ورودی مؤثر تغییر کرد؛ نتیجه قبلی دیگر مجوز اجرا نیست.",
) -> OperatorWorkflowState:
    if not relevant:
        return state
    next_status: OperatorWorkflowStatus = "stale" if (
        state.preview_revision is not None
        or state.status != "not_checked"
    ) else "not_checked"
    return replace(
        state,
        status=next_status,
        input_revision=state.input_revision + 1,
        preview_revision=None,
        detail_fa=detail_fa,
    )


def record_preview(
    state: OperatorWorkflowState,
    preflight_status: str,
) -> OperatorWorkflowState:
    status: OperatorWorkflowStatus = "blocked" if preflight_status != "ready" else "not_checked"
    detail = (
        "Preflight preview آماده است؛ برای اجرا باید دکمه اصلی را بزنید تا fingerprint جدید در همان تراکنش صادر شود."
        if preflight_status == "ready"
        else "Preflight preview مجوز اجرا نداد؛ diagnosticهای نمایش‌داده‌شده را اصلاح کنید."
    )
    return replace(
        state,
        status=status,
        preview_revision=state.input_revision,
        detail_fa=detail,
    )


def operation_is_current(
    state: OperatorWorkflowState,
    operation_id: int,
    operation_revision: int,
) -> bool:
    return (
        state.operation_id == operation_id
        and state.input_revision == operation_revision
        and state.operation_revision == operation_revision
    )


def mark_running(
    state: OperatorWorkflowState,
    operation_id: int,
    operation_revision: int,
) -> OperatorWorkflowState:
    if not operation_is_current(state, operation_id, operation_revision):
        return replace(
            state,
            status="stale",
            detail_fa="ورودی هنگام Preflight تغییر کرد؛ backend اجرا نشد.",
        )
    return replace(
        state,
        status="running",
        detail_fa="Preflight مجوز داد؛ backend اکنون همان درخواست را دوباره اعتبارسنجی می‌کند.",
    )


def complete_workflow(
    state: OperatorWorkflowState,
    operation_id: int,
    operation_revision: int,
    *,
    failed: bool = False,
) -> OperatorWorkflowState:
    if not operation_is_current(state, operation_id, operation_revision):
        return replace(
            state,
            status="stale",
            detail_fa="یک نتیجه قدیمی نادیده گرفته شد چون ورودی یا عملیات فعال تغییر کرده بود.",
        )
    return replace(
        state,
        status="failed" if failed else "completed",
        detail_fa=(
            "تراکنش با خطای کنترل‌شده متوقف شد؛ جزئیات را بررسی کنید."
            if failed
            else "تراکنش تمام شد؛ نتیجه نهایی Gate و diagnostics را بررسی کنید."
        ),
    )


def block_workflow(
    state: OperatorWorkflowState,
    operation_id: int,
    operation_revision: int,
    *,
    detail_fa: str,
) -> OperatorWorkflowState:
    if not operation_is_current(state, operation_id, operation_revision):
        return replace(state, status="stale", detail_fa="نتیجه Preflight قدیمی شد و اجرا نشد.")
    return replace(state, status="blocked", detail_fa=detail_fa)


def transition_choices() -> list[str]:
    return [option.label_en for option in TRANSITION_OPTIONS]


def option_for_label(label: str | None) -> TransitionOption:
    if label:
        for option in TRANSITION_OPTIONS:
            if label in {option.label_en, option.label_fa, option.transition_id, option.service_choice}:
                return option
    return TRANSITION_OPTIONS[0]


def normalize_ui_status(status: Any) -> ProjectGateStatus:
    try:
        return normalize_status(str(status))
    except ValueError:
        return "invalid"


def status_label_fa(status: Any) -> str:
    normalized = normalize_ui_status(status)
    presentation = presentation_for_status(normalized)
    return f"{presentation.icon} {presentation.persian_label} / {normalized}"
