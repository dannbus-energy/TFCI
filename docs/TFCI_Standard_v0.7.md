# TFCI Standard

> Markdown preservation copy generated from `TFCI_Standard-2.docx` on 2026-09-15. The DOCX remains the authoritative source record for this conversion.

Transition Finance Credibility Index — TFCI Standard

September 13, 2026

Part 0 — Document control

Status. Pre-launch; the 0.x series permits breaking changes. Public launch freezes v1.0; DOI minting freezes it permanently.

Coverage. 207 jurisdictions — every UN member state (193), both observer states (Holy See, Palestine), and 12 territories with materially autonomous policy.

Lineage. CIEES 2026 conference paper → Credibility-PISA journal methodology → this Index.

Normative language. The key words MUST, MUST NOT, SHOULD, and MAY are to be interpreted as follows: MUST = an absolute requirement of the instrument; SHOULD = a strong default, deviations must be logged; MAY = a genuinely optional behavior.

Companion. The TFCI Manifesto states the instrument's purpose. This document is the single normative reference for its construction.

Part I — Purpose and principles

The TFCI evaluates where transition capital will execute and where it will strand. Incumbent frameworks measure policy intent, announced targets, or pipeline size. The TFCI measures execution capacity: the physical, regulatory, capital, social, and delivery realities that decide whether announced capital becomes operating infrastructure.

Three principles govern everything:

Execution over intent. A jurisdiction is scored on what it can deliver, not what it announces.

Physics is non-negotiable. Capital cannot compensate for absent water, land, grid capacity, or geology — formalized as the Structural Veto (Part III).

Falsifiability. Scores imply predictions; the Conversion Ledger (Part IV) tests them; the Gap is published; the Index measures its own accuracy against delivered outcomes and publishes the result.

Part II — Taxonomy and controlled vocabulary

2.1 Architecture

Fixed matrix: 207 jurisdictions × 20 sectors × 5 pillars. The jurisdiction-level All-Sectors aggregate is a derived rollup (Part III) — a published view, never a stored fact. Regions (8): Europe, APAC, South Asia, Central Asia, MENA, SS Africa, LatAm, N. America.

2.2 Jurisdiction admission rule

A jurisdiction enters the matrix if it is: (i) a UN member state, a UN observer state, or a territory with materially autonomous policy; (ii) above a minimal evidence floor sufficient for honest scoring at Low/Medium data confidence; (iii) of material economic, energy, or strategic weight. Jurisdictions below the evidence floor join a published watch list rather than the matrix. Coverage is complete under this rule; territories are reviewed annually.

2.3 The four sector admission tests

A sector joins only if it is: (i) a distinct capital sink ≥ ~$200B/decade; (ii) veto-prone — a physical or execution bottleneck; (iii) durable through 2031, defensible toward 2036; (iv) MECE-bounded against neighboring sectors.

2.4 The 20 sectors

ID

Sector

Group

Capital Pool

T16

Utility-Scale Renewables

Clean Power Supply

$6.9T

T17

Nuclear & Clean Firm

Clean Power Supply

$750B

T18

Energy Storage & Flexibility

Clean Power Supply

$1.5T

T01

Grid Modernization

Energy Networks & Molecules

$2.5T

T19

Hydrogen & Powerfuels

Energy Networks & Molecules

$800B

T11

Carbon Markets

Energy Networks & Molecules

$900B

T03

Critical Minerals

Resources & Physical Baseload

$3.8T

T02

Water Security

Resources & Physical Baseload

$1.2T

T15

Food Systems & Agriculture

Resources & Physical Baseload

$1.4T

T04

AI Compute

Deep Tech & Advanced Industry

$2.1T

T05

Semiconductors

Deep Tech & Advanced Industry

$1.9T

T07

Advanced Manufacturing

Deep Tech & Advanced Industry

$3.1T

T13

Cyber-Physical Security

Deep Tech & Advanced Industry

$850B

T12

Space Economy

Deep Tech & Advanced Industry

$600B

T06

Net-Zero Mobility

Mobility & Built Environment

$4.2T

T08

Aviation & Maritime

Mobility & Built Environment

$1.5T

T20

Buildings & Heat

Mobility & Built Environment

$4.0T

T09

Smart Cities

Human & Digital Infrastructure

$2.8T

T10

Labor Transition

Human & Digital Infrastructure

$1.1T

T14

Digital Public Infrastructure

Human & Digital Infrastructure

$750B

2.5 Boundary rules (MECE)

