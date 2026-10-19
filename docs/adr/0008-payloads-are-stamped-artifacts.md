# ADR-0008: Payloads are immutable, versioned, stamped artifacts

Status: Accepted
Context: Consumers need to know exactly which data and method produced a
number.
Decision: Every materialized payload embeds {git_sha, engine_version,
input_ledger_hash, as_of} and is archived immutably (R2) before serving.
Consequences: Bit-level reproducibility of publications.
