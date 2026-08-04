"""Project root + db import path setup for Streamlit Cloud and local runs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_DIR = ROOT / "db"


def ensure_paths() -> Path:
    root_s = str(ROOT)
    db_s = str(DB_DIR)
    if root_s not in sys.path:
        sys.path.insert(0, root_s)
    if db_s not in sys.path:
        sys.path.insert(0, db_s)
    return ROOT
