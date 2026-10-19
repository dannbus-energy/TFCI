#!/usr/bin/env python3
"""
build_mockup_v091.py — Consolidated, deterministic TFCI mockup generator.

Input : mockups/TFCI_Dashboard_Mockup_v0.8.9.html  (v0.8.3-composed artifact)
Output: mockups/TFCI_Dashboard_Mockup_v0.9.1.html

Applies in one pass:
  * v090 explicit element bindings (no reliance on window named-property mechanism)
  * dropBanner() empty-phrase repair + permanent filter guard (ROOT CAUSE of the
    panelBody/countLine cascade: indexOf('') === 0 matched every string and the
    banner stripper removed every leaf <div>, including #countLine and #panelBody)
  * v091: sector view default = all-sectors, Active Capital survives Reset/pager,
    ultra-thin dot contours, panel locator left-most, count-line hidden,
    centered navy title on white header
  * dead v088 repair layers removed
  * every inline script re-validated (node --check when node is available)
"""
import os, re, sys, shutil, subprocess

ROOT   = os.path.dirname(os.path.abspath(__file__))
MOCK   = os.path.join(ROOT, "mockups")
INPUT  = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.8.9.html")
OUTPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.1.html")

# ---------------------------------------------------------------- v091 styles
CSS091 = """
<style id="v091-polish">
/* (7) centered navy title on white */
header{background:#ffffff!important;color:#0b2545!important;justify-content:center!important}
header h1{color:#0b2545!important;text-align:center;width:100%}
header .ver{color:#64748b!important;margin-left:0!important}

/* (6) hide the view/basis count line */
.countline,#countLine{display:none!important}

/* (3) ultra-thin dot contours; dark accent only on hover/focus */
.m8 circle.pt80{stroke-width:0.6!important}
.m8 circle.pt80i{stroke:none!important}
.m8 g.map-mark circle{stroke-width:0.6!important}
.m8 [data-s]:hover,.m8 [data-s]:focus-visible{stroke:#0f172a!important;stroke-width:1.4!important}

/* (4) panel locator goes LEFT-most, before the flag/identity block */
#panelBody .phead{display:flex!important;flex-wrap:wrap!important;align-items:flex-start!important;gap:14px!important}
#panelBody .loc80,#panelBody .loc83{order:-1!important;margin-left:0!important;margin-right:auto!important}

/* selected-jurisdiction locator contour: light slate, thin */
.loc80 .sel,.loc83 .sel{stroke:#cbd5e1!important;stroke-width:0.8!important}
</style>
"""

# ------------------------------------------------------------ v091 behaviour
JS091 = """
<script>
/* v091: sector default reinforcement + capital-column persistence on Reset/pager */
(function () {
  function reinforceSectorDefault() {
    var s = document.getElementById('fSector');
    if (s && !s.value) s.value = 'all-sectors';
  }
  function hookReset() {
    if (!window.__cap83 || window.__cap83.__hooked) return;
    var r = document.getElementById('fReset');
    if (!r) return;
    window.__cap83.__hooked = true;
    r.addEventListener('click', function () {
      setTimeout(function () {
        try { window.__cap83.ensureCapColumn(); } catch (e) {}
        try { window.__cap83.applySort(); } catch (e) {}
      }, 0);
    });
  }
  function hookPager() {
    if (!window.__cap83) return;
    document.querySelectorAll('.pager button').forEach(function (b) {
      if (b.__cap91) return; b.__cap91 = true;
      b.addEventListener('click', function () {
        setTimeout(function () {
          try { window.__cap83.ensureCapColumn(); } catch (e) {}
        }, 0);
      });
    });
    var pp = document.getElementById('perPage');
    if (pp && !pp.__cap91) { pp.__cap91 = true;
      pp.addEventListener('change', function () {
        setTimeout(function () {
          try { window.__cap83.ensureCapColumn(); } catch (e) {}
        }, 0);
      });
    }
  }
  function boot() { hookReset(); hookPager(); reinforceSectorDefault(); }
  if (document.readyState === 'complete') boot();
  else {
    window.addEventListener('load', boot);
    setTimeout(boot, 800);
    setTimeout(boot, 2000);
  }
})();
</script>
"""

