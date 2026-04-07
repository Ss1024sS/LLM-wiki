"""Convenience wrapper — forwards to the real bootstrap script."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REAL_SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "knowledge-system-bootstrap" / "scripts" / "bootstrap_knowledge_system.py"

if not REAL_SCRIPT.exists():
    print(f"Error: cannot find {REAL_SCRIPT}", file=sys.stderr)
    sys.exit(1)

os.execv(sys.executable, [sys.executable, str(REAL_SCRIPT)] + sys.argv[1:])
