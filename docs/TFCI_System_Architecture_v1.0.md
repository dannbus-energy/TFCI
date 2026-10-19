# TFCI System Architecture v1.0

**Status:** Proposed
**Date:** 2026-09-28
**Scope:** End-to-end architecture for the Transition Finance Credibility Index as a production application — from evidence collection to hosted dashboard.

---

## 0. Document intent and method

This document defines the target architecture using the **C4 model** (system context → containers → components) plus a data-lineage map and a phased delivery roadmap. Each significant decision should be captured as a short **Architecture Decision Record (ADR)** in `docs/adr/` (one decision per file: Status / Context / Decision / Consequences). This document is the map; the ADRs are the why.

**First principles (non-negotiable):**

1. **Deterministic core, stochastic periphery.** LLMs propose; arithmetic decides. No AI output ever touches a governed score without passing a human approval gate and the deterministic calculator.
2. **Append-only.** The ledger never edits history. Corrections are new events that supersede, with lineage.
3. **Falsifiable.** Every published score must be re-derivable by a third party from archived raw sources + the published method + the deterministic engine. If it can't be recomputed, it can't be published.
4. **Gates, not hopes.** Nothing moves between planes without a passing acceptance gate. The gate is the deployment mechanism, not an afterthought.
5. **Chain of custody.** score → ledger event → evidence source → archived raw artifact → SHA-256 hash. Unbroken, at every hop.

---

## 1. C4 Level 1 — System context

```
                 ┌────────────────────────────────────────────┐
                 │              TFCI PLATFORM                 │
   Analysts ────▶│  (collection, adjudication, publication)   │◀──── Investors / Public
                 └──────┬───────────────┬───────────────┬─────┘
                        │               │               │
                  OpenRouter       Cloudflare        Source web
                  (LLM/SLM)        (edge, R2, DNS)   (news, filings,
                                                     regulators, IEA/IRENA)
```

**Actors**

| Actor | Role |
|---|---|
| Analyst (you, later +AI agents) | Runs sweeps, adjudicates evidence, approves ledger appends |
| Investor / reviewer / public | Reads the dashboard, queries the API or MCP server |
| Harvester agents | LLM-assisted collection workers (never write to ledger) |
| Verifier agents | Cross-check harvested claims against sources (never write to ledger) |
| Auditor (future) | Re-runs the falsification pipeline from raw archives |

**External systems:** OpenRouter (model access), Cloudflare (Workers, R2, DNS, email), the public web (sources), GitHub (repo, CI, ADRs).

---

## 2. C4 Level 2 — Containers

