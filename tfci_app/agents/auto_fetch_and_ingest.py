#!/usr/bin/env python3
"""Zero-Touch Orchestrator Agent (Massive Scale - WB REST API)."""
import sys
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT / "data" / "ingest"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_world_bank_energy():
    print("[*] Fetching World Bank Active Energy/Climate Projects (REST API)...")
    # Use the dedicated Projects REST API
    url = "https://projectsapi.worldbank.org/rest/v1/project"
    params = {
        "format": "json",
        "active_project": "Y",
        "size": 500,
        "fields": "id,project_name,countryshortname,totalamt,boardapprovaldate,status,sector"
    }
    headers = {"User-Agent": "Mozilla/5.0 (TFCI/1.0)"}
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        projects = data.get("projects", [])
        print(f"    -> Retrieved {len(projects)} World Bank projects.")
        
        normalized = []
        for p in projects:
            if not isinstance(p, dict): continue # Skip if it's a string
            
            claim_id = f"wb-{p.get('id', 'unknown')}"
            country = p.get("countryshortname", "unknown").lower().replace(" ", "-")
            sector = "utility-scale-renewables" 
            amt = float(p.get("totalamt", 0)) / 1e9 if p.get("totalamt") else 0.0
            date_str = p.get("boardapprovaldate", "")
            date = date_str[:10] if date_str else datetime.now().strftime("%Y-%m-%d")
            status = p.get("status", "").lower()
            
            if "closed" in status or "cancelled" in status: discharge = "defaulted"
            elif "active" in status or "implementing" in status: discharge = "partially_discharged"
            else: discharge = "pending"

            normalized.append({
                "claim_id": claim_id, "jurisdiction_slug": country, "sector_slug": sector,
                "claim_type": "capital_commitment", "promise_value": amt, "promise_unit": "USD_bn",
                "claim_date": date, "discharge_status": discharge,
                "provenance_tier": "tier_1_regulatory", "estimability": "estimable"
            })
        return normalized
    except Exception as e:
        print(f"    -> [!] World Bank fetch failed: {e}")
        return []

def main():
    print(f"=== 🤖 Zero-Touch Orchestrator Agent ({datetime.now().isoformat()}) ===")
    all_claims = fetch_world_bank_energy()
    if not all_claims:
        print("⚠️ No new projects fetched.")
        return

    df = pd.DataFrame(all_claims)
    csv_path = OUTPUT_DIR / "massive_wb_ingest.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Normalized {len(df)} claims to {csv_path}")

if __name__ == "__main__":
    main()
