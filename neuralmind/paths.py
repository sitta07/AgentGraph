"""Where studies and results live.

Order of precedence:

1. ``$NEURALMIND_HOME``, if set.
2. The source checkout, when running from the repository (it has ``studies/``).
3. The current working directory, for example after ``pip install neuralmind``.
"""

from __future__ import annotations

import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent


def home() -> Path:
    env = os.environ.get("NEURALMIND_HOME")
    if env:
        return Path(env).expanduser().resolve()
    if (_REPO / "studies").is_dir() and (_REPO / "neuralmind").is_dir():
        return _REPO
    return Path.cwd()


def results_dir() -> Path:
    return home() / "results"


def studies_dir() -> Path:
    return home() / "studies"
