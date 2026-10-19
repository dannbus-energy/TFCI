# TFCI Dashboard Component Catalog

**Version:** 0.1  
**Status:** Pre-launch implementation specification

## Shared component contract

Every dashboard component documents its purpose, payload inputs, primary encoding, secondary encoding, keyboard behavior, textual equivalent, null behavior, responsive behavior and acceptance criteria. Components MUST use canonical TFCI slugs for joins.

## Landing controls

- Filters preserve the current region, sector, pillar and band semantics.
- Credibility and Deployment are mutually exclusive analytical basis controls.
- Selected analytical controls use deep teal; reset is neutral slate and shares the 40 px control baseline.
- All controls are keyboard operable and have visible navy focus.

## Geographic map

- Colour: continuous Credibility Score ramp.
- Hover/focus: navy outline/halo; same tooltip content on pointer and keyboard focus.
- Activation: click, Enter or Space opens the jurisdiction panel.
- Tooltip: flag, jurisdiction, credibility, deployment, rank, active capital, evidence class and veto count.
- Microstates: labelled point marker and regional locator inset where polygon geometry is not legible.
- A linked table is the non-map equivalent.

## Execution Map

- Position: selected governed analytical scores.
- Bubble area: `activeCapitalUsdBn`.
- Bubble fill: credibility colour.
- Outline: capital evidence class.
- Dashed wine outline: no active capital value, never zero.

## Jurisdiction panel

- Retain scorecards, ranks, bands, veto narrative, pillar profile, radar, sector grid and outlook.
- Add flag and locator map beside the jurisdiction switcher.
- Add Capital evidence card under the score header: active capital, range, method, evidence class and explicit null interpretation.

## Veto banner and pillars

- Banner text identifies active-veto count and most exposed pillar.
- Severity is presentational and must not alter governed values.
- Pillar bars use the canonical score ramp; neutral grey is track only.
- Radar uses profile colour and pillar-coloured vertices.

## Data table

- Left: jurisdiction and region.
- Right: scores, ranks, counts, currency and percentages.
- Centre: compact badges and icons.
- Active capital is right aligned; evidence badge follows the numeric amount.
