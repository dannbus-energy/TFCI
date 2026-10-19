#!/usr/bin/env python3
"""Capital Aggregator (Claim-Based).
Calculates 'Expected Discharged Capital' by weighting claim promise values 
against their discharge_status and the jurisdiction's historical P5 (Execution Velocity).
"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "db"))

DB_URL = "postgresql://tfci:tfci@127.0.0.1:5433/tfci"
engine = create_engine(DB_URL)

# Deterministic discharge weights (Version 1.0)
# These represent the baseline probability of a claim reaching full discharge 
# based purely on its current lifecycle status, before jurisdictional P5 adjustment.
DISCHARGE_WEIGHTS = {
    'pending': 0.20,
    'partially_discharged': 0.60,
    'fully_discharged': 1.00,
    'defaulted': 0.00,
    'not_estimable': 0.00
}

def main():
    print("[*] Aggregating Expected Discharged Capital from claims ledger...")
    
    with engine.begin() as conn:
        # 1. Fetch jurisdiction P5 (Execution Velocity) scores to use as a risk multiplier
        p5_scores = {}
        p5_result = conn.execute(text("""
            SELECT jurisdiction_slug, AVG(p5_subscore) as avg_p5 
            FROM sector_scores GROUP BY jurisdiction_slug
        """))
        for row in p5_result.fetchall():
            # Normalize P5 (0-100) to a multiplier (0.5 to 1.5)
            # A P5 of 50 yields a 1.0x multiplier.
            p5_scores[row.jurisdiction_slug] = 0.5 + (float(row.avg_p5) / 100.0) if row.avg_p5 else 1.0

        # 2. Fetch all active claims
        claims_result = conn.execute(text("""
            SELECT claim_id, jurisdiction_slug, promise_value, promise_unit, discharge_status 
            FROM claims WHERE promise_unit = 'USD_bn' AND promise_value IS NOT NULL
        """))
        
        capital_by_jurisdiction = {}
        
        for row in claims_result.fetchall():
            j_slug = row.jurisdiction_slug
            value = float(row.promise_value)
            status = row.discharge_status or 'pending'
            
            # Apply deterministic weights
            base_weight = DISCHARGE_WEIGHTS.get(status, 0.20)
            jurisdiction_multiplier = p5_scores.get(j_slug, 1.0)
            
            # Expected Discharged Capital
            expected_cap = value * base_weight * jurisdiction_multiplier
            
            capital_by_jurisdiction[j_slug] = capital_by_jurisdiction.get(j_slug, 0.0) + expected_cap

        # 3. Upsert into capital_registry
        updated_count = 0
        for j_slug, est_cap in capital_by_jurisdiction.items():
            conn.execute(text("""
                INSERT INTO capital_registry 
                (jurisdiction_slug, provisional_capital_usd_bn, evidence_class, methodology, lifecycle_status, estimability)
                VALUES (:j_slug, :est_cap, 'B_agent_estimated', 'expected_discharged_capital_v1', 'active', 'estimable')
                ON CONFLICT (jurisdiction_slug) 
                DO UPDATE SET 
                    provisional_capital_usd_bn = :est_cap,
                    methodology = 'expected_discharged_capital_v1'
            """), {"j_slug": j_slug, "est_cap": round(est_cap, 4)})
            updated_count += 1
            
        print(f"✅ Updated Expected Discharged Capital for {updated_count} jurisdictions.")
        print(" Next step: Run materialize_payload.py to see the risk-weighted capital totals.")

if __name__ == "__main__":
    main()
