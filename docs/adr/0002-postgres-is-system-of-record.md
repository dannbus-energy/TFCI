# ADR-0002: Postgres is the system of record; CSVs are transitional

Status: Accepted
Context: The governed dataset lives in versioned CSVs with a 14-test gate;
production needs concurrent access and transactions.
Decision: PostgreSQL 17 becomes the ledger system of record. CSVs remain
the transitional source of truth until the loader and gate prove parity;
full-refresh (drop/create/COPY) until Alembic migrations arrive. Scores are
NEVER computed in SQL.
Consequences: Two representations coexist temporarily; parity checks are
mandatory in CI until CSVs are retired.
