"""Deterministic calculator package (architecture doc section 3, step 8).

Phase 0: re-exports the canonical engine from src/ so imports migrate gradually.
Phase 1: the file moves here proper; src/ becomes a thin shim.
"""
import importlib.util
from pathlib import Path

_ENGINE_SRC = Path(__file__).resolve().parents[2] / "src" / "tfci_engine.py"
_spec = importlib.util.spec_from_file_location("_tfci_engine_canonical", _ENGINE_SRC)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

TfciData = _mod.TfciData
compute_rollup = _mod.compute_rollup
compute_deployment = _mod.compute_deployment
compute_cell_ratios = _mod.compute_cell_ratios
HORIZONS = _mod.HORIZONS
band = _mod.band
