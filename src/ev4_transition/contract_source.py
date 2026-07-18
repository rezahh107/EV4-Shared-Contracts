from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ContractSource(Protocol):
    def read_bytes(self, repository: str, commit: str, path: str) -> bytes: ...


@dataclass(frozen=True)
class LocalCheckoutContractSource:
    repository_roots: dict[str, Path]

    def read_bytes(self, repository: str, commit: str, path: str) -> bytes:
        if repository not in self.repository_roots:
            raise FileNotFoundError(f"Missing specialist checkout for {repository}@{commit}.")

        root = self.repository_roots[repository]
        file_path = (root / path).resolve()
        root_resolved = root.resolve()
        if root_resolved not in file_path.parents and file_path != root_resolved:
            raise FileNotFoundError(f"Contract path escapes checkout root: {path}")

        # Real Git checkouts must resolve bytes from the declared immutable commit.
        # Reading the working tree would silently bind current bytes to a historical
        # commit and break the commit/hash identity invariant.
        if (root_resolved / ".git").exists():
            try:
                completed = subprocess.run(
                    ["git", "-C", str(root_resolved), "show", f"{commit}:{path}"],
                    check=False,
                    capture_output=True,
                )
            except OSError as exc:
                raise FileNotFoundError(
                    f"Unable to execute Git for pinned contract {repository}@{commit}:{path}."
                ) from exc
            if completed.returncode != 0:
                raise FileNotFoundError(
                    f"Unable to read pinned contract {repository}@{commit}:{path}."
                )
            return completed.stdout

        # Hermetic fixture directories used by unit tests are intentionally allowed
        # to provide direct bytes without pretending to be immutable Git checkouts.
        return file_path.read_bytes()
