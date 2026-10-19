# TFCI Accessibility and Map Policy

**Version:** 0.1  
**Status:** Pre-launch mandatory UI policy

## Core requirements

- Colour MUST NOT be the sole means of communicating score, band, evidence class, veto or data state.
- All interactive map and chart marks MUST be reachable by keyboard.
- Hover content MUST also appear on keyboard focus.
- Tooltips MUST be dismissible with Escape, remain visible while pointer users move to them, and not obscure the selected mark.
- Enter and Space open the same jurisdiction panel as pointer click.
- Every map/chart MUST have a linked table or textual equivalent.
- Focus uses a visible high-contrast navy ring.
- Flags supplement names; they never substitute for jurisdiction names.
- Interfaces respect reduced-motion preferences.

## Geographic policy

Geographic representation is analytical location only. Boundaries, names and treatments do not imply an institutional position on sovereignty, legal status or boundary delimitation. TFCI uses canonical jurisdiction slugs, not map-provider names, for data joins.

Small states, islands, observer states and territories may use a point marker plus a regional locator inset. The user must still be able to find and activate every indexed jurisdiction through search and table views.

## Test checklist

1. Tab through all controls and visible map/chart marks.
2. Verify focus tooltip equals hover tooltip.
3. Verify Escape dismisses tooltip.
4. Verify tooltip contents are available in the table/panel.
5. Verify contrast and 200% zoom remain usable.
6. Verify no-null-capital state is explicitly textual.
