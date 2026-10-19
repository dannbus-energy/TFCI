#!/usr/bin/env python3
"""Bulk Ingestor for Structured Public Registries (e.g., Global Energy Monitor, World Bank).

Bypasses LLM extraction for already-structured data, mapping CSV rows directly 
to the staging_events table with high confidence (ADR-0003).

Usage:
  python tfci_app/agents/bulk_ingest_registry.py <path_to_csv> <source_name>
"""
import csv, sys, uuid
from pathlib import Path
import psycopg

# Add paths to import local modules
AGENTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENTS_DIR))

DSN = "postgresql://tfci:tfci@localhost:5433/tfci"

# Simple normalization maps (expand this dictionary as you add more sources)
COUNTRY_TO_SLUG = {
    "united states": "united-states",
    "united kingdom": "united-kingdom",
    "china": "china",
    "india": "india",
    "argentina": "argentina",
    "kosovo": "kosovo",
    "puerto rico": "puerto-rico",
    "faroe islands": "faroe-islands",
    "new caledonia": "new-caledonia",
    "niue": "niue"
}

FUEL_TO_SECTOR = {
    "solar": "utility-scale-renewables",
    "wind": "utility-scale-renewables",
    "hydro": "utility-scale-renewables",
    "coal": "fossil-fuels",
    "gas": "fossil-fuels",
    "grid": "grid-modernization",
    "transmission": "grid-modernization"
}

STATUS_TO_EVENT = {
    "operating": "commissioning",
    "construction": "construction_start",
    "announced": "announcement",
    "pre-permit development": "announcement",
    "cancelled": "cancellation",
    "shut down": "cancellation"
}

def normalize_slug(name):
    return str(name).lower().strip().replace(" ", "-").replace(".", "").replace("'", "")

def main():
    if len(sys.argv) < 3:
        print("Usage: python bulk_ingest_registry.py <csv_file> <source_name>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    source_name = sys.argv[2]
    
    if not Path(csv_file).exists():
        print(f"❌ Error: File {csv_file} not found.")
        sys.exit(1)

    print(f"[*] Starting bulk ingest from {csv_file}...")
    
    conn = psycopg.connect(DSN)
    inserted_count = 0
    skipped_count = 0
    
    with conn.cursor() as cur, open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            country_raw = row.get("Country", "").strip().lower()
            jurisdiction_slug = COUNTRY_TO_SLUG.get(country_raw, normalize_slug(country_raw))
            
            fuel_raw = row.get("Primary_Fuel", "").strip().lower()
            sector_slug = FUEL_TO_SECTOR.get(fuel_raw, normalize_slug(fuel_raw))
            
            status_raw = row.get("Status", "").strip().lower()
            event_type = STATUS_TO_EVENT.get(status_raw, "announcement")
            
            project_name = row.get("Project_Name", "Unknown Project").strip()
            if not project_name or project_name == "Unknown Project":
                skipped_count += 1
                continue
                
            project_id = f"{normalize_slug(source_name)}-{normalize_slug(project_name)}"
            staging_id = f"STG-{uuid.uuid4().hex[:8].upper()}"
            source_id = f"SRC-{source_name}-{uuid.uuid4().hex[:6].upper()}"
            
            year = row.get("Year", "").strip()
            event_date = f"{year}-01-01" if year and year.isdigit() else None
            date_precision = "year" if year else "unknown"
            
            capital_str = row.get("Capital_USD_M", "").replace(",", "").replace("$", "").strip()
            amount_local = float(capital_str) if capital_str else None
            
            try:
                cur.execute("""
                    INSERT INTO staging_events 
                    (staging_id, project_id, jurisdiction_slug, sector_slug, event_type, event_date, date_precision, amount_local, currency_code, source_ids, confidence, blocking_reason)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    staging_id, project_id, jurisdiction_slug, sector_slug, event_type,
                    event_date, date_precision, amount_local, "USD", source_id, "high", None
                ))
                inserted_count += 1
            except Exception as e:
                print(f"[-] Failed to insert {project_name}: {e}")
                conn.rollback()
                
        conn.commit()
        
    conn.close()
    print(f"✅ Successfully staged {inserted_count} projects in Postgres. ({skipped_count} skipped).")
    print("👉 Next step: Run your approval gate to promote these to the ledger.")

if __name__ == "__main__":
    main()
