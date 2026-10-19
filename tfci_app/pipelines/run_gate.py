#!/usr/bin/env python3
"""Runs the canonical acceptance gate (src/tfci_acceptance_tests.py) via subprocess."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    rc = subprocess.call([sys.executable, str(ROOT / "src" / "tfci_acceptance_tests.py"),
                          str(ROOT / "data")])
    sys.exit(rc)
