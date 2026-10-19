#!/usr/bin/env python3
"""Postgres-aware data loader for the deterministic engine.
Replaces CSV loading while keeping the engine's pure-Python logic intact (ADR-0003).
"""
import pandas as pd
from sqlalchemy import create_engine

DSN = "postgresql://tfci:tfci@localhost:5433/tfci"
engine = create_engine(DSN)

class TfciDataDB:
    """Mimics the original TfciData CSV loader, but fetches from Postgres via SQLAlchemy."""
    def __init__(self):
        # Fetch dimensions and facts into Pandas DataFrames (matching CSV structure)
        self.jurisdictions = pd.read_sql("SELECT * FROM jurisdictions", engine)
        self.sectors = pd.read_sql("SELECT * FROM sectors", engine)
        self.pillars = pd.read_sql("SELECT * FROM pillars", engine)
        self.sourcing_policy = pd.read_sql("SELECT * FROM sourcing_policy", engine)
        
        self.sector_scores = pd.read_sql("SELECT * FROM sector_scores", engine)
        self.projects = pd.read_sql("SELECT * FROM projects", engine)
        self.ledger_events = pd.read_sql("SELECT * FROM ledger_events", engine)
        self.ledger_coverage = pd.read_sql("SELECT * FROM ledger_coverage", engine)
        self.veto_ledger = pd.read_sql("SELECT * FROM veto_ledger", engine)
        self.score_history = pd.read_sql("SELECT * FROM score_history", engine)
        self.evidence_sources = pd.read_sql("SELECT * FROM evidence_sources", engine)
        self.score_evidence = pd.read_sql("SELECT * FROM score_evidence", engine)
        self.fx_rates = pd.read_sql("SELECT * FROM fx_rates", engine)
        self.exception_log = pd.read_sql("SELECT * FROM exception_log", engine)
