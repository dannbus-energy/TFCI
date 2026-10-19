# Revision protocol (v0.1)

1. Methodology changes are versions, never mutations: methodology/vX.Y.md.
2. Every verdict and publication stamps the methodology and sweep-policy
   versions that produced it.
3. Back-casts: on a methodology change, recompute history under the new
   version and store both series in score_history with methodology_version.
4. Golden fixtures (tfci_app/agents/test_regression.py) must pass before any
   prompt, model, or policy change ships.
5. Exceptions (exception_log) are triaged each sweep cycle; promoted rules
   fold into the next methodology version with effective date.