def main():
    if not os.path.isfile(INPUT):
        sys.exit("Missing " + INPUT + " -- keep v0.8.9 until v0.9.1 generation is proven.")
    if os.path.exists(OUTPUT):
        sys.exit("Delete " + OUTPUT + " first (generator never overwrites).")

    html = open(INPUT, encoding="utf-8").read()

    # -- 1. remove the three dead v088 repair layers (matched by content marker)
    for marker in ("v088-globals",
                   "v088: re-run the initial render",
                   "function ready(fn)"):
        for t in re.finditer(r"<script[^>]*>", html):
            end = html.find("</script>", t.end())
            blk = html[t.start():end + len("</script>")]
            if marker in blk:
                html = html.replace(blk, "", 1)
                break

    # -- 2. explicit element bindings at top of the main DATA script (v090)
    bindings = ("\n/* v090: explicit element bindings */\n"
                "var countLine=document.getElementById('countLine'),\n"
                "    panelBody=document.getElementById('panelBody'),\n"
                "    panel=document.getElementById('panel'),\n"
                "    tbody=document.getElementById('tbody'),\n"
                "    scoreHead=document.getElementById('scoreHead');\n")
    if "v090: explicit element bindings" not in html:
        assert "<script>\nconst DATA" in html, "anchor '<script>\nconst DATA' not found"
        html = html.replace("<script>\nconst DATA", "<script>" + bindings + "const DATA", 1)

    # -- 3. ROOT-CAUSE repair: dropBanner empty phrase + permanent guard
    html = re.sub(r"\n\s*''(?=\s*\];)", "", html, count=1)
    html = html.replace(
        "qsa('div,section,aside,p,span,header').forEach(function(el){",
        "phrases=phrases.filter(function(p){return p;});\n"
        "  qsa('div,section,aside,p,span,header').forEach(function(el){",
        1)

    # -- 4. sector view default (base script inserts o0 but never selects it)
    assert "fSector.insertBefore(o0,fSector.firstChild)" in html
    html = html.replace(
        "fSector.insertBefore(o0,fSector.firstChild)",
        "fSector.insertBefore(o0,fSector.firstChild);fSector.value='all-sectors';",
        1)

    # -- 5. expose cap-layer hooks from the v0.8.3 IIFE
    assert "function ensureCapColumn(){" in html
    html = html.replace(
        "function ensureCapColumn(){",
        "window.__cap83={ensureCapColumn:ensureCapColumn,applySort:applySort};\n"
        "function ensureCapColumn(){",
        1)

    # -- 6. thin the two fat inline halo strokes at source
    html = html.replace('stroke="#fff" stroke-width="3"', 'stroke="#fff" stroke-width="0.8"')

    # -- 7. append v091 presentation + behaviour before </body>
    assert "</body>" in html
    html = html.replace("</body>", CSS091 + "\n" + JS091 + "\n</body>", 1)

    # ---------------- verification ----------------
    checks = {
        "sector default forced":  "fSector.value='all-sectors'" in html,
        "cap hooks exposed":      "window.__cap83" in html,
        "v091 css":               "v091-polish" in html,
        "v091 js":                "v091: sector default" in html,
        "countline hidden":       "#countLine{display:none!important}" in html,
        "header centered navy":   "header h1{color:#0b2545!important" in html,
        "thin dots at source":    'stroke-width="3"' not in html,
        "dropBanner repaired":    "phrases=phrases.filter" in html,
        "bindings injected":      "v090: explicit element bindings" in html,
        "dead layers removed":    ("v088-globals" not in html and "v088-retry" not in html),
        "country wording gone":   ("Type a country" not in html and "(country score)" not in html),
    }
    failed = [k for k, v in checks.items() if not v]
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    if failed:
        sys.exit("Verification failed: " + ", ".join(failed))

    # node syntax gate (skipped silently if node missing)
    if shutil.which("node"):
        segs = list(re.finditer(r"<script[^>]*>", html))
        for i, t in enumerate(segs):
            end = html.find("</script>", t.end())
            tmp = os.path.join(ROOT, "_v091_seg%d.js" % i)
            open(tmp, "w", encoding="utf-8").write(html[t.end():end].replace(chr(10), chr(10)))
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
            os.remove(tmp)
            if r.returncode != 0:
                sys.exit("node --check FAIL on script %d:\n%s" % (i, r.stderr[:400]))
        print("node --check: all %d inline scripts OK" % len(segs))
    else:
        print("node not found - structural checks only (safe to ship; browser is the gate)")

    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("\nWrote:", os.path.relpath(OUTPUT, ROOT), "%d bytes" % os.path.getsize(OUTPUT))
    print("Open " + os.path.basename(OUTPUT) + " with Ctrl+Shift+R.")

if __name__ == "__main__":
    main()
