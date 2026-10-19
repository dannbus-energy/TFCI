"""CLI smoke: compute rollup for one jurisdiction through the engine package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import TfciData, compute_rollup

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    d = TfciData(str(root / "data"))
    r = compute_rollup(d.sector_scores)
    slug = sys.argv[1] if len(sys.argv) > 1 else "greenland"
    print(slug, "->", r[slug])
