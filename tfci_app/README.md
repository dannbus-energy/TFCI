# TFCI Application Layer

Phase 0 scaffold per docs/TFCI_System_Architecture_v1.0.md.

```
engine/      deterministic calculator (re-export of src/tfci_engine.py; moves here in Phase 1)
pipelines/   gate runner (wraps src/tfci_acceptance_tests.py)
api/         FastAPI serving the governed payload
collectors/  harvest stubs (raw-archive + staging append; LLM extraction = Phase 3)
db/          generated Postgres schema + CSV loader
tasks.py     command hub (up / load / api / gate / check)
```

## Commands

```
pip install -r requirements.txt
python tasks.py up      # docker compose up -d (postgres 17 + pgvector, adminer :8080)
python tasks.py load    # regenerate schema from CSVs, load all tables, verify row counts
python tasks.py api      # uvicorn api.main:app --reload  (http://localhost:8000/docs)
python tasks.py gate    # re-run the 14-test acceptance gate against ../data
python tasks.py check   # re-run stdlib CSV integrity checks
```

## Rules of the house

1. Nothing here edits /data or /src. Data flows one way: CSVs -> Postgres -> API.
2. The gate gates everything. `python tasks.py gate` must be green before any publish step.
3. LLMs never write to the ledger (ADR-0004). collectors/ stages; humans approve.
