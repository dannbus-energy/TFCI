#!/usr/bin/env python3
"""Harvest stub: fetch a URL, archive raw bytes, register a staged candidate.

Implements the collection-plane skeleton (architecture doc section 3, steps 0-5).
LLM extraction (step 3) is a stub - Phase 3 wires OpenRouter.

Usage:
  python harvest_stub.py https://example.com/press-release greenland critical-minerals
"""
import csv, hashlib, sys
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
EVIDENCE = DATA / "evidence"
STAGING = DATA / "staging_events.csv"

def next_source_id():
    ids = []
    if EVIDENCE.exists():
        for p in EVIDENCE.glob("SRC-*_*.md"):
            head = p.name.split("_")[0]
            if "-" in head and head.split("-")[1].isdigit():
                ids.append(int(head.split("-")[1]))
    return "SRC-%04d" % ((max(ids) + 1) if ids else 100)

def fetch_and_stage(url, jurisdiction, sector):
    sid = next_source_id()
    resp = requests.get(url, timeout=30, headers={"User-Agent": "TFCI-harvest/0.1"})
    resp.raise_for_status()
    raw = resp.content
    digest = hashlib.sha256(raw).hexdigest()
    EVIDENCE.mkdir(exist_ok=True)
    vault = EVIDENCE / ("%s_%s.md" % (sid, hashlib.sha256(url.encode()).hexdigest()[:8]))
    vault.write_text(
        "# raw capture\n\nsource_id: %s\nurl: %s\nfetched: %s\nsha256: %s\n\n---\n%s\n"
        % (sid, url, date.today().isoformat(), digest, resp.text[:5000]),
        encoding="utf-8")
    # TODO Phase 3: LLM extraction of {event date, capital, actors, claim} via OpenRouter.
    row = {
        "staging_id": "STG-%s" % digest[:12],
        "jurisdiction_slug": jurisdiction,
        "sector_slug": sector,
        "source_id": sid,
        "archive_url": str(vault),
        "content_hash": digest,
        "claim_date": date.today().isoformat(),
        "capital_usd_bn": "",
        "evidence_class": "raw_staged",
        "review_status": "awaiting_adjudication",
        "notes": "harvest_stub v1; LLM extraction pending Phase 3",
    }
    new = not STAGING.exists()
    with STAGING.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)
    print("staged:", row["staging_id"], "->", vault.name)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: harvest_stub.py URL jurisdiction_slug sector_slug")
    fetch_and_stage(sys.argv[1], sys.argv[2], sys.argv[3])