```
┌─────────────────────────── COLLECTION PLANE (stochastic) ───────────────────────────┐
│  Harvester Agents (LangGraph + OpenRouter)     Verifier Agents (LangGraph)           │
│        │ fetch, extract, classify                     │ cross-check, flag conflicts  │
│        ▼                                               ▼                              │
│  RAW ARCHIVE (WORM): local fs + R2 bucket, content-addressed by SHA-256              │
│        ▼                                                                              │
│  STAGING (staging_events): candidate ledger events, deduplicated, awaiting review    │
└──────────────────────────────┬───────────────────────────────────────────────────────┘
                               │  HUMAN APPROVAL GATE (LangGraph interrupt)
┌──────────────────────────────▼───────────────────────────────────────────────────────┐
│                    GOVERNED DATA PLANE (deterministic, append-only)                  │
│  LEDGER (ledger_events, veto_ledger, fx_rates, projects, evidence_sources)             │
│        ▼                                                                              │
│  DETERMINISTIC CALCULATOR (tfci_engine: pure functions, no network, versioned)       │
│        ▼                                                                              │
│  SCORES (sector_scores, score_history) + COVERAGE (ledger_coverage)                  │
└──────────────┬──────────────────────────────────────────────────────────┬────────────┘
               │ ACCEPTANCE GATE (asset checks t1–t14)                    │
┌──────────────▼──────────────────────────────────────────▼────────────────────────────┐
│                     PUBLICATION PLANE (deterministic outputs)                       │
│  PAYLOAD MATERIALIZER → TFCI_frontend_payload_vN.json (immutable, hash-stamped)     │
│        ▼                                                                              │
│  API (FastAPI: REST + MCP server)  →  UI (Next.js)                                   │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**Container responsibilities**

| Container | Technology | Writes to ledger? | Runs where |
|---|---|---|---|
| Harvester agents | LangGraph + OpenRouter (SLM triage, LLM verdicts) | **Never** — staging only | Laptop now → VPS later (cron/cadence) |
| Raw archive (vault) | Local `data/evidence/` + R2 mirror, WORM semantics | n/a (immutable) | Laptop + R2 |
| Staging | `staging_events` (DB table, currently CSV) | No | Postgres |
| Approval gate | LangGraph interrupt + analyst UI | Analyst yes; agents never | Laptop |
| Governed ledger | Postgres (was CSVs) | Append-only, event-sourced | Postgres |
| Deterministic calculator | `tfci_engine` as a pure Python package | Reads ledger, writes scores | Anywhere (no I/O side effects) |
| Acceptance gate | Dagster asset checks (was `tfci_acceptance_tests.py`) | Blocks publication | CI + local |
| Payload materializer | Python job, git-SHA + engine-version stamped | No (immutable artifacts) | CI |
| API | FastAPI (+ MCP server exposing index queries) | No | Python Workers / VPS |
| UI | Next.js 16 + shadcn + TanStack + MapLibre | No | Local dev → Cloudflare Workers |

---

## 3. The data journey (numbered, falsifiable at every hop)

```
 0. SOURCE REGISTRY      evidence_sources row created BEFORE fetch (planned sweep scope)
 1. FETCH                 harvester downloads page/document (robots-respecting fetcher)
 2. RAW ARCHIVE           artifact stored verbatim → SHA-256 → vault (local + R2)
                          ── nothing downstream may alter the raw bytes ──
 3. EXTRACTION            SLM/LLM extracts structured candidate event (date, amount,
                          actors, sector, claim) → cites raw artifact hash + char offsets
 4. VERIFICATION          verifier agent cross-checks: second source? conflicts? plausibility
 5. STAGING               candidate lands in staging_events with provenance payload
 6. ADJUDICATION          human analyst reviews; LangGraph interrupt freezes the write
 7. LEDGER APPEND         approved event appended (immutable, event_id monotonic)
                          + capital normalized to USD via fx_rates (as-of event date)
 8. DETERMINISTIC COMPUTE tfci_engine recomputes sector_scores, rollups, deployment,
                          ratios from ledger — same inputs, same outputs, every time
 9. ACCEPTANCE GATE       t1–t14 as Dagster asset checks; red gate = no publication
10. MATERIALIZATION       payload JSON stamped with {git_sha, engine_version, input_ledger_hash}
11. PUBLICATION           API serves payload; UI renders; R2/Workers cache
```

**Where scraping happens:** steps 1–4, on your laptop today (on demand), on a VPS later (on cadence per the tier table: T1 Weekly … T4 Annual). Scraping is *pull-triggered by the source registry* — the sweep cadence of a jurisdiction determines how often its harvesters run.

**Where the deterministic calculator sits:** step 8, and nowhere else. It is a **pure function package**: `scores = engine(ledger_state, standard_version)`. No network, no LLM, no clock, no randomness. Its only inputs are the ledger and the Standard version. This is what makes falsification possible: anyone holding the ledger snapshot and the engine version can reproduce every score bit-for-bit.

**Where SQL sits:** Postgres is the *system of record* for the ledger and the *query layer* for the API (materialized views for rollups). SQL never *computes* scores — computation stays in the versioned Python engine so the method travels with the repo, not the database.

---

## 4. Falsifiability design

A claim is falsifiable when a skeptic can, in principle, prove it wrong. TFCI's falsification contract:

| Mechanism | Implementation |
|---|---|
| **Recompute challenge** | `make reproduce SNAPSHOT=2026-09-28` → replays engine over archived ledger snapshot → diff against published payload. Any delta = red alert. |
| **Chain of custody** | score row → `evidence_source_ids` → source row → raw artifact → SHA-256. UI "why this score" walks this chain to the archived document. |
| **Bitemporal honesty** | every event carries event date + recording date; payloads are stamped `as_of`; history is never silently rewritten (append-only). |
| **Negative controls** | known-veto cases (e.g., Greenland uranium ban) must reproduce as vetoes; if the pipeline ever fails to reproduce a control, the gate goes red. |
| **Method publication** | the Standard is versioned in-repo; engine version is stamped into every payload; a score cannot exist without a method version. |
| **Drift detection** | recomputation over time must be monotone-explained: any score change must trace to ledger events between snapshots (no "unexplained drift" allowed). |
| **Adversarial review** | GraphRAG over the evidence graph lets a reviewer ask "show me every project blocked by a statute" and check the veto ledger against it. |

## 5. Reproducibility design

| Layer | Mechanism |
|---|---|
| Code | git; every payload embeds `git_sha` |
| Dependencies | lockfiles (`uv.lock`/`requirements.txt` pinned); Docker images by digest, not tag |
| Database schema | Alembic migrations, versioned in-repo |
| Data snapshots | ledger snapshots (logical dump) per publication; fixture "golden files" for engine unit tests |
| Engine determinism | golden-file tests: fixed ledger fixture → expected scores, byte-compared |
| Build | same Docker images locally and in CI; CI gate = local gate |
| Publication artifacts | payload JSON + manifest (hashes of all inputs) archived to R2 |

## 6. Local UI → hosted UI

The UI is **one codebase, two runtimes**:

```
DEVELOPMENT (laptop, WSL2)
  next dev  ──▶  http://localhost:3000  ──▶  uvicorn (FastAPI) ──▶  Postgres (Docker)
  hot reload, mock data allowed, seed from latest materialized payload

