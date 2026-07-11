from __future__ import annotations

from typing import Any


class _FinalGateAuthorityToken:
    def __deepcopy__(self, memo: dict[int, Any]) -> "_FinalGateAuthorityToken":
        return self


_AUTHORITY_TOKEN = _FinalGateAuthorityToken()


class AuthoritativeFinalGateResult(dict[str, Any]):
    """In-process Final Gate result carrying non-JSON authority state.

    JSON serialization intentionally drops the authority token. A deserialized or
    externally authored dictionary therefore cannot produce an authoritative
    success receipt without rerunning Final Gate.
    """

    def __init__(self, payload: dict[str, Any]) -> None:
        super().__init__(payload)
        self._authority_token = _AUTHORITY_TOKEN


def _authoritative_final_gate_result(payload: dict[str, Any]) -> AuthoritativeFinalGateResult:
    return AuthoritativeFinalGateResult(payload)


def is_authoritative_final_gate_result(value: Any) -> bool:
    return isinstance(value, AuthoritativeFinalGateResult) and getattr(value, "_authority_token", None) is _AUTHORITY_TOKEN
