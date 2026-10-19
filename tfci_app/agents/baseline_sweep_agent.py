#!/usr/bin/env python3
"""Zero-Touch Baseline Sweep Agent."""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "db"))

DB_URL = "postgresql://tfci:tfci@127.0.0.1:5433/tfci"
engine = create_engine(DB_URL)

def main():
    print("[*] Starting Zero-Touch Baseline Sweep...")
    with engine.begin() as conn:
        coverage_query = text("SELECT jurisdiction_slug, sector_slug FROM ledger_coverage")
        coverage_rows = conn.execute(coverage_query).fetchall()
        total_cells = len(coverage_rows)
        swept_count = 0
        print(f"[*] Scanning {total_cells} jurisdiction-sector cells...")
        
        for row in coverage_rows:
            j_slug = row.jurisdiction_slug
            s_slug = row.sector_slug
            
            claims_query = text("""
                SELECT COUNT(*) as claim_count, 
                       SUM(CASE WHEN discharge_status = 'fully_discharged' THEN 1 ELSE 0 END) as discharged_count
                FROM claims 
                WHERE jurisdiction_slug = :j_slug AND sector_slug = :s_slug
            """)
            claim_stats = conn.execute(claims_query, {"j_slug": j_slug, "s_slug": s_slug}).fetchone()
            claim_count = claim_stats.claim_count or 0
            discharged_count = claim_stats.discharged_count or 0
            
            if claim_count == 0: status = 'swept_baseline_empty'
            elif discharged_count > 0: status = 'swept_active_claims'
            else: status = 'swept_pending_claims'
                
            conn.execute(text("""
                UPDATE ledger_coverage 
                SET ledger_status = :status
                WHERE jurisdiction_slug = :j_slug AND sector_slug = :s_slug
            """), {"status": status, "j_slug": j_slug, "s_slug": s_slug})
            swept_count += 1
            
        print(f"✅ Baseline Sweep Complete. {swept_count}/{total_cells} cells marked as swept.")

if __name__ == "__main__":
    main()