Generation → Utility-Scale Renewables; wires → Grid Modernization; storage deployment → Energy Storage & Flexibility. Fuel production → Hydrogen & Powerfuels; fleet/port adoption → Aviation & Maritime. Battery manufacturing → Advanced Manufacturing; battery deployment → Energy Storage. Data centers → AI Compute. Mining and refining → Critical Minerals. EV charging → Net-Zero Mobility. CCUS within industrial narratives.

2.6 Stability rule

Sector_IDs are append-only: never renumbered, never reused. The same rule applies to jurisdiction slugs, pillar IDs, project IDs, and event IDs. Names are promises.

2.7 Watch list

Distributed-energy delivery models; nature/biodiversity finance; fusion (on commercialization evidence); standalone CCUS; Smart Cities / DPI consolidation review.

2.8 Controlled vocabulary (normative)

One concept, one term, everywhere. The canonical terms are: jurisdiction; sector; pillar; announced capital; commissioned capital; cancelled capital; Execution Ratio (commissioned ÷ announced); Survival Ratio (1 − cancelled ÷ announced); Credibility Gap (1 − Execution Ratio); Structural Veto; Credibility Score; Deployment Score; capital pool; sweep cadence; recompute tier. Synonyms MUST NOT be introduced at any layer.

Part III — Scoring and veto methodology

3.1 The five structural pillars

P1 Regulatory Certainty · P2 Physical Bandwidth · P3 Capital Architecture · P4 Social License · P5 Execution Velocity. The absence of a veto is the documented state P0 (No Veto).

3.2 Scoring doctrine: anchored judgment

Sub-scores are analyst assessments anchored to published indicator bands (80–100 best-in-class demonstrated; 60–79 sound with binding local constraints; 40–59 announced-not-statutory / chronic friction; 20–39 voluntary-reversing / systemic failure; <30 fundamental failure). Metrics normalize via bands as inputs to judgment; band crossings require a second reviewer; QA target inter-rater MAD < 4. Every sub-score MUST cite its evidence records.

3.3 The P5 empirical anchor — staged by evidence depth

P5 is anchored to the Conversion Ledger where evidence permits. The anchor stage is stored and published with every score:

Ledger evidence per cell

P5 formula

Anchor regime stamp

0 qualifying projects

1.00 × analyst

analyst

1–9 projects

0.70 × analyst + 0.30 × (Execution Ratio × 100)

hybrid

≥10 projects

0.60 × analyst + 0.40 × (Execution Ratio × 100)

empirical

Universality is preserved by transparency: the rulebook is identical for every jurisdiction; the evidence depth is visible on every row. The regime stamp MUST be published in the fact table and the frontend payload.

3.4 Rollup and band doctrine

Sector Overall Score = round-half-up mean of the five pillar sub-scores, exact on every row.

All-Sectors rollup (derived view): each pillar sub-score = pillar-wise rounded mean of the jurisdiction's 20 sector rows; Overall = rounded mean of those sub-scores. The two-step order (sub-score rounding precedes Overall rounding) is canonical.

Bands: HIGH ≥ 75 · MEDIUM 50–74 · LOW < 50. Derived, never edited.

Structural Veto — two-path trigger: (i) floor path — any pillar < 30 ⇒ automatic veto on that pillar; (ii) event path — an approved Veto_Ledger event evidencing a structural blocker ⇒ veto on the evidenced pillar at any sub-score. Consequence: non-compensation. A cell has at most one veto; the veto is stored as a single nullable pillar reference, never as a boolean matrix.

Hysteresis: downgrades apply immediately; recoveries release at ≤ +4 points/quarter with zero recovery in the first quarter post-resolution.

3.5 The dual jurisdiction scores

Credibility Score (headline): the jurisdiction's All-Sectors Overall Score — identical by construction to the rollup view.

Deployment Score (capital-weighted): Σ(sector score × sector capital pool) ÷ Σ(capital pool). Published only where the jurisdiction's capital weights are assessed; where unassessed, the score is suppressed and the coverage state is published — never silently omitted. Both scores obey the same band, veto, and hysteresis doctrine, and are published with ranks.

Part IV — The Conversion Ledger (normative core)

The Ledger is the instrument's instrument: the causal record of expectation versus execution. The base relation is the event set, not the project status. All statuses, cumulative capital figures, and ratios are derived views over an append-only event log. This guarantees the accumulation of history that cannot be recreated retrospectively: no fact is ever edited or deleted.

4.1 Event types

Event

Semantics

announcement

Opens an account; the denominator event

capex_revision

Non-destructive; the latest revision is canonical, history preserved

fid

Financial investment decision

construction_start

Ground broken

partial_commissioning

Closes an account pro-rata at the fraction commissioned

commissioning

Closes the account

cancellation

The falsification signal; capital leaves the surviving base, never the announced base

resumption

Reopens a cancelled/shelved project; feeds the hysteresis watch

