ADR-0004: Agents never write to the ledger; Claims are the primitive
Status: Accepted
Context: Collection will be LLM-assisted via OpenRouter; governance requires
human accountability. The unit of account is no longer an "event" but a 
"Claim" (a dated, scoped obligation with a discharge criterion).
Decision: Agents write only to staging_events, which are then canonicalized 
into the append-only `claims` ledger. A human approval gate (LangGraph 
interrupt) is required for material changes to existing claims or claims 
flagged with estimability='low_confidence'. Routine, high-confidence 
corroborations of existing claims may be auto-promoted.
Consequences: Slower ingestion by design for novel claims; clean chain of 
custody. The system tracks Promise-Performance, not just raw announcements.
