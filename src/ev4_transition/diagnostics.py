from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Severity = Literal["error", "warning", "info", "insufficient_evidence"]


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str
    path: str = "$"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = {"severity": self.severity, "code": self.code, "message": self.message, "path": self.path}
        if self.details:
            data["details"] = self.details
        return data


def diagnostic(severity: Severity, code: str, message: str, path: str = "$", **details: Any) -> Diagnostic:
    return Diagnostic(severity, code, message, path, details)


def aggregate_status(items: list[Diagnostic]) -> str:
    if any(i.severity == "error" for i in items):
        return "invalid"
    if any(i.severity == "insufficient_evidence" for i in items):
        return "insufficient_evidence"
    return "valid"


def persian_summary(status: str) -> str:
    return {
        "valid": "بسته معتبر است و شواهد لازم وجود دارد.",
        "accepted": "بسته پذیرفته شد و خروجی مرحله بعد ساخته شد.",
        "invalid": "بسته نامعتبر است و باید اصلاح شود.",
        "failed": "انتقال انجام نشد چون خطای قطعی وجود دارد.",
        "insufficient_evidence": "شواهد کافی نیست؛ سیستم چیزی را حدس نمی‌زند و مالک اصلاح هنوز قطعی نیست."
    }.get(status, f"وضعیت: {status}")
