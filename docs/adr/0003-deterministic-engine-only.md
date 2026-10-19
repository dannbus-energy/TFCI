ADR-0003: Scores are computed only by the deterministic engine
Status: Accepted
Context: LLMs and SQL could both derive scores; both would make the method
unreproducible or invisible. Furthermore, naive statistical filters (e.g., 
3-sigma bounds, historical maximum caps) penalize genuine structural breaks 
and leapfrogging, violating the core purpose of a transition index.
Decision: All score computation happens in the versioned pure-Python engine
package (no network, no clock, no randomness). SQL stores and queries; LLMs
stage and propose. Payloads are stamped with git SHA + engine version +
input ledger hash. The engine MUST NOT apply statistical anomaly filters that 
suppress unprecedented data; anomaly is a hypothesis requiring corroboration, 
not a penalty.
Consequences: Falsification is mechanically possible (recompute challenge);
methodology audits trace to code. Leapfrogging is preserved as a first-class signal.
