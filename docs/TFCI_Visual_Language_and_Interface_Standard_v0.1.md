# TFCI Visual Language and Interface Standard

**Version:** 0.1  
**Status:** Pre-launch normative interface standard  
**Authority:** Subordinate to the TFCI Standard; governs public representation of governed TFCI data.

## Purpose

This standard defines how the TFCI communicates governed scores, Structural Vetoes, capital measures, evidence classes, coverage states, and uncertainty in public interfaces. It MUST NOT modify, infer, smooth, or obscure a governed value.

## Authority and conflicts

1. The Manifesto governs purpose and intellectual philosophy.
2. The TFCI Standard governs methodology, vocabulary, scoring, vetoes, data and publication contract.
3. This document governs the visual and interaction representation of those governed outputs.
4. A dashboard implementation MUST conform to this document.
5. In any conflict, the TFCI Standard prevails. A visual treatment MUST NOT create a second undocumented scoring system.

## Semantic grammar

| Concept | Canonical encoding | Must not mean |
|---|---|---|
| Credibility Score | Continuous sequential colour | Capital magnitude or evidence quality |
| Deployment Score | Selected analytical axis and published number | Credibility colour replacement |
| Active capital | Bubble area and right-aligned currency value | Score quality |
| Capital evidence class | Badge, outline and method text | Credibility score |
| Structural Veto | Explicit count/state and severity banner | A hidden score adjustment |
| Pillar subscore | Coloured progress fill and radar vertex | Neutral grey score fill |
| Interaction/focus | Navy focus ring | Positive execution quality |
| Legacy baseline | Slate provenance treatment | Low score or veto |
| No active capital | Dashed outline and explicit text | Numerical zero |

## Score colour ramp

Score quality uses one continuous ordered ramp. Published HIGH, MEDIUM and LOW bands remain governed by the TFCI Standard and are always shown in text where needed.

| Score | Colour | Meaning |
|---:|---|---|
| 0–24 | `#7F1D1D` | Critical constraint |
| 25–39 | `#B91C1C` | Severe friction |
| 40–54 | `#D97706` | Material constraint |
| 55–69 | `#D6A20A` | Mixed / monitor |
| 70–84 | `#3A8F5C` | Sound execution capacity |
| 85–100 | `#0B6B4F` | Best-in-class execution capacity |

Navy is reserved for selected and keyboard-focus states. Slate is reserved for neutral structure, reference and legacy states. Colour is never the sole carrier of a governed state.

## Capital and evidence

Active capital uses the publication payload field `activeCapitalUsdBn`. Bubble area encodes magnitude. Evidence class uses border/outline, badge and text: verified is green, derived teal, modelled amber, legacy slate, and not established wine-red dashed. A missing active value MUST read “Not established” and MUST NOT be rendered as zero.

## Veto, pillars and radar

Structural Veto is a governed fact. UI severity MAY combine veto burden and credibility for comprehension, but MUST NOT modify the veto state, score, rank or band. Pillar bars use the score ramp on a neutral track. Radar outline/fill uses the five-pillar profile; vertices use individual pillar colours. Axis scaffolding remains neutral slate.

## Tables and controls

Names and descriptive labels are left aligned. Scores, ranks, counts, percentages and currency are right aligned using tabular numerals. Small fixed-width badges are centred. Selected analytical toggles use deep teal; reset uses neutral pale slate; navy marks focus and hover.

## Versioning

A material change to a canonical visual encoding, map treatment, colour semantic, interaction rule or disclosure state MUST have a dated entry in `TFCI_Design_Decision_Log.md`.
