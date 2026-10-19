#!/usr/bin/env python3
"""Human Approval Gate (Phase 3, Step 6) - HARDENED.

Idempotent: refuses to promote a staging event twice (ADR-0004).
Displays verification agent output before approval.
Always registers the project so ledger events are never orphans.

Usage:
  python tfci_app/agents/approve_staged.py STG-0010
"""
import sys
import uuid
from datetime import datetime, timezone
import psycopg

DSN = "postgresql://tfci:tfci@localhost:5433/tfci"

def main():
    if len(sys.argv) < 2:
        print("Usage: python tfci_app/agents/approve_staged.py <staging_id>")
        sys.exit(1)

    staging_id = sys.argv[1]
    conn = psycopg.connect(DSN)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT staging_id, project_id, jurisdiction_slug, sector_slug,
                   event_type, event_date, date_precision, amount_local,
                   currency_code, source_ids, confidence,
                   verification_notes, verified_confidence, promoted_event_id
            FROM staging_events WHERE staging_id = %s
        """, (staging_id,))
        row = cur.fetchone()

        if not row:
            print(f"[!] No staged event found for {staging_id}")
            sys.exit(1)

        (sid, proj_id, j_slug, s_slug, e_type, e_date, e_prec, amt, curr,
         src_ids, conf, v_notes, v_conf, promoted) = row

        # IDEMPOTENCY GUARD (ADR-0004)
        if promoted:
            print(f"[!] REFUSED: {sid} was already promoted as {promoted}.")
            print("    A staging event may enter the ledger exactly once.")
            conn.close()
            sys.exit(1)

        print("\n" + "=" * 60)
        print(" HUMAN APPROVAL GATE")
        print("=" * 60)
        print(f"Staging ID      : {sid}")
        print(f"Project         : {proj_id or 'Will be generated'}")
        print(f"Jurisdiction    : {j_slug}")
        print(f"Sector          : {s_slug}")
        print(f"Event Type      : {e_type}")
        print(f"Event Date      : {e_date} ({e_prec})")
        print(f"Amount          : {amt} {curr}")
        print(f"Source IDs      : {src_ids}")
        print(f"Harvest conf.   : {conf}")
        print("-" * 60)
        print(f"Verifier conf.  : {v_conf or 'NOT VERIFIED'}")
        print(f"Verifier notes  : {v_notes or 'Verification agent has not run on this event.'}")
        print("=" * 60)

        response = input("\nPromote this event to the governed ledger? (y/n): ").strip().lower()
        if response != 'y':
            print("[*] Approval denied. Event remains in staging_events.")
            conn.close()
            sys.exit(0)

        print("[*] Promoting to governed ledger...")

        # Always register the project so the event is never an orphan
        final_proj_id = proj_id or f"PRJ-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO projects (project_id, jurisdiction_slug, sector_slug,
                                  project_name, capacity_unit, created_at)
            VALUES (%s, %s, %s, %s, 'unknown', CURRENT_DATE)
            ON CONFLICT (project_id) DO NOTHING
        """, (final_proj_id, j_slug, s_slug, proj_id or f"Project {final_proj_id}"))

        event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        recorded_at = datetime.now(timezone.utc)
        capital_usd_bn = (float(amt) / 1_000_000_000) if amt else None

        cur.execute("""
            INSERT INTO ledger_events
            (event_id, project_id, event_type, event_date, event_date_precision,
             amount_local, currency_code, capital_usd_bn, capital_basis, capital_type,
             source_id, recorded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'estimated', 'capex', %s, %s)
        """, (event_id, final_proj_id, e_type, e_date, e_prec,
              amt, curr, capital_usd_bn, src_ids, recorded_at))

        # Mark as promoted -> gate can never fire twice for this staging row
        cur.execute("""
            UPDATE staging_events SET promoted_event_id = %s WHERE staging_id = %s
        """, (event_id, sid))

    conn.commit()
    conn.close()
    print(f"✅ SUCCESS: Event {event_id} appended to governed ledger.")
    print(f"   Staging row {sid} is now locked (promoted_event_id set).")

if __name__ == "__main__":
    main()
