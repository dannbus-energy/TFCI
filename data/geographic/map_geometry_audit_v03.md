# TFCI Map Geometry Coverage Audit v0.3

## Scope

- TFCI canonical and browser map files: 207 unique features each.
- External comparison source: Natural Earth 1:110m Admin 0 Countries.
- Matching method: normalized TFCI slug against Natural Earth country-name metadata and documented aliases.
- This is a read-only audit: no map geometry has been changed.

## Summary

- Current Polygon / MultiPolygon features: **165**
- Current Point-marker features: **42**
- Point markers with matching Natural Earth polygon geometry: **2**
- Point markers requiring manual name/territory review: **40**

## Required geometry repairs

| TFCI slug | ISO-2 | Current source | Natural Earth match | Required action |
|---|---|---|---|---|
| norway | NO | REST Countries centroid fallback | Norway | Replace Point with polygon geometry |
| taiwan | TW | REST Countries centroid fallback | Taiwan | Replace Point with polygon geometry |

## Manual point-marker review

These point markers did not match by country-name metadata. They are not automatically approved; review territorial naming and intended representation before retaining Point geometry.

| TFCI slug | ISO-2 | Current source |
|---|---|---|
| singapore | SG | REST Countries centroid fallback |
| mauritius | MU | REST Countries centroid fallback |
| andorra | AD | REST Countries centroid fallback |
| aruba | AW | REST Countries centroid fallback |
| bahrain | BH | REST Countries centroid fallback |
| barbados | BB | REST Countries centroid fallback |
| bermuda | BM | REST Countries centroid fallback |
| cabo-verde | CV | REST Countries centroid fallback |
| cayman-islands | KY | REST Countries centroid fallback |
| cook-islands | CK | REST Countries centroid fallback |
| curacao | CW | REST Countries centroid fallback |
| guernsey | GG | REST Countries centroid fallback |
| isle-of-man | IM | REST Countries centroid fallback |
| jersey | JE | REST Countries centroid fallback |
| liechtenstein | LI | REST Countries centroid fallback |
| maldives | MV | REST Countries centroid fallback |
| malta | MT | REST Countries centroid fallback |
| san-marino | SM | REST Countries centroid fallback |
| seychelles | SC | REST Countries centroid fallback |
| saint-lucia | LC | REST Countries centroid fallback |
| turks-and-caicos | TC | REST Countries centroid fallback |
| hong-kong | HK | REST Countries centroid fallback |
| macau | MO | REST Countries centroid fallback |
| comoros | KM | REST Countries centroid fallback |
| sao-tome-principe | ST | REST Countries centroid fallback |
| kiribati | KI | REST Countries centroid fallback |
| marshall-islands | MH | REST Countries centroid fallback |
| micronesia | FM | REST Countries centroid fallback |
| nauru | NR | REST Countries centroid fallback |
| palau | PW | REST Countries centroid fallback |
| samoa | WS | REST Countries centroid fallback |
| tonga | TO | REST Countries centroid fallback |
| tuvalu | TV | REST Countries centroid fallback |
| antigua-barbuda | AG | REST Countries centroid fallback |
| dominica | DM | REST Countries centroid fallback |
| grenada | GD | REST Countries centroid fallback |
| saint-kitts-nevis | KN | REST Countries centroid fallback |
| saint-vincent-grenadines | VC | REST Countries centroid fallback |
| monaco | MC | REST Countries centroid fallback |
| holy-see | VA | REST Countries centroid fallback |

## Rendering control

Render polygons first. Render remaining approved point markers in a second final SVG pass with a white halo and navy outline, preventing marker occlusion by neighboring polygons.

## Build gate

Future dashboard builds must fail when the Required geometry repairs table is non-empty. Manual-review entries require a documented representation decision.
