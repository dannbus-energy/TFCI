# ADR-0005: Publication is gated by the acceptance suite

Status: Accepted
Context: The 14-test gate currently guards the data layer manually.
Decision: The same gate runs in CI as a deployment blocker: a red gate
blocks deploy of payload artifacts and the hosted UI.
Consequences: The gate becomes release infrastructure.
