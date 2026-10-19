# TFCI Map Geometry Coverage Audit v0.4

## Method

- Read-only audit; neither governed map asset is modified.
- Requires 207 unique features in canonical and browser-map assets and verifies normalized JSON equivalence.
- Compares each current Point geometry first to Natural Earth `ISO_A2` / `ISO_A2_EH`, then country-name metadata and explicit aliases.

## Summary

- Polygon / MultiPolygon: **167**
- Point markers: **40**
- Confirmed polygon repair candidates: **0**
- Exceptions requiring documented scale/territory decision: **40**

## Required geometry repairs

No current point marker matched a Natural Earth polygon.


## Documented exception queue

These do not resolve to a usable Natural Earth 110m country polygon under ISO-2 or name/alias matching. Retain as a point only after documenting that the 110m map scale or territorial representation makes a point marker intentional.

| Slug | ISO-2 | Current source |
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

## Dashboard renderer rule

Render all polygon/multipolygon paths first. Render approved points in a second final pass with a white halo and navy outline. A future build must fail while Required geometry repairs is non-empty.
