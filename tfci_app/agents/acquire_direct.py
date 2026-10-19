"""acquire_direct.py - analyst-directed source acquisition.

An analyst who LOCATES a source by hand (e.g. the White & Case release)
can have the machine archive, hash, and quote-verify it - the same machine
checks agents get, never bypassed. Registered in agent_sources so the
approval gate's --source-url / --capital-source-url can reference it.

Usage:
  python tfci_app/agents/acquire_direct.py STG-0010 "URL" "classification" "exact verbatim quote"
  classification: independent | primary
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg

AGENTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENTS_DIR))
sys.path.insert(0, str(AGENTS_DIR.parent.parent))
from tfci_app.db.load import DSN
from evidence_store import acquire, quote_in_text

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    staging_id, url, classification = sys.argv[1], sys.argv[2], sys.argv[3]
    quote = sys.argv[4] if len(sys.argv) > 4 else ""
    if classification not in ("independent", "primary"):
        sys.exit("classification must be independent or primary")

    rec = acquire(url, staging_id)
    verified = bool(rec["plain_text"]) and quote_in_text(quote, rec["plain_text"])
    print("http_status=%s  error=%s" % (rec["http_status"], rec["error"]))
    print("sha256=%s" % rec["sha256"])
    print("archive=%s" % rec["archive_path"])
    print("quote_verified=%s" % verified)
    if rec["error"]:
        sys.exit(2)

    conn = psycopg.connect(DSN)
    now = datetime.now(timezone.utc) + timezone.utc.utcoffset(None)  # naive ok via default
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO agent_sources
                       (staging_id, verdict_ts, url, title, classification,
                        quote, quote_verified, sha256, archive_path,
                        http_status, error)
                       VALUES (%s, now(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT (staging_id, verdict_ts, url) DO NOTHING""",
                    (staging_id, url, "[analyst-directed]", classification,
                     quote, verified, rec["sha256"], rec["archive_path"],
                     rec["http_status"], rec["error"]))
    conn.commit()
    conn.close()
    print("recorded in agent_sources as [analyst-directed].")
    if not verified:
        print("NOTE: quote did NOT verify - gate will refuse this URL. "
              "Copy the quote exactly as it appears in the archived text.")
