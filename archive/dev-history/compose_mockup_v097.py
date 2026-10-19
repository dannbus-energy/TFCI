#!/usr/bin/env python3
"""
compose_mockup_v097.py - fixes on top of v0.9.6.

Input : mockups/TFCI_Dashboard_Mockup_v0.9.6.html
Output: mockups/TFCI_Dashboard_Mockup_v0.9.7.html

1. Remove the drop-shadow halo from the white hover contour (plain white stroke).
2. Tooltip no longer lingers: global pointer tracker - if the pointer is not over a
   jurisdiction shape at any moment, tooltip + highlight clear (catches fast moves
   where mouseout never fires on the shape itself).
3. Header row: neutralize v096's faulty reorderHeader (it deleted the Jurisdiction th
   after reordering) and REBUILD the thead to exactly:
   Jurisdiction | Region | Credibility | Score | Deployment | Band | Vetoes | Active capital
   preserving any existing .tip tooltip spans per label.
4. Presenter restyled as a grey/green toggle pill.
"""
import os, sys

ROOT = r"C:\dev\tfci"
MOCK = os.path.join(ROOT, "mockups")
INPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.6.html")
OUTPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.7.html")

if not os.path.isfile(INPUT):
    sys.exit("Missing v0.9.6 - run compose_mockup_v096.py first.")
if os.path.exists(OUTPUT):
    sys.exit("Delete OUTPUT first - generator never overwrites.")
html = open(INPUT, encoding="utf-8").read()

# --- 3a. neutralize the faulty v096 header path (it deletes the wrong th after reorder)
n = html.count("reorderHeader();reorderRows();")
assert n == 1, "expected one v096 decorate call, found %d" % n
html = html.replace("reorderHeader();reorderRows();", "reorderRows();")

CSS = """<style id="v097-styles">
/* 1. no shadow on white hover contour */
.m8 .map-hl path,.m8 path.map-hl{filter:none!important}
.m8 g.map-mark.map-hl circle{filter:none!important}
/* 4. presenter as grey/green toggle */
#presentBtn{border-radius:99px!important;border:none!important;background:#94a3b8!important;
  color:#ffffff!important;cursor:pointer}
body.present #presentBtn{background:#166534!important}
</style>
"""
i = html.rfind("</head>")
assert i != -1
html = html[:i] + CSS + html[i:]

JS = """<script id="v097-app">
(function(){
'use strict';
/* ---------- 3. canonical header rebuild ---------- */
var LABELS=['Jurisdiction','Region','Credibility','Score','Deployment','Band','Vetoes','Active capital'];
function normHeader(){
  var tbl=document.querySelector('.tblwrap table')||document.querySelector('table');
  if(!tbl||!tbl.tHead)return;
  var row=tbl.tHead.rows[0];
  var ths=Array.prototype.slice.call(row.cells);
  /* idempotent: already canonical? */
  if(ths.length===8 && ths.every(function(th,i){return th.textContent.replace(/\\s+/g,' ').trim().indexOf(LABELS[i])===0;}))return;
  var tips={};
  ths.forEach(function(th){
    var tip=th.querySelector && th.querySelector('.tip');
    if(tip){var key=th.textContent.replace(/\\s+/g,' ').trim().split(' ')[0];tips[key]=tip;}
  });
  /* the empty rank th and any stray placeholders just die */
  row.innerHTML='';
  LABELS.forEach(function(lb){
    var th=document.createElement('th');th.textContent=lb;
    if(lb==='Active capital')th.id='capTH';
    var t=tips[lb]||tips[lb.split(' ')[0]];
    if(t)th.appendChild(t);
    row.appendChild(th);
  });
}
/* ---------- 2. hard tooltip dismissal ---------- */
function inMapMark(el){return !!(el&&el.closest&&el.closest('#map8 [data-s],#map8 [data-slug],#map8')) && !!(el.closest('[data-s],[data-slug]'));}
function pointerTrack(){
  document.addEventListener('mousemove',function(e){
    var svg=document.getElementById('map8');
    if(!svg)return;
    var inside=e.target&&e.target.closest?e.target.closest('[data-s],[data-slug]'):null;
    if(!inside){
      document.querySelectorAll('#map8 .map-hl').forEach(function(el){el.classList.remove('map-hl');});
      var t=document.getElementById('tfTip');
      if(t&&t.style.display!=='none')t.style.display='none';
    }
  },true);
  /* belt & braces: also clear when pointer leaves the document */
  document.addEventListener('mouseleave',function(){
    var t=document.getElementById('tfTip');if(t)t.style.display='none';
    document.querySelectorAll('#map8 .map-hl').forEach(function(el){el.classList.remove('map-hl');});
  });
}
function boot(){
  normHeader();
  var head=(document.querySelector('.tblwrap table')||document.querySelector('table'));
  if(head&&head.tHead&&!head.tHead.getAttribute('data-v097mo')){
    head.tHead.setAttribute('data-v097mo','1');
    new MutationObserver(normHeader).observe(head.tHead,{childList:true,subtree:true});
  }
  pointerTrack();
  var tb=document.querySelector('.tblwrap tbody');
  if(tb&&!tb.getAttribute('data-v097mo2')){
    tb.setAttribute('data-v097mo2','1');
    new MutationObserver(function(){setTimeout(normHeader,0);}).observe(tb,{childList:true});
  }
}
document.addEventListener('DOMContentLoaded',boot);
window.addEventListener('load',boot);
setTimeout(boot,600);setTimeout(boot,1700);
})();
</script>
"""
i = html.rfind("</body>")
assert i != -1
html = html[:i] + JS + html[i:]

checks = {
 "v096 faulty header call neutralized": "reorderHeader();reorderRows();" not in html,
 "shadow removed": "filter:none!important" in html,
 "canonical header rebuild": "LABELS=['Jurisdiction','Region','Credibility','Score','Deployment','Band','Vetoes','Active capital']" in html.replace("'", "'"),
 "tooltip pointer guard": "pointerTrack" in html,
 "presenter toggle colors": "body.present #presentBtn{background:#166534" in html,
 "app injected": 'id="v097-app"' in html,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS " if v else "FAIL ")+k)
if bad: sys.exit("verification failed: "+", ".join(bad))

with open(OUTPUT,"w",encoding="utf-8",newline="") as f: f.write(html)
print()
print("WROTE",os.path.basename(OUTPUT),os.path.getsize(OUTPUT),"bytes")
print("Verify: headers = Jurisdiction|Region|Credibility|Score|Deployment|Band|Vetoes|Active capital,")
print("plain white hover ring, tooltip dies the instant the pointer leaves the shape,")
print("Presenter = grey pill, green when on.")
