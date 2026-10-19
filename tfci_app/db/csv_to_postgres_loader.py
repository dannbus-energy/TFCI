#!/usr/bin/env python3
"""Loads all CSVs from data/ into Postgres (ADR-0002 Transition)."""
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# Match the connection string from docker-compose.yml (mapped to host port 5433)
DB_URL = "postgresql://tfci:tfci@127.0.0.1:5433/tfci"
engine = create_engine(DB_URL)

data_dir = Path("data")
csv_files = list(data_dir.glob("*.csv"))

print(f"[*] Found {len(csv_files)} CSVs to load...")

for csv_path in csv_files:
    table_name = csv_path.stem
    try:
        # Read CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # Clean column names (replace spaces with underscores, lowercase)
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        
        # Load to Postgres (replace existing data for a clean full-refresh)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"    -> Loaded {len(df)} rows into '{table_name}'")
    except Exception as e:
        print(f"    -> [!] Failed to load {table_name}: {e}")

print("✅ CSV to Postgres transition complete.")
