#!/usr/bin/env python3
"""Batch Sweep Script (Phase 3).

Reads a CSV of target URLs, runs the Harvester to stage the event,
and immediately runs the Verification Agent to cross-check it.
Leaves all verified candidates in staging_events for the Human Approval Gate.

Usage:
  python tfci_app/agents/batch_sweep.py batch_targets.csv
"""
import csv
import subprocess
import re
import sys
from pathlib import Path

def run_pipeline(url, j_slug, s_slug):
    print(f"\n{'='*70}")
    print(f"PROCESSING: {url}")
    print(f"TARGET: {j_slug} | {s_slug}")
    print(f"{'='*70}")
    
    # 1. Harvest
    harvest_cmd = ["python", "tfci_app/agents/harvest_agent.py", url, j_slug, s_slug]
    harvest_res = subprocess.run(harvest_cmd, capture_output=True, text=True)
    print(harvest_res.stdout)
    
    if harvest_res.returncode != 0:
        print(f"[!] Harvest failed for {url}. Skipping.")
        print(harvest_res.stderr)
        return
        
    # Extract staging_id from harvest output
    match = re.search(r"staging_id: (STG-[A-F0-9]+)", harvest_res.stdout)
    if not match:
        print(f"[!] Failed to extract staging ID for {url}. Skipping.")
        return
        
    staging_id = match.group(1)
    print(f"[*] Harvest successful. Staging ID: {staging_id}")
    
    # 2. Verify
    print(f"[*] Passing {staging_id} to Verification Agent...")
    verify_cmd = ["python", "tfci_app/agents/verify_agent.py", staging_id]
    verify_res = subprocess.run(verify_cmd, capture_output=True, text=True)
    print(verify_res.stdout)
    
    if verify_res.returncode != 0:
        print(f"[!] Verification failed for {staging_id}.")
        print(verify_res.stderr)
        
    print(f"✅ Pipeline complete for {staging_id}. Ready for Human Approval Gate.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python tfci_app/agents/batch_sweep.py <targets.csv>")
        sys.exit(1)
        
    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"[!] File not found: {csv_path}")
        sys.exit(1)
        
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        targets = list(reader)
        
    print(f"[*] Starting batch sweep of {len(targets)} targets...")
    
    for i, row in enumerate(targets, 1):
        print(f"\n[ Target {i} of {len(targets)} ]")
        run_pipeline(row['url'], row['jurisdiction_slug'], row['sector_slug'])
        
    print(f"\n{'='*70}")
    print(f"🎉 BATCH SWEEP COMPLETE!")
    print(f"   {len(targets)} targets processed.")
    print(f"   Run `python tfci_app/agents/approve_staged.py <STG-ID>` to review.")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
