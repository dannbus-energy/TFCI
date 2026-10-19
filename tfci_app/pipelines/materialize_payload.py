#!/usr/bin/env python3
"""Payload Materializer (ADR-0008)."""
import json, hashlib, subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "db"))

from db_loader import TfciDataDB, engine
from sqlalchemy import text
from tfci_engine import compute_rollup, compute_deployment

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = ROOT / "data" / "TFCI_frontend_payload_v2.json"

def get_git_sha():
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except Exception: return "no-git-repo"

def get_ledger_hash(data: TfciDataDB):
    df = data.sector_scores.sort_values(["jurisdiction_slug", "sector_slug"])
    return hashlib.sha256(df.to_csv(index=False).encode("utf-8")).hexdigest()

def main():
    print("1. Loading governed data from Postgres...")
    data = TfciDataDB()
    
    print("2. Computing deterministic rollups and deployment scores...")
    rollup = compute_rollup(data.sector_scores)
    deploy = compute_deployment(data.sector_scores, data.sectors)
    
    print("3. Aggregating real capital (Registry), pillars, and vetoes...")
    capital_registry, total_active_capital, pillar_averages, active_vetoes = {}, 0.0, {}, {}
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT cr.jurisdiction_slug, COALESCE(cr.provisional_capital_usd_bn, cr.commissioned_capital_usd_bn) as active_cap,
            cr.evidence_class, CURRENT_DATE as capital_as_of_date, cr.methodology, cr.lifecycle_status, cr.estimability,
            COALESCE(j.is_offshore_jurisdiction, FALSE) as is_offshore
            FROM capital_registry cr
            LEFT JOIN jurisdictions j ON cr.jurisdiction_slug = j.jurisdiction_slug
        """))
        for row in result.fetchall():
            j_slug, cap, e_class, as_of, method, status, estimability, is_offshore = row
            cap_float = float(cap) if cap else 0.0
            capital_registry[j_slug] = {
                "amount": round(cap_float, 2), "evidenceClass": e_class or "LEGACY_BASELINE",
                "asOf": str(as_of) if as_of else None, "method": method,
                "provisionalStatus": status, "estimability": estimability or "estimable", "isOffshore": is_offshore
            }
            if not is_offshore:
                total_active_capital += cap_float
            
        result_pillars = conn.execute(text("""
            SELECT jurisdiction_slug, ROUND(AVG(p1_subscore)) as p1, ROUND(AVG(p2_subscore)) as p2,
            ROUND(AVG(p3_subscore)) as p3, ROUND(AVG(p4_subscore)) as p4, ROUND(AVG(p5_subscore)) as p5
            FROM sector_scores GROUP BY jurisdiction_slug
        """))
        for row in result_pillars.fetchall():
            pillar_averages[row[0]] = {"regulatory": int(row[1] or 0), "grid": int(row[2] or 0), "capital": int(row[3] or 0), "execution": int(row[4] or 0), "survival": int(row[5] or 0)}
            
        result_vetoes = conn.execute(text("""
            SELECT jurisdiction_slug, veto_pillar_slug, COUNT(*) as sector_count,
            COALESCE(MAX(legacy_drag), 'structural veto flagged') as reason
            FROM sector_scores WHERE has_veto = TRUE AND veto_pillar_slug IS NOT NULL
            GROUP BY jurisdiction_slug, veto_pillar_slug
        """))
        for row in result_vetoes.fetchall():
            active_vetoes.setdefault(row[0], []).append({"pillar": row[1] or "unknown", "sector_count": row[2], "reason": row[3]})

    total_active_capital = round(total_active_capital, 2)
    print(f"   -> Aggregated Expected Discharged Capital: ${total_active_capital}bn")
    
    print("4. Constructing governed payload...")
    jurisdictions_payload = []
    for _, j_row in data.jurisdictions.iterrows():
        slug = j_row["jurisdiction_slug"]
        coverage_row = data.ledger_coverage[data.ledger_coverage["jurisdiction_slug"] == slug]
        ledger_status = coverage_row["ledger_status"].iloc[0] if not coverage_row.empty else "not_yet_swept"
        j_cap_data = capital_registry.get(slug, {})
        
        jurisdictions_payload.append({
            "slug": slug, "name": j_row["name"], "iso2": j_row["iso2"], "region": j_row["region"],
            "sweepCadence": j_row["sweep_cadence"], "recomputeTier": j_row["recompute_tier"],
            "credibility": rollup.get(slug, {}).get("overall"), "credibilityBand": rollup.get(slug, {}).get("band"),
            "deployment": deploy.get(slug, {}).get("score"), "deploymentBand": deploy.get(slug, {}).get("band"), 
            "ledgerStatus": ledger_status,
            "isOffshore": j_cap_data.get("isOffshore", False),
            "capital": {
                "activeCapitalUsdBn": j_cap_data.get("amount", 0.0) if j_cap_data.get("amount", 0.0) > 0 else None,
                "asOf": j_cap_data.get("asOf"), "evidenceClass": j_cap_data.get("evidenceClass", "LEGACY_BASELINE"),
                "method": j_cap_data.get("method", "legacy baseline"), "provisionalStatus": j_cap_data.get("provisionalStatus", "not_created"),
                "estimability": j_cap_data.get("estimability", "estimable")
            },
            "pillars": pillar_averages.get(slug), "vetoes": active_vetoes.get(slug, [])
        })

    for rank_key, score_key in (("credibilityRank", "credibility"), ("deploymentRank", "deployment")):
        ordered = sorted([j for j in jurisdictions_payload if j.get(score_key) is not None], key=lambda x: (-x[score_key], x["slug"]))
        for i, j in enumerate(ordered, 1): j[rank_key] = i
    jurisdictions_payload.sort(key=lambda x: x.get("credibilityRank") or 999)

    total_verified = sum(j["capital"]["activeCapitalUsdBn"] for j in jurisdictions_payload if j["capital"]["activeCapitalUsdBn"] and j["capital"]["evidenceClass"] == "A_verified")
    total_registry = sum(j["capital"]["activeCapitalUsdBn"] for j in jurisdictions_payload if j["capital"]["activeCapitalUsdBn"])
    verified_ratio = round((total_verified / total_registry * 100), 1) if total_registry > 0 else 0.0
    
    # DYNAMIC MATH: No more hardcoded 19/208
    total_jurisdictions = len(jurisdictions_payload)
    swept_jurisdictions = sum(1 for j in jurisdictions_payload if str(j.get("ledgerStatus", "")).startswith("swept"))
    sweep_coverage = round((swept_jurisdictions / total_jurisdictions * 100), 1) if total_jurisdictions > 0 else 0.0
    
    print(f"   -> Verified Coverage Ratio: {verified_ratio}%")
    print(f"   -> Sweep Coverage Ratio: {sweep_coverage}% ({swept_jurisdictions} swept / {total_jurisdictions} total)")

    payload = {
        "metadata": {
            "git_sha": get_git_sha(), "engine_version": "1.0.0-claim-primitive",
            "input_ledger_hash": get_ledger_hash(data), "as_of": datetime.now(timezone.utc).isoformat(),
            "active_capital_usd_bn": total_active_capital, "verified_coverage_ratio": verified_ratio,
            "credibility_gap": round(100 - verified_ratio, 1), "sweep_coverage_ratio": sweep_coverage,
            "execution_gap": round(100 - sweep_coverage, 1)
        },
        "jurisdictions": jurisdictions_payload
    }

    print("5. Writing stamped artifact...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
        
    print("🎉 ADR-0008 COMPLIANT PAYLOAD MATERIALIZED!")
    print(f"   Path: {OUTPUT_FILE}")
    print(f"   Git SHA: {payload['metadata']['git_sha']}")
    print(f"   Ledger Hash: {payload['metadata']['input_ledger_hash'][:16]}...")
    print(f"   Expected Discharged Capital: ${total_active_capital}bn")
    print(f"   Jurisdictions: {len(jurisdictions_payload)}")

if __name__ == "__main__":
    main()
