#!/usr/bin/env python3
"""Trusted Source Promoter (ADR-0004 Compliance).
Automatically promotes high-confidence, deterministic staging events to the 
append-only projects ledger, bypassing manual review for trusted APIs.
"""
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "db"))

DB_URL = "postgresql://tfci:tfci@127.0.0.1:5433/tfci"
engine = create_engine(DB_URL)

def main():
    print("[*] Scanning staging_events for trusted, high-confidence records...")
    
    with engine.begin() as conn: # begin() ensures automatic commit/rollback
        # 1. Fetch eligible staging events
        query = text("""
            SELECT staging_id, project_id, jurisdiction_slug, sector_slug, 
                   event_date, source_ids
            FROM staging_events
            WHERE confidence = 'high' 
              AND source_ids LIKE '%deterministic_registry%' 
              AND (blocking_reason IS NULL OR blocking_reason = '')
              AND project_id IS NOT NULL
        """)
        result = conn.execute(query)
        staged_projects = result.fetchall()
        
        if not staged_projects:
            print("✅ No new trusted projects to promote.")
            return
            
        print(f"[*] Found {len(staged_projects)} eligible projects. Promoting to ledger...")
        
        promoted_count = 0
        for row in staged_projects:
            try:
                # 2. Insert into the append-only projects ledger using ACTUAL schema columns
                # We use project_id as a fallback for project_name, and event_date for created_at
                conn.execute(text("""
                    INSERT INTO projects (project_id, jurisdiction_slug, sector_slug, project_name, capacity_unit, created_at)
                    VALUES (:project_id, :jurisdiction_slug, :sector_slug, :project_name, :capacity_unit, :created_at)
                    ON CONFLICT (project_id) DO NOTHING
                """), {
                    "project_id": row.project_id,
                    "jurisdiction_slug": row.jurisdiction_slug,
                    "sector_slug": row.sector_slug,
                    "project_name": row.project_id, # Fallback since staging lacks this column
                    "capacity_unit": "MW",          # Default assumption for power projects
                    "created_at": row.event_date or datetime.now().strftime("%Y-%m-%d")
                })
                
                # 3. Mark as approved in staging to prevent re-processing
                conn.execute(text("""
                    UPDATE staging_events 
                    SET blocking_reason = 'auto_approved_trusted_source'
                    WHERE staging_id = :staging_id
                """), {"staging_id": row.staging_id})
                
                promoted_count += 1
            except Exception as e:
                print(f"[-] Failed to promote {row.project_id}: {e}")
                conn.rollback() # Reset transaction state for the next iteration
                
        print(f"✅ Successfully promoted {promoted_count} trusted projects to the projects ledger.")
        print("👉 Note: To reflect in Total Active Capital, these projects must be aggregated into capital_registry.")

if __name__ == "__main__":
    main()