retraction

Corrects a recording error only, and MUST reference the superseded event

4.2 Canonical aggregation rules

Cell-level Execution Ratio = Σ commissioned ÷ Σ announced (latest revision canonical), per jurisdiction × sector.

Cell-level Survival Ratio = 1 − (Σ cancelled ÷ Σ announced).

Credibility Gap = 1 − Execution Ratio, published at cell and jurisdiction grain.

Jurisdiction-level Execution Ratio = Σ commissioned ÷ Σ announced across sectors — weighted by announced capital, not by capital pools.

Partial commissioning counts pro-rata.

Cancellation never reduces the announced denominator.

4.3 Coverage model — nulls are forbidden

Every one of the 4,140 cells MUST carry a coverage state; silence is never an acceptable value:

populated (≥10 projects) · thin (1–9) · announced_only · swept_empty (a sweep ran; no qualifying announcements — a publishable finding) · not_yet_swept (a to-do, never presented as a finding).

4.4 Bitemporality

Every event carries event_date (when it happened in the world) and recorded_at (when the Index observed it). Fact time and record time are never conflated; snapshot artifacts carry as_of_date.

4.5 Backfill doctrine

Coverage gaps are worked in priority order: (1) T1 jurisdictions; (2) T2/T3; (3) T4 via headline-projects tracking, honestly stamped. Backfill trajectory is published per release. A jurisdiction with no computed ratio MUST publish its coverage state.

Part V — Data architecture

5.1 Layered design

Source of record — normalized tables, the only editable data.

Derived views — recomputed by the scoring engine; never hand-edited (jurisdiction rollups, pillar summaries, bands, ranks, ratios).

Publication payloads — generated artifacts (frontend JSON, CMS exports), parity-tested in CI.

5.2 Source-of-record tables

Dimensions. jurisdictions (jurisdiction_slug PK, name, iso2, iso3, region, sweep_cadence, recompute_tier) · sectors (sector_slug PK, sector_id, name, sector_group, description, capital_pool_usd_bn, display_order) · pillars (pillar_slug PK, pillar_id, name, question, definition, icon_url) · sourcing_policy (sector_slug PK, min_records, target_records, max_records, sweep_cadence, preferred_sources, stop_rule, escalation_rule, min_ledger_projects, completion_sources).

Fact. sector_scores — PK (jurisdiction_slug, sector_slug, as_of_date); p1_subscore … p5_subscore; overall_score; has_veto; veto_pillar_slug (nullable FK, P0 semantics when null); legacy_drag; investment_outlook; private_outlook; human_capital_trend; data_confidence. One row per cell per snapshot; history is versioned, never overwritten.

Ledger and state. projects (project_id PK, jurisdiction_slug, sector_slug, project_name, capacity_unit, created_at) · ledger_events (event_id PK, project_id, event_type, event_date, capital_usd_bn, source_url, source_confidence, recorded_at) — append-only · ledger_coverage (jurisdiction_slug + sector_slug PK, ledger_status, project_count, last_sweep_date, sweep_source) · veto_ledger (event-path veto evidence) · score_history (mandatory hysteresis state store).

5.3 Derived views (engine-owned)

v_project_status · v_cell_conversion · v_jurisdiction_conversion · v_all_sectors_rollup · v_jurisdiction_scores (with credibility_rank, deployment_rank, execution_ratio, survival_ratio, credibility_gap, ledger_status, p5_anchor) · v_jurisdiction_pillar_summary (subscore, vetoed_sector_count, weakest_sector_slug, strongest_sector_slug — slugs, never display names).

5.4 Data conventions

CSV interchange: dates ISO 8601; booleans lowercase true/false; UTF-8; slugs ^[a-z0-9-]+$, immutable; joins by slug, never by display name; measures carry units in their names (_usd_bn); counts carry _count; booleans are predicates (has_veto); no SQL reserved words as identifiers; no nulls where a coverage state exists; no OLD/NEW/COPY/final in file names.

Part VI — Naming conventions (normative)

Every concept has one canonical name per layer, with a documented mapping:

Layer

Convention

Example

Normative (this Standard, Manifesto)

Product terms, Title Case

Credibility Gap

Data (tables, columns)

snake_case; plural tables, singular columns

credibility_gap

API / payload (JSON)

camelCase, full words — no abbreviations

credibilityGap

CMS (collections)

Natural plural nouns for editors

Jurisdictions

UI copy

Sentence case, human terms

Credibility Gap

Additional rules: file names follow {Project}_{Artifact}_v{major.minor}.{ext}; the fact table is named for its grain (sector_scores), never for a shape ("matrix"); derived views confess their nature in their names; and display names never appear where a slug can serve.

