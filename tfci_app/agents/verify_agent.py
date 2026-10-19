#!/usr/bin/env python3
"""Verification Agent (Phase 3).

Cross-checks a staged event against live web search results using OpenRouter's
online search capability. Updates the staging record with verification notes
and an adjusted confidence score for the Human Approval Gate (ADR-0004).

Usage:
  python tfci_app/agents/verify_agent.py STG-90DF70A8
"""
import json, sys
from pathlib import Path

# Add paths to import local modules
AGENTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENTS_DIR))
sys.path.insert(0, str(AGENTS_DIR.parent.parent))

from openrouter_client import OpenRouterClient
import psycopg

DSN = "postgresql://tfci:tfci@localhost:5433/tfci"

SYSTEM_PROMPT = """You are a rigorous financial data verification agent for the Transition Finance Credibility Index.
Your task is to cross-check a proposed transition finance event against live web search results.
Look for corroborating evidence of the project name, location, event type, and especially the capital amount.
Return ONLY valid JSON matching this exact schema. Do not include markdown formatting.
{
  "corroborated": boolean,
  "discrepancies": "string describing any conflicts, or null if none",
  "updated_confidence": "high" | "medium" | "low",
  "verification_notes": "concise summary of findings and sources"
}"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python tfci_app/agents/verify_agent.py <staging_id>")
        sys.exit(1)
    
    staging_id = sys.argv[1]
    
    conn = psycopg.connect(DSN)
    with conn.cursor() as cur:
        # 1. Fetch the staged event
        cur.execute("""
            SELECT project_id, jurisdiction_slug, sector_slug, event_type, 
                   amount_local, currency_code, confidence
            FROM staging_events WHERE staging_id = %s
        """, (staging_id,))
        row = cur.fetchone()
        
        if not row:
            print(f"[!] No staged event found for {staging_id}")
            sys.exit(1)
            
        proj_id, j_slug, s_slug, e_type, amt, curr, orig_conf = row
        
        print(f"[*] Verifying staged event: {staging_id}")
        print(f"    Target: {proj_id} | {j_slug} | {s_slug} | {e_type}")
        print(f"    Proposed Amount: {amt} {curr}")
        
        # 2. Construct Search Query
        search_query = f"{proj_id} {j_slug} {s_slug} {e_type} capital investment amount {curr}"
        print(f"[*] Searching web for: '{search_query}'")
        
        # 3. Call OpenRouter with Live Search
        client = OpenRouterClient(max_calls=5)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Proposed Event Data:\n- Project: {proj_id}\n- Jurisdiction: {j_slug}\n- Sector: {s_slug}\n- Event Type: {e_type}\n- Amount: {amt} {curr}\n\nPlease search the live web and verify this data."}
        ]
        
        try:
            # online=True triggers OpenRouter's web search capability
            response = client.chat(messages, json_mode=True, online=True)
            response = response.strip().removeprefix("```json").removesuffix("```").strip()
            verification = json.loads(response)
            
            print("\n[*] Verification Results:")
            print(f"    Corroborated: {verification.get('corroborated')}")
            print(f"    Discrepancies: {verification.get('discrepancies') or 'None'}")
            print(f"    Updated Confidence: {verification.get('updated_confidence')}")
            print(f"    Notes: {verification.get('verification_notes')}")
            
            # 4. Update Staging Record
            cur.execute("""
                UPDATE staging_events
                SET verification_notes = %s,
                    verified_confidence = %s
                WHERE staging_id = %s
            """, (
                verification.get('verification_notes'),
                verification.get('updated_confidence', orig_conf),
                staging_id
            ))
            conn.commit()
            print(f"\n✅ Successfully updated {staging_id} with verification data.")
            
        except Exception as e:
            print(f"[!] Verification failed: {e}")
            # Record the failure in the DB so the human gate knows
            cur.execute("""
                UPDATE staging_events
                SET verification_notes = %s
                WHERE staging_id = %s
            """, (f"Verification agent error: {str(e)[:200]}", staging_id))
            conn.commit()
            sys.exit(2)
            
    conn.close()

if __name__ == "__main__":
    main()
