from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import ServiceDiagnostic


@dataclass(frozen=True)
class ParsedJsonInput:
    value: Any
    diagnostics: list[ServiceDiagnostic]
    source: str


def parse_json_input(
    *,
    input_json_path: str | None = None,
    input_json_text: str | None = None,
    input_data: Any = None,
) -> ParsedJsonInput:
    """Parse UI-provided JSON without mutating caller-owned objects."""

    provided = [
        name
        for name, value in (
            ("file_path", input_json_path),
            ("json_text", input_json_text),
            ("dict", input_data),
        )
        if value is not None
    ]
    if not provided:
        return ParsedJsonInput(
            None,
            [
                ServiceDiagnostic(
                    "PG.SERVICE.JSON_INPUT_MISSING",
                    "error",
                    "A JSON file, pasted JSON text, or parsed JSON object is required for this check.",
                    "$",
                )
            ],
            "missing",
        )
    if len(provided) > 1:
        return ParsedJsonInput(
            None,
            [
                ServiceDiagnostic(
                    "PG.SERVICE.JSON_INPUT_AMBIGUOUS",
                    "error",
                    "Provide only one JSON input source: file path, pasted JSON text, or parsed object.",
                    "$",
                    {"sources": provided},
                )
            ],
            "missing",
        )

    if input_data is not None:
        return ParsedJsonInput(deepcopy(input_data), [], "dict")

    if input_json_text is not None:
        try:
            return ParsedJsonInput(json.loads(input_json_text), [], "json_text")
        except json.JSONDecodeError as exc:
            return ParsedJsonInput(
                None,
                [
                    ServiceDiagnostic(
                        "PG.SERVICE.MALFORMED_JSON",
                        "error",
                        "Pasted input is not valid JSON.",
                        "$",
                        {"line": exc.lineno, "column": exc.colno},
                    )
                ],
                "json_text",
            )

    assert input_json_path is not None
    try:
        text = Path(input_json_path).read_text(encoding="utf-8")
    except OSError as exc:
        return ParsedJsonInput(
            None,
            [
                ServiceDiagnostic(
                    "PG.SERVICE.FILE_READ_ERROR",
                    "error",
                    "JSON input file could not be read.",
                    "$.input_json_path",
                    {"error_type": type(exc).__name__, "path": input_json_path},
                )
            ],
            "file_path",
        )
    try:
        return ParsedJsonInput(json.loads(text), [], "file_path")
    except json.JSONDecodeError as exc:
        return ParsedJsonInput(
            None,
            [
                ServiceDiagnostic(
                    "PG.SERVICE.MALFORMED_JSON",
                    "error",
                    "JSON input file is not valid JSON.",
                    "$",
                    {"line": exc.lineno, "column": exc.colno, "path": input_json_path},
                )
            ],
            "file_path",
        )
