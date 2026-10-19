#!/usr/bin/env python3
"""
compose_mockup_v092b.py - deterministic regenerator (clean rerun of v092).

Input : mockups/TFCI_Dashboard_Mockup_v0.9.1.html
        data/TFCI_frontend_payload_v2.json
        data/sector_scores.csv
        assets/map/tfci_jurisdiction_boundaries_simplified.geojson
Output: mockups/TFCI_Dashboard_Mockup_v0.9.2.html

A1. V83 blob  <- rebuilt from the governed payload (Greenland rides map/table/capital)
A2. F83 blob  <- rebuilt from the geojson (real Greenland MultiPolygon)
A3. DATA blob <- Greenland added to countries/pillars/secScores/vetoes/outlooks
A4. "Show All 207" -> 208
B.  view-limit leak root-fix: expandAndResort rewritten via brace-balanced extraction;
    rows-per-page is stashed (window.cap92) and restored on Reset/filter/pager/per-page.
"""
import csv, json, os, re, shutil, subprocess, sys

ROOT = r"C:\dev\tfci"
MOCK = os.path.join(ROOT, "mockups")
INPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.1.html")
OUTPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.2.html")
PAYLOAD = os.path.join(ROOT, "data", "TFCI_frontend_payload_v2.json")
SCORES = os.path.join(ROOT, "data", "sector_scores.csv")
GEOJSON = os.path.join(ROOT, "assets", "map", "tfci_jurisdiction_boundaries_simplified.geojson")

DEC = json.JSONDecoder()

def splice(html, marker, obj):
    """Replace the JS value that begins right after `marker` with json-obj (minified)."""
    i = html.find(marker)
    assert i != -1, "marker not found: " + marker
    start = None
    for k in range(i + len(marker), min(i + len(marker) + 512, len(html))):
        if html[k] in "[{":
            start = k
            break
    assert start is not None, "value start not found after " + marker
    parsed, end = DEC.raw_decode(html[start:])
    dumped = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return html[:start] + dumped + html[start + end:], len(parsed)

