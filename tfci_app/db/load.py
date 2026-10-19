#!/usr/bin/env python3
"""Load CSVs -> Postgres via row-by-row INSERT (v2).

Why not COPY: source CSVs contain bare carriage returns in some text fields
(PostgreSQL rejects them in CSV mode). Python's csv module parses them
correctly; at <= ~5k rows per table, INSERT performance is a non-issue.

Full-refresh (drop/create/insert). Fails loudly on zero-row tables.
"""
import csv, re, sys
from pathlib import Path

try:
    import psycopg
except ImportError:
    sys.exit("pip install 'psycopg[binary]' first")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from schema_gen import build_schema  # noqa: E402

DSN = "postgresql://tfci:tfci@localhost:5433/tfci"

def csv_row_count(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return max(0, sum(1 for _ in csv.reader(f)) - 1)

def norm_col(c, i):
    c = (c or "").strip()
    return '"%s"' % (re.sub(r"\W+", "_", c.lower()) or "col_%d" % i)

def main():
    schema, mapping = build_schema(HERE.parents[1] / "data")
    (HERE / "schema.sql").write_text(schema, encoding="utf-8")
    print("schema.sql regenerated (%d tables)" % len(mapping))
    bad = []
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
            conn.commit()
        for tbl, p in sorted(mapping.items()):
            with open(p, newline="", encoding="utf-8-sig") as f:
                rdr = csv.reader(f)
                header = next(rdr)
                cols = ", ".join(norm_col(c, i) for i, c in enumerate(header))
                ph = ", ".join(["%s"] * len(header))
                sql = 'INSERT INTO "%s" (%s) VALUES (%s)' % (tbl, cols, ph)
                n = 0
                with conn.cursor() as cur, conn.transaction():
                    for row in rdr:
                        if not any(cell.strip() for cell in row):
                            continue  # skip blank lines
                        vals = list(row) + [None] * (len(header) - len(row))
                        vals = [v if v != "" else None for v in vals[:len(header)]]
                        cur.execute(sql, vals)
                        n += 1
            with conn.cursor() as cur:
                cur.execute('SELECT COUNT(*) FROM "%s"' % tbl)
                db_n = cur.fetchone()[0]
            print("  loaded %-28s %6d rows (csv: %d)" % (tbl, db_n, csv_row_count(p)))
            if db_n == 0 and csv_row_count(p) > 0:
                bad.append(tbl)
    if bad:
        sys.exit("ZERO-ROW TABLES: %s" % ", ".join(bad))
    print("done. adminer: http://localhost:8080")

if __name__ == "__main__":
    main()