PRODUCTION (Cloudflare)
  git push ──▶ GitHub Actions:
        1. pytest (engine golden files)
        2. Dagster asset checks (t1–t14) over current DB
        3. materialize payload → R2 (versioned, immutable)
        4. wrangler deploy (Workers: UI + API edge layer)
  credibilitydashboard.com ──▶ Workers ──▶ R2 payload / Hyperdrive ──▶ Postgres (VPS, Phase 3+)

  credibilityboard.com ──▶ 301 redirect ──▶ credibilitydashboard.com
```

Key rule: **the UI never computes**. It renders the materialized payload exactly as the mockups do today (`V83`/`DATA` blobs become API responses). The local–hosted boundary is a deployment concern, not an architectural fork — same containers, same gate, same artifacts.

## 7. Target repository structure (monorepo)

```
tfci/
├── docs/
│   ├── TFCI_Standard_v0.7.md            # method (existing)
│   ├── adr/                             # 0001-use-adrs.md, 0002-postgres-for-ledger.md, ...
│   └── TFCI_System_Architecture_v1.0.md  # this document
├── engine/                              # deterministic calculator (pure Python package)
│   ├── src/tfci/engine.py               # graduated from src/tfci_engine.py
│   └── tests/golden/                    # fixture ledger → expected scores
├── ledger/                              # schema + migrations
│   ├── alembic/
│   └── seed/                            # snapshot loads
├── collectors/                          # harvest + verify agents (LangGraph, MCP tools)
├── pipelines/                           # Dagster assets + checks (t1–t14)
├── api/                                 # FastAPI app + MCP server
├── web/                                 # Next.js 16 + shadcn + MapLibre
├── data/                                # current governed CSVs → migrated into Postgres
├── infra/
│   ├── docker-compose.yml               # local = prod parity
│   └── wrangler.toml                    # Workers config
└── .github/workflows/gate.yml           # CI gate (existing, extended)
```

## 8. Phased roadmap

| Phase | Deliverable | Exit criterion |
|---|---|---|
| **0. Foundations** (now) | WSL2 + Docker; Postgres schema mirroring CSVs; CSV loader post-gate; repo restructure; ADRs 0001–0008 | 14/14 gate green against Postgres-loaded data |
| **1. API + local UI** | FastAPI serving existing payload shape; Next.js shell reproducing mockup v0.9.7 pixel-for-pixel (TanStack table, MapLibre map) | local UI reads live from API; mockup retired to design reference |
| **2. Publish** | CI gate → payload materialization → Workers deploy; R2 vault mirror; Email Routing live | credibilitydashboard.com serves real data from CI-built artifacts |
| **3. Agent factory** | Dagster cadence sweeps; LangGraph harvest/verify with OpenRouter; human approval UI; MCP server | first weekly sweep produces staged candidates with zero manual fetches |
| **4. Knowledge layer** | Neo4j evidence graph + GraphRAG over vault; "why this score" provenance views; A2A between specialized agents | reviewer can walk score → statute → archived document in one query |

## 9. Seed ADRs to write immediately

1. `0001` — We record architecture decisions as ADRs.
2. `0002` — Postgres is the system of record; CSVs are transitional source-of-truth.
3. `0003` — Scores are computed only by the deterministic engine package; never by SQL, never by LLM.
4. `0004` — Agents never write to the ledger; humans approve via staging gate.
5. `0005` — Publication is gated by the acceptance suite; red gate blocks deploy.
6. `0006` — One UI codebase (Next.js), deployed to Cloudflare Workers; no separate mockup lineage after v1.
7. `0007` — Raw evidence artifacts are immutable and content-addressed (SHA-256), stored locally and mirrored to R2.
8. `0008` — Payloads are immutable, versioned artifacts stamped with git SHA + engine version + input hash.

---

*This document supersedes nothing yet; it is the parent of the ADR series. Update it only through the ADR process.*