Part VII — Collection and pipeline operations

Sourcing policy per sector, including AI Compute (policy coverage is complete — no pseudo-sector rows).

Two-track collection. Track A (announcements): FID trackers, press releases, developer filings — loud. Track B (completions): commissioning reports, grid-operator registries, plant databases — quiet. Track B is deliberately over-weighted: the epistemic asymmetry between loud announcements and quiet completions is the ontology of the instrument.

Two-level scheduling. sweep_cadence (Weekly · Biweekly · Monthly · Quarterly · Semiannual · Annual) governs the evidence sweep; recompute_tier (T1–T4) governs score recompute. Mapping: Weekly/Biweekly → T1, Monthly → T2, Quarterly → T3, Semiannual/Annual → T4. Within T1, Weekly jurisdictions are swept every 7 days, Biweekly every 14; both recompute biweekly so published rankings are not churned by intra-fortnight noise. The always-on event layer (veto triggers, FIDs, cancellations, commissionings) overrides all schedules. Tier assignments combine systemic weight, data velocity, and volatility; published annually with changes logged.

Extraction ≠ scoring. Collected evidence never edits scores directly; it flows through the engine.

Ledger → matrix feedback runs through the hysteresis state store, never by hand.

Part VIII — Publication contract

8.1 Frontend payload

Engine-generated JSON; camelCase, full words. Jurisdiction objects carry: slug, name, iso2, region, sweepCadence, recomputeTier, credibility, credibilityBand, credibilityRank, deployment, deploymentBand, deploymentRank, executionRatio, survivalRatio, credibilityGap, ledgerStatus, p5Anchor, asOf. Keys for keyed collections use slug pairs, never display names. The Credibility Gap MUST appear on the landing page of the public instrument.

8.2 CMS mapping

Framer collections are named for what editors manage: Jurisdictions (207), Sectors (20), Pillars (5). The landing ranking is a view of Jurisdictions sorted by credibility score — never a collection itself. Import order: Jurisdictions → Sectors → Pillars → Sector Scores export. Cell-grain data (4,140 rows per snapshot) is served by the payload or API, not stored as editable collections. UI rules: paginate 25–50 rows; lazy-load; filter-first; outlook fields as plain strings; verify a 100-row sample import before bulk.

Part IX — Quality assurance

Acceptance tests MUST pass in CI before any release:

FK integrity: every ledger and fact reference resolves to a dimension member; sector references are real sectors only.

Domain checks: 0 ≤ Execution Ratio ≤ 1; commissioned ≤ announced − cancelled per project and per cell.

Coverage completeness: all 4,140 cells carry a ledger_coverage row; no null states.

Parity: published jurisdiction ratios equal ledger-recomputed values; Credibility Score equals the rollup view; Country-level artifacts equal engine output.

Anchor coherence: every P5 score carries a regime stamp consistent with its cell's project count.

Append-only audit: monotonic event IDs; retractions reference their superseded events.

Payload parity: all 207 jurisdictions present; Gap and coverage fields populated.

Doc sync: this Standard's table list matches the delivered package exactly.

Spot-check: ≥95% of sampled cells match source evidence.

Part X — Versioning

One version line across the entire package. The 0.x series permits breaking changes; v1.0 freezes at public launch; DOI minting freezes permanently. Every artifact carries the same version at a given cut. Changelog entries are dated, attributed, and note breaking changes explicitly.

Appendix A — Worked example

Norway, Evidence Pack 2026-09-10: AI Compute cell P1 80 / P2 78 / P3 84 / P4 78 / P5 76 → Overall 79 → HIGH, no veto (P0), anchor empirical. Norway leads both jurisdiction scores (Credibility 80 #1, Deployment 83 #1 of 207). Ledger: 31 announced projects in the cell, 26 commissioned, 2 cancelled → Execution Ratio 0.84, Survival Ratio 0.94, Credibility Gap 0.16 — published on the landing page.

Appendix B — Package manifest (planned, cut with v0.1 Second Edition)

Artifact

File

Foundational document

TFCI_Manifesto

This Standard

TFCI_Standard

Consolidated dataset

TFCI_Dataset.xlsx

Source-of-record CSVs

jurisdictions · sectors · pillars · sector_scores · sourcing_policy

Ledger CSVs

projects · ledger_events · ledger_coverage · veto_ledger · score_history

Engine

TFCI_Scoring_Engine.py

Acceptance tests

TFCI_Acceptance_Tests.py

Frontend payload

TFCI_frontend_payload.json

Frontend reference

TFCI_Dashboard_Mockup.html

Collection exemplars

Norway_Evidence_Pack.csv · Ledger_Backfill_Backlog_v0.1.csv
