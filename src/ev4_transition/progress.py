from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProgressEvent:
    event_type: str
    message: str
    status: str
    repo_path: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = {"event_type": self.event_type, "message": self.message, "status": self.status}
        if self.repo_path is not None:
            data["repo_path"] = self.repo_path
        if self.details:
            data["details"] = self.details
        return data


def emit_progress_event(sink: list[dict[str, Any]] | None, event: ProgressEvent, repo_root: str | Path | None = None) -> None:
    if sink is None:
        return
    data = event.to_dict()
    if repo_root is not None:
        data["repo_root"] = Path(repo_root).name
    sink.append(data)
