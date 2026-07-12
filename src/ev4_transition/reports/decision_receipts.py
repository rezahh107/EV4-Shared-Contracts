from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from ev4_transition.final_gate_authority import is_authoritative_final_gate_result
from ev4_transition.kernel_decision_dependencies import KERNEL_ACCEPTED_COMMIT, KERNEL_INTAKE_RESULT_SCHEMA_ID, KERNEL_REPOSITORY

ReceiptStatus = Literal["success", "warning", "blocked"]
REQUIRED_KERNEL_DECISION_TRACE_FIELDS = ("decision_family", "decision_card_ref", "selected_option", "rejected_options", "evidence_refs", "evidence_state", "consumer_stage")
_STRING_TRACE_FIELDS = {"decision_family", "decision_card_ref", "selected_option", "evidence_state", "consumer_stage"}
_LIST_TRACE_FIELDS = {"rejected_options", "evidence_refs"}
SUCCESS_RECEIPT_FA = "✅ این Gate دارای نتیجهٔ پذیرفته‌شدهٔ KROAD-011 از اجرای داخلی L2 روی Kernel پین‌شده است؛ رسید فقط نمایش می‌دهد و تصمیم یا evidence جدیدی ایجاد نمی‌کند."
WARNING_RECEIPT_FA = "⚠️ این Gate نتیجهٔ in-process و authoritative از اجرای Final Gate ندارد یا projection کامل lineage موجود نیست؛ دادهٔ JSON قابل‌نویسندگی به‌تنهایی gate-pass معتبر نیست."
BLOCKED_RECEIPT_FA = "⛔ Gate مسدود شد؛ نتیجهٔ KROAD-011 پذیرفته نشده یا evidence لازم کافی نیست و باید repair/reopen شود."
EXPLICIT_NON_CLAIMS = ("no_release_readiness_claim", "no_production_readiness_claim", "no_downstream_contract_enforcement_claim", "no_runtime_monitor_enforcement_claim", "no_project_gate_repair_authority_added")


@dataclass(frozen=True)
class KernelDecisionReceipt:
    status: ReceiptStatus
    message_fa: str
    trace_complete: bool
    missing_trace_fields: list[str]
    machine_trace_source: str | None
    authoritative_intake_accepted: bool
    authoritative_intake_source: str | None
    presentation_layer_only: bool = True
    source_of_truth: str = "in_process_authoritative_final_gate_result"
    schema_version: str = "project-gate-kernel-decision-receipt.v1"

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "status": self.status, "message_fa": self.message_fa, "trace_complete": self.trace_complete, "missing_trace_fields": list(self.missing_trace_fields), "machine_trace_source": self.machine_trace_source, "authoritative_intake_accepted": self.authoritative_intake_accepted, "authoritative_intake_source": self.authoritative_intake_source, "presentation_layer_only": self.presentation_layer_only, "source_of_truth": self.source_of_truth, "explicit_non_claims": list(EXPLICIT_NON_CLAIMS)}


def build_kernel_decision_receipt(result: dict[str, Any] | Any) -> KernelDecisionReceipt:
    trace, trace_source = _find_machine_trace(result)
    missing = missing_kernel_decision_trace_fields(trace)
    trace_complete = trace is not None and not missing
    final_gate_authoritative = _is_authoritative_final_gate_result(result)
    intake = result.get("kernel_decision_intake_result") if final_gate_authoritative else None
    intake_accepted = final_gate_authoritative and _is_authoritative_intake_accepted(intake)
    gate_status = str(result.get("status", "invalid")) if isinstance(result, dict) else "invalid"
    if gate_status == "accepted":
        if trace_complete and intake_accepted:
            return KernelDecisionReceipt("success", SUCCESS_RECEIPT_FA, True, [], trace_source, True, "$.kernel_decision_intake_result")
        return KernelDecisionReceipt("warning", WARNING_RECEIPT_FA, trace_complete, [] if trace_complete else missing, trace_source, intake_accepted, "$.kernel_decision_intake_result" if intake_accepted else None)
    return KernelDecisionReceipt("blocked", BLOCKED_RECEIPT_FA, trace_complete, [] if trace_complete else missing, trace_source, intake_accepted, "$.kernel_decision_intake_result" if intake_accepted else None)


def missing_kernel_decision_trace_fields(trace: Any) -> list[str]:
    if not isinstance(trace, dict):
        return list(REQUIRED_KERNEL_DECISION_TRACE_FIELDS)
    missing: list[str] = []
    for field in REQUIRED_KERNEL_DECISION_TRACE_FIELDS:
        value = trace.get(field)
        if field in _STRING_TRACE_FIELDS and not _valid_string(value):
            missing.append(field)
        elif field in _LIST_TRACE_FIELDS and not _valid_string_list(value):
            missing.append(field)
    return missing


def _find_machine_trace(result: Any) -> tuple[dict[str, Any] | None, str | None]:
    for label, keys in (("$.output.decision_lineage", ("output", "decision_lineage")), ("$.output.responsive_output.decision_lineage", ("output", "responsive_output", "decision_lineage"))):
        value = _get_path(result, keys)
        if isinstance(value, dict):
            return value, label
    return None, None


def _is_authoritative_final_gate_result(value: Any) -> bool:
    if not is_authoritative_final_gate_result(value):
        return False
    if value.get("schema_version") != "final-gate-result.v1" or value.get("result_type") != "final_evidence_gate" or value.get("gate_id") != "ev4-final-evidence-gate@1.0.0":
        return False
    required = value.get("accepted_requires")
    return isinstance(required, dict) and required.get("kernel_decision_intake_accepted") is True


def _is_authoritative_intake_accepted(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("schema_version") != KERNEL_INTAKE_RESULT_SCHEMA_ID or value.get("result_type") != "kernel_decision_intake" or value.get("status") != "accepted":
        return False
    pin = value.get("kernel_pin")
    if not isinstance(pin, dict) or pin.get("repository") != KERNEL_REPOSITORY or pin.get("accepted_commit") != KERNEL_ACCEPTED_COMMIT:
        return False
    required = value.get("accepted_requires")
    required_keys = ("kernel_pin_verified", "semantic_lock_verified", "intake_schema_valid", "packet_binding_valid", "l2_executed_all", "no_unsupported_claims", "result_schema_valid")
    if not isinstance(required, dict) or any(required.get(key) is not True for key in required_keys):
        return False
    packets = value.get("packet_results")
    if not isinstance(packets, list) or not packets or not all(isinstance(item, dict) and item.get("status") == "accepted" and item.get("l2_executed") is True for item in packets):
        return False
    counts = value.get("derived_counts")
    return isinstance(counts, dict) and counts.get("accepted_decision_count") == len(packets) and counts.get("rejected_decision_count") == 0 and counts.get("unresolved_decision_count") == 0


def _get_path(value: Any, keys: tuple[str, ...]) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _valid_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_valid_string(item) for item in value)
