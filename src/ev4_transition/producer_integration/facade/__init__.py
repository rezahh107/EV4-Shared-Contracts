from __future__ import annotations

from typing import Any

from . import runtime as _runtime
from ..intake import intake_producer_export, transition_producer_export


def inspect_producer_handoff(*args: Any, **kwargs: Any) -> dict[str, Any]:
    _runtime.intake_producer_export = intake_producer_export
    return _runtime.inspect_producer_handoff(*args, **kwargs)


def execute_producer_handoff(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Preserve the public facade injection seams used by service tests."""

    _runtime.intake_producer_export = intake_producer_export
    _runtime.transition_producer_export = transition_producer_export
    return _runtime.execute_producer_handoff(*args, **kwargs)


def required_repository_fields(resolved_transition: str) -> tuple[str, ...]:
    return _runtime.required_repository_fields(resolved_transition)


__all__ = [
    "execute_producer_handoff",
    "inspect_producer_handoff",
    "intake_producer_export",
    "required_repository_fields",
    "transition_producer_export",
]