def replace_function(html, fname, new_src):
    i = html.find("function " + fname + "(")
    assert i != -1, "function not found: " + fname
    p = html.find("{", i)
    depth = 0
    k = p
    while True:
        c = html[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    old = html[i:k + 1]
    return html.replace(old, new_src, 1), old

# ------------------------------------------------------------------ data in
payload = json.load(open(PAYLOAD, encoding="utf-8"))
jz = payload["jurisdictions"]
gl = next(j for j in jz if j["slug"] == "greenland")

rows = {}
with open(SCORES, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["jurisdiction_slug"] == "greenland":
            rows[r["sector_slug"]] = r
assert len(rows) == 20, "expected 20 greenland sector rows, got %d" % len(rows)

geo = json.load(open(GEOJSON, encoding="utf-8"))
gl_feat = next(ft for ft in geo["features"]
               if (ft.get("properties") or {}).get("tfciSlug") == "greenland")
assert gl_feat["geometry"]["type"] in ("Polygon", "MultiPolygon"), \
    "greenland geometry is still a Point; run repair_greenland_geometry_v02.py first"

pill_cols = ["p1_subscore", "p2_subscore", "p3_subscore", "p4_subscore", "p5_subscore"]
pillar_sub = [round(sum(float(r[c]) for r in rows.values()) / 20) for c in pill_cols]

sector_slugs = ["utility-scale-renewables", "nuclear-clean-firm", "energy-storage-flexibility",
 "grid-modernization", "hydrogen-powerfuels", "carbon-markets", "critical-minerals",
 "water-security", "food-systems-agriculture", "ai-compute", "semiconductors",
 "advanced-manufacturing", "cyber-physical-security", "space-economy", "net-zero-mobility",
 "aviation-maritime", "buildings-heat", "smart-cities", "labor-transition",
 "digital-public-infrastructure"]
overall20 = [int(float(rows[s]["overall_score"])) for s in sector_slugs]
mat5x20 = [[int(float(rows[s]["p%d_subscore" % (i + 1)])) for s in sector_slugs]
           for i in range(5)]

GL_OUTLOOK = {
 "inv": ("Greenland executes selectively: hydropower plus waste-to-energy cover roughly 70% of "
         "utility sales with two new plants licensed in 2021 and an 85%-by-2030 target, all new oil "
         "and gas exploration was halted in July 2021, the December 2021 uranium-ban statute "
         "(Inatsisartutlov nr. 20) blocks the giant Kvanefjeld deposit, and in May 2026 the government "
         "approved Critical Metals taking a controlling stake in the Tanbreez rare-earth project, "
         "per public reporting."),
 "pri": ("Licenses are real but conditional - Tanbreez deadlines demand production by end-2028 while "
         "uranium-bearing deposits stay unmineable by statute. Infrastructure is fragmented across "
         "roughly 70 isolated localities with their own microgrids, and the September 2026 "
         "US-Denmark-Greenland security agreement raises long-horizon strategic exposure, "
         "per public reporting."),
}
GL_VETO = {"Critical Minerals": "regulatory moratorium: uranium exploration/mining ban, "
                                "Inatsisartutlov nr. 20 (Dec 2021)"}

# ------------------------------------------------------------------ html out
if not os.path.isfile(INPUT):
    sys.exit("Missing INPUT - run build_mockup_v091.py first.")
if os.path.exists(OUTPUT):
    sys.exit("Delete OUTPUT first - the generator never overwrites.")
html = open(INPUT, encoding="utf-8").read()

html, n = splice(html, "V83=", jz)
assert len(jz) == 208, "payload must hold 208 jurisdictions"

html, _ = splice(html, "F83=", geo["features"])

i = html.find("const DATA=")
if i == -1:
    i = html.find("DATA=")
assert i != -1
start = html.find("{", i)
data, end = DEC.raw_decode(html[start:])

countries = data["countries"]
assert not any(c["slug"] == "greenland" for c in countries), "greenland already in DATA.countries"
entry = {
    "slug": "greenland", "name": "Greenland", "iso2": "gl", "region": "N. America",
    "cadence": gl.get("sweepCadence", "Quarterly"), "tier": gl.get("recomputeTier", "T3"),
    "cred": gl["credibility"], "credBand": gl["credibilityBand"], "credRank": gl["credibilityRank"],
    "depl": gl["deployment"], "deplBand": gl["deploymentBand"], "deplRank": gl["deploymentRank"],
}
pos = next((k for k, c in enumerate(countries) if c.get("credRank", 10 ** 6) > entry["credRank"]),
           len(countries))
countries.insert(pos, entry)

data["pillars"]["greenland"] = {"sub": pillar_sub, "vetoes": [0, 0, 0, 0, 0]}
data["secScores"]["greenland"] = {"overall": overall20, "pillars": mat5x20}
data["vetoes"]["greenland"] = GL_VETO
data["outlooks"]["greenland"] = GL_OUTLOOK

html = html[:start] + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + html[start + end:]

html = html.replace("Show All 207", "Show All 208", 1)

# ------------------------------------------------------------------ B: perPage leak root-fix
NEW_FN = (
 "function expandAndResort(){"
 "if(!expanded){"
 "expanded=true;"
 "var pp=document.getElementById('perPage');"
 "window.cap92={origPerPage:(pp?pp.value:'25')};"
 "try{if(typeof state!=='undefined'){"
 "try{state.perPage=V83.length}catch(e0){}"
 "try{state.page=1}catch(e1){}"
 "}}catch(e2){}"
 "try{if(typeof render==='function')render();}catch(e3){}"
 "}"
 "ensureCapColumn();applySort();"
 "}")
html, old_fn = replace_function(html, "expandAndResort", NEW_FN)
html = html.replace(NEW_FN,
    NEW_FN + "\nwindow.restoreViewLimit=function(){"
    "if(!window.cap92)return;"
    "var pp=document.getElementById('perPage');"
    "try{if(typeof state!=='undefined'){"
    "state.perPage=parseInt(window.cap92.origPerPage,10)||25;"
    "state.page=1;}}catch(e){}"
    "if(pp)pp.value=window.cap92.origPerPage;"
    "delete window.cap92;expanded=false;"
    "try{if(typeof render==='function')render();}catch(e4){}"
    "try{ensureCapColumn();applyMapFilters();}catch(e5){}"
    "};", 1)

V092B_JS = ("<script>\n/* v092b view-limit reconciliation: leave sorted expanded mode cleanly */\n"
 "(function(){\n"
 "  function rel(){ if(window.cap92 && typeof window.restoreViewLimit==='function'){"
 " setTimeout(window.restoreViewLimit,0); } }\n"
 "  ['fRegion','fSector','fPillar','fBand'].forEach(function(id){\n"
 "    var el=document.getElementById(id); if(el) el.addEventListener('change', rel); });\n"
 "  var r=document.getElementById('fReset'); if(r) r.addEventListener('click', rel);\n"
 "  ['mCred','mDepl'].forEach(function(id){ var el=document.getElementById(id); "
 "if(el) el.addEventListener('click', rel); });\n"
 "  var pp=document.getElementById('perPage'); if(pp) pp.addEventListener('change', rel);\n"
 "  document.querySelectorAll('.pager button').forEach(function(b){ "
 "b.addEventListener('click', rel); });\n"
 "  window.addEventListener('load', rel);\n"
 "})();\n</script>\n")
i = html.rfind("</body>")
assert i != -1
html = html[:i] + V092B_JS + html[i:]

# ------------------------------------------------------------------ verify
checks = {
 "v83 has greenland": '"slug":"greenland"' in html,
 "f83 has greenland polygon": '"tfciSlug":"greenland"' in html and '"MultiPolygon"' == gl_feat["geometry"]["type"],
 "countries +1": '"name":"Greenland"' in html,
 "pillars patched": '"greenland":{"sub":' in html,
 "outlook + veto text": "Inatsisartutlov nr. 20" in html,
 "label 208": "Show All 208" in html,
 "perPage stash wired": "window.cap92" in html and "restoreViewLimit" in html,
 "reconcile layer": "v092b view-limit reconciliation" in html,
}
bad = [k for k, v in checks.items() if not v]
for k, v in checks.items():
    print(("PASS " if v else "FAIL ") + k)
if bad:
    sys.exit("verification failed: " + ", ".join(bad))

if shutil.which("node"):
    segs = list(re.finditer(r"<script[^>]*>", html))
    for i, t in enumerate(segs):
        e = html.find("</script>", t.end())
        tmp = os.path.join(ROOT, "v092bseg%d.js" % i)
        open(tmp, "w", encoding="utf-8").write(html[t.end():e])
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        os.remove(tmp)
        if r.returncode != 0:
            sys.exit("node --check FAIL on script %d: %s" % (i, r.stderr[:400]))
    print("node --check: all %d inline scripts OK" % len(segs))
else:
    print("node not found - structural checks only (browser is the final gate)")

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    f.write(html)
print()
print("WROTE", os.path.basename(OUTPUT), os.path.getsize(OUTPUT), "bytes")
print("Open with Ctrl+Shift+R / hard refresh.")

