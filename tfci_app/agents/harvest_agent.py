#!/usr/bin/env python3
"""Automated Harvester Agent (Phase 3).

Fetches a URL, archives it, extracts structured event data via OpenRouter,
and stages it in Postgres for human approval (ADR-0004).

Usage:
  python tfci_app/agents/harvest_agent.py "https://example.com/news" "japan" "utility-scale-renewables"
"""
import json, sys, uuid
from pathlib import Path

# Add paths to import local modules
AGENTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENTS_DIR))
sys.path.insert(0, str(AGENTS_DIR.parent.parent))

from evidence_store import acquire
from openrouter_client import OpenRouterClient
import psycopg

DSN = "postgresql://tfci:tfci@localhost:5433/tfci"

SYSTEM_PROMPT = """You are an expert data extractor for the Transition Finance Credibility Index. 
Extract structured JSON from the provided text about a transition finance project.
Return ONLY valid JSON matching this exact schema. Do not include markdown formatting like ```json.
{
  "project_name": "string or null",
  "jurisdiction_slug": "string (lowercase, hyphenated, e.g., 'japan', 'united-kingdom') or null",
  "sector_slug": "string (e.g., 'utility-scale-renewables', 'grid-modernization', 'semiconductors') or null",
  "event_type": "string ('announcement', 'fid', 'construction_start', 'commissioning', 'cancellation', 'capex_revision') or null",
  "event_date": "string (YYYY-MM-DD) or null",
  "amount_local": number or null,
  "currency_code": "string (e.g., 'USD', 'EUR', 'JPY') or null",
  "confidence": "string ('high', 'medium', 'low')"
}
If a field cannot be confidently determined from the text, use null."""

def main():
    if len(sys.argv) < 4:
        print("Usage: python tfci_app/agents/harvest_agent.py <URL> <jurisdiction_slug> <sector_slug>")
        sys.exit(1)
    
    url = sys.argv[1]
    target_jurisdiction = sys.argv[2]
    target_sector = sys.argv[3]
    
    staging_id = f"STG-{uuid.uuid4().hex[:8].upper()}"
    print(f"[*] Starting harvest for staging_id: {staging_id}")
    
    # 1. Acquire and archive (ADR-0007)
    print("[*] Fetching and archiving source...")
    rec = acquire(url, staging_id)
    if rec["error"]:
        print(f"[!] Failed to acquire: {rec['error']}")
        sys.exit(2)
    
    print(f"    -> Archived to: {rec['archive_path']}")
    print(f"    -> SHA-256: {rec['sha256']}")
    
    # 2. LLM Extraction (ADR-0003: LLM proposes, never computes)
    print("[*] Extracting structured data via OpenRouter...")
    client = OpenRouterClient(max_calls=5)
    
    # Truncate text to avoid massive token bills, keeping the most relevant parts
    text_to_analyze = rec["plain_text"][:6000] 
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Target Jurisdiction: {target_jurisdiction}\nTarget Sector: {target_sector}\n\nText to analyze:\n{text_to_analyze}"}
    ]
    
    try:
        response = client.chat(messages, json_mode=True)
        # Clean up markdown if the model adds it despite instructions
        response = response.strip().removeprefix("```json").removesuffix("```").strip()
        extracted = json.loads(response)
        print("[*] Extraction successful:")
        print(json.dumps(extracted, indent=2))
    except Exception as e:
        print(f"[!] LLM extraction failed: {e}")
        sys.exit(2)
        
    # 3. Stage in Postgres (ADR-0004: Agents never write to the ledger)
    print("[*] Staging candidate event in Postgres...")
    conn = psycopg.connect(DSN)
    with conn.cursor() as cur:
        # Record the evidence source
        source_id = f"SRC-{staging_id}"
        cur.execute("""
            INSERT INTO evidence_sources (source_id, url, archive_url, content_hash, publisher, source_type, confidence)
            VALUES (%s, %s, %s, %s, 'agent-harvested', 'web', %s)
            ON CONFLICT (source_id) DO NOTHING
        """, (source_id, url, rec["archive_path"], rec["sha256"], extracted.get("confidence", "low")))
        
        # Insert into staging_events
        cur.execute("""
            INSERT INTO staging_events 
            (staging_id, project_id, jurisdiction_slug, sector_slug, event_type, event_date, date_precision, amount_local, currency_code, source_ids, confidence, blocking_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            staging_id,
            extracted.get("project_name"), # Temporarily using name as ID; gate will formalize
            extracted.get("jurisdiction_slug", target_jurisdiction),
            extracted.get("sector_slug", target_sector),
            extracted.get("event_type"),
            extracted.get("event_date"),
            "exact" if extracted.get("event_date") else "unknown",
            extracted.get("amount_local"),
            extracted.get("currency_code"),
            source_id,
            extracted.get("confidence", "low"),
            None
        ))
    conn.commit()
    conn.close()
    
    print(f"✅ Successfully staged {staging_id} in Postgres. Awaiting human approval gate.")

if __name__ == "__main__":
    main()
