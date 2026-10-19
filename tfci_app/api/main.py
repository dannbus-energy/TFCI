"""TFCI FastAPI - serves the governed payload (Phase 1 shape).

Contract mirrors data/TFCI_frontend_payload_v2.json - the UI never computes.
"""
import csv
import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent.parent
PAYLOAD_V2 = ROOT / "data" / "TFCI_frontend_payload_v2.json"
SCORES_CSV = ROOT / "data" / "sector_scores.csv"

app = FastAPI(
    title="TFCI API",
    version="0.1.0",
    description="Transition Finance Credibility Index - governed payload server.",
)

@lru_cache(maxsize=1)
def payload():
    return json.loads(PAYLOAD_V2.read_text(encoding="utf-8"))

@lru_cache(maxsize=1)
def sector_scores():
    with SCORES_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

@app.get("/health")
def health():
    jz = payload()["jurisdictions"]
    return {"status": "ok", "jurisdictions": len(jz), "source": PAYLOAD_V2.name}

@app.get("/v1/meta")
def meta():
    p = payload()
    jz = p["jurisdictions"]
    # Expose ALL metadata from the governed payload
    meta_data = p.get("metadata", {})
    return {
        "jurisdictions": len(jz),
        "sectors": 20,
        "pillars": 5,
        "execution_ratio_live": meta_data.get("execution_ratio_live", 0),
        "execution_ratio_mean": meta_data.get("sweep_coverage_ratio"),  # Alias for backwards compat
        "credibility_gap_mean": meta_data.get("credibility_gap"),  # Alias for backwards compat
        "active_capital_usd_bn": meta_data.get("active_capital_usd_bn"),
        "verified_coverage_ratio": meta_data.get("verified_coverage_ratio"),
        "credibility_gap": meta_data.get("credibility_gap"),
        "sweep_coverage_ratio": meta_data.get("sweep_coverage_ratio"),
        "execution_gap": meta_data.get("execution_gap"),
        "bands": {
            "high": len([j for j in jz if j["credibilityBand"] == "HIGH"]),
            "medium": len([j for j in jz if j["credibilityBand"] == "MEDIUM"]),
            "low": len([j for j in jz if j["credibilityBand"] == "LOW"])
        }
    }

@app.get("/v1/jurisdictions")
def jurisdictions(region=None, band=None, limit: int = Query(default=250, le=250)):
    jz = payload()["jurisdictions"]
    
    # ENFORCE PROVISIONAL BASELINE: Guarantee no None values for new jurisdictions
    for j in jz:
        j["credibility"] = j.get("credibility") or 50
        j["credibilityBand"] = j.get("credibilityBand") or "MEDIUM"
        j["deployment"] = j.get("deployment") or 50
        j["deploymentBand"] = j.get("deploymentBand") or "MEDIUM"
    
    out = [j for j in jz
           if (region is None or j["region"] == region)
           and (band is None or j["credibilityBand"] == band)]
    out.sort(key=lambda j: -(j["credibility"] or 0))
    return out[:limit]

@app.get("/v1/jurisdictions/{slug}")
def jurisdiction(slug: str):
    j = next((x for x in payload()["jurisdictions"] if x["slug"] == slug), None)
    if j is None:
        raise HTTPException(404, "unknown jurisdiction: %s" % slug)
    rows = [r for r in sector_scores() if r["jurisdiction_slug"] == slug]
    return {"jurisdiction": j, "sector_scores": rows}

@app.get("/v1/sectors")
def sectors():
    seen = {}
    for r in sector_scores():
        seen.setdefault(r["sector_slug"], 0)
        seen[r["sector_slug"]] += 1
    return [{"sector_slug": s, "rows": n} for s, n in sorted(seen.items())]


# --- v1.1 flags endpoint (added by phase1_build_v1.py; marker: TFciFlagsRoute) ---
from fastapi.responses import FileResponse

@app.get("/v1/flags/{iso2}")
def flag(iso2: str):
    p = ROOT / "assets" / "flags" / (iso2.lower() + ".svg")
    if not p.is_file():
        raise HTTPException(404, "no flag for %s" % iso2)
    return FileResponse(p, media_type="image/svg+xml")
