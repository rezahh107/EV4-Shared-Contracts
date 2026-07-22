from __future__ import annotations

import os


def pytest_configure(config):
    """Keep GitHub Actions logs concise without changing test execution."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        config.option.verbose = -1
