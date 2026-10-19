# ADR-0007: Raw evidence artifacts are immutable and content-addressed

Status: Accepted
Context: Chain of custody requires the original bytes of every source.
Decision: Raw captures are stored verbatim, keyed by SHA-256, in the local
vault and mirrored to R2. Nothing downstream may alter them.
Consequences: Storage grows monotonically; deletion is a governance event.
