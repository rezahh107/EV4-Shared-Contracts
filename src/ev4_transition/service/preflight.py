from __future__ import annotations

from dataclasses import replace
from typing import Any

from ev4_transition.io.secure_snapshot import SnapshotError

from .environment_preflight import validate_gate_request_environment
from .models import GateRequest, ServiceDiagnostic
from .preflight_core import (
    PreflightCheck,
    PreflightCheckStatus,
    PreflightResult,
    PreflightResultStatus,
    run_preflight as _run_core_preflight,
)
from .request_identity import build_gate_request_identity


def run_preflight(request: GateRequest) -> PreflightResult:
    """Run the single authoritative, read-only preflight for every adapter."""

    result = (
        validate_gate_request_environment(request)
        if request.acquisition_mode == "producer_emitted_gate_artifact"
        else _run_core_preflight(request)
    )
    try:
        identity = build_gate_request_identity(request)
    except SnapshotError as exc:
        return _blocked_identity_result(result, exc.code, str(exc), exc.details)
    except (OSError, ValueError, TypeError) as exc:
        return _blocked_identity_result(
            result,
            "PG.SERVICE.PREFLIGHT_IDENTITY_FAILED",
            "The exact request identity could not be computed during preflight.",
            {"error_type": type(exc).__name__},
        )
    return replace(
        result,
        request_fingerprint=identity.fingerprint if result.status == "ready" else None,
        source_identity=dict(identity.source_identity),
    )


def preflight_authorization_diagnostic(
    request: GateRequest,
    result: PreflightResult,
) -> ServiceDiagnostic | None:
    """Fail closed unless current preflight authorizes the exact request.

    ``service_immediate`` remains only as a compatibility name for the same-call
    Preflight → dispatch path. It no longer suppresses non-ready Preflight.
    ``validate_bundle`` is validation-only and may run diagnostically with warnings;
    it cannot publish an operational handoff.
    """

    if result.status != "ready":
        if str(request.transition_choice) == "validate_bundle" and result.status == "warnings":
            return None
        return ServiceDiagnostic(
            "PG.SERVICE.PREFLIGHT_NOT_READY",
            "error",
            "Authoritative preflight is not ready for the current request.",
            "$.preflight",
            {
                "preflight_status": result.status,
                "request_fingerprint": result.request_fingerprint,
            },
        )
    if request.preflight_mode == "service_immediate":
        # The fingerprint was computed from this exact immutable request in the same
        # call. This mode is no longer an authorization bypass.
        return None
    supplied = request.preflight_fingerprint
    if not supplied:
        return ServiceDiagnostic(
            "PG.SERVICE.PREFLIGHT_FINGERPRINT_REQUIRED",
            "error",
            "Execution requires the fingerprint produced by authoritative preflight.",
            "$.preflight_fingerprint",
        )
    if supplied != result.request_fingerprint:
        return ServiceDiagnostic(
            "PG.SERVICE.PREFLIGHT_FINGERPRINT_STALE",
            "error",
            "The current request differs from the request that passed preflight.",
            "$.preflight_fingerprint",
            {
                "supplied_fingerprint": supplied,
                "current_fingerprint": result.request_fingerprint,
            },
        )
    return None


def _blocked_identity_result(
    result: PreflightResult,
    code: str,
    message: str,
    details: dict[str, Any],
) -> PreflightResult:
    check = PreflightCheck(
        "request.identity.blocked",
        "هویت دقیق درخواست",
        "error",
        message,
        f"code={code}; details={details}",
        "ورودی source و مسیرهای درخواست را اصلاح کن و Preflight را دوباره اجرا کن.",
        "request_identity_failed",
    )
    return replace(
        result,
        status="blocked",
        checks=[*result.checks, check],
        summary_fa="Preflight مسدود است؛ هویت دقیق درخواست قابل تأیید نیست.",
        request_fingerprint=None,
    )


__all__ = [
    "PreflightCheck",
    "PreflightCheckStatus",
    "PreflightResult",
    "PreflightResultStatus",
    "preflight_authorization_diagnostic",
    "run_preflight",
    "validate_gate_request_environment",
]
