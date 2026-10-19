#!/usr/bin/env python3
"""
compose_mockup_v096.py - five refinements on top of v0.9.5.

Input : mockups/TFCI_Dashboard_Mockup_v0.9.5.html
Output: mockups/TFCI_Dashboard_Mockup_v0.9.6.html

1. Hover contour: white stroke (+dark drop-shadow halo so it reads on the white ocean).
2. Tooltip resets shape-scope: hides as soon as the pointer leaves the jurisdiction
   shape, not only on map leave.
3. Presenter button relocated: inside the map legend row, far left.
4. Reset unchanged (already good in v095).
5. Rank column REMOVED and columns reordered at the DOM level (template-independent):
   Jurisdiction - Region - Credibility - Score - Deployment - Band - Vetoes - Active Capital.
   window.tfCmp is remapped to the new column indices so sorting stays data-level.
"""
import os, re, sys

ROOT = r"C:\dev\tfci"
MOCK = os.path.join(ROOT, "mockups")
INPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.5.html")
OUTPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.6.html")

if not os.path.isfile(INPUT):
    sys.exit("Missing v0.9.5 - run compose_mockup_v095.py first.")
if os.path.exists(OUTPUT):
    sys.exit("Delete OUTPUT first - generator never overwrites.")
html = open(INPUT, encoding="utf-8").read()

CSS = """<style id="v096-styles">
/* 1. white hover contour, dark halo for contrast on white ocean */
.m8 .map-hl path,.m8 path.map-hl{
  stroke:#ffffff!important;stroke-width:2.4!important;
  filter:drop-shadow(0 0 2px rgba(15,23,42,.9))}
.m8 g.map-mark.map-hl circle{
  stroke:#ffffff!important;stroke-width:2!important;
  filter:drop-shadow(0 0 2px rgba(15,23,42,.9))}
body.present .m8 .map-hl path,body.present .m8 path.map-hl{stroke-width:3.2!important}
/* 3. presenter inside legend row, far left */
.map-legend #presentBtn{margin:0 12px 0 0;padding:4px 12px;height:26px;font-size:11px}
/* 5. rank column gone */
.tblwrap td.rank,.tblwrap th.rank{display:none!important}
.tblwrap tdnth-child(4),.tblwrap th:nth-child(4){text-align:left!important}
</style>
"""
i = html.rfind("</head>")
assert i != -1
html = html[:i] + CSS + html[i:]

JS = """<script id="v096-app">
(function(){
'use strict';
/* ---------- 5. column reorder (DOM-level, template-independent) ---------- */
var NEW_ORDER=[1,2,6,3,7,4,5];            /* of the first 8 pre-capital cells */
var NEW_HEAD =[1,2,6,3,7,4,5,8];          /* header incl. Active capital */
var CapRe=/active\\s*capital/i;
function reorderHeader(){
  var tbl=document.querySelector('.tblwrap table')||document.querySelector('table');
  if(!tbl||!tbl.tHead)return;
  var row=tbl.tHead.rows[0];
  if(row.getAttribute('data-v096'))return;
  var ths=Array.prototype.slice.call(row.cells);
  if(ths.length<8)return;                                  /* capital th may lag */
  if(ths.length===8){ths.splice(7,0,document.createElement('th'));} /* placeholder for cap */
  if(CapRe.test(ths[ths.length-1].textContent)===false && !/active/i.test(ths[8].textContent)){/*(capital th unlabeled placeholder - v095 will label it)*/}
  row.setAttribute('data-v096','1');
  var ordered=[];
  NEW_HEAD.forEach(function(ix){ if(ths[ix])ordered.push(ths[ix]); });
  ordered.forEach(function(th){row.appendChild(th);});
}
function reorderRows(){
  var tb=document.querySelector('.tblwrap tbody')||document.querySelector('tbody');
  if(!tb)return;
  Array.prototype.slice.call(tb.rows).forEach(function(tr){
    if(tr.getAttribute('data-v096'))return;
    var tds=Array.prototype.slice.call(tr.cells);
    if(tds.length<8)return;
    tr.setAttribute('data-v096','1');
    var ordered=[];
    NEW_ORDER.forEach(function(ix){ if(tds[ix])ordered.push(tds[ix]); });
    if(tds[8])ordered.push(tds[8]);                        /* existing capital cell */
    ordered.forEach(function(td){tr.appendChild(td);});
    if(tds[0])tds[0].remove();                             /* rank column out */
  });
  var row=(document.querySelector('.tblwrap table')||document.querySelector('table')).tHead.rows[0];
  if(row.cells[0])row.cells[0].remove();
}
/* sort state remapped to new column indices (overrides v093 comparator) */
function remapSort(){
  window.tfCmp=function(a,b){
    var s=window.tfSortState;
    if(!s||s.col<0)return b.score-a.score||a.name.localeCompare(b.name);
    function bandOfL(x){return x>=75?2:x>=50?1:0;}
    var va,vb;
    switch(s.col){
      case 0:va=(a.name||'').toLowerCase();vb=(b.name||'').toLowerCase();break;
      case 1:va=(a.region||'').toLowerCase();vb=(b.region||'').toLowerCase();break;
      case 2:va=a.cred;vb=b.cred;break;
      case 3:va=a.score;vb=b.score;break;
      case 4:va=a.depl;vb=b.depl;break;
      case 5:va=bandOfL(a.score);vb=bandOfL(b.score);break;
      case 6:try{va=DATA.pillars[a.slug].vetoes.reduce(function(p,q){return p+q;},0);}catch(e){va=0;}
             try{vb=DATA.pillars[b.slug].vetoes.reduce(function(p,q){return p+q;},0);}catch(e2){vb=0;}break;
      default:va=null;vb=null;
    }
    if(va==null&&vb==null)return 0;
    if(va==null)return 1;
    if(vb==null)return -1;
    var cmp=(typeof va==='number'&&typeof vb==='number')?va-vb:String(va).localeCompare(String(vb));
    return window.tfSortState.dir==='asc'?cmp:-cmp;
  };
}
/* ---------- 2. shape-scope tooltip dismissal ---------- */
function patchTooltip(){
  var svg=document.getElementById('map8');
  if(!svg||svg.getAttribute('data-v096tip'))return;
  svg.setAttribute('data-v096tip','1');
  svg.addEventListener('mouseout',function(e){
    var to=e.relatedTarget;
    var toMark=to&&to.closest?to.closest('[data-s],[data-slug]'):null;
    if(!toMark){
      document.querySelectorAll('.map-hl').forEach(function(el){el.classList.remove('map-hl');});
      var t=document.getElementById('tfTip');if(t)t.style.display='none';
    }
  },true);
}
/* ---------- 3. presenter into legend ---------- */
function placePresenter(){
  var lg=document.querySelector('.map-legend');
  var b=document.getElementById('presentBtn');
  if(lg&&b&&b.parentNode!==lg)lg.insertBefore(b,lg.firstChild);
}
/* ---------- boot ---------- */
function decorate(){
  reorderHeader();reorderRows();
  try{if(window.cap83&&window.cap83.ensureCapColumn)window.cap83.ensureCapColumn();}catch(e){}
  patchTooltip();
  placePresenter();
}
var busy=false;
function soon(){if(busy)return;busy=true;setTimeout(function(){busy=false;decorate();},0);}
remapSort();
function boot(){
  decorate();
  var tb=document.querySelector('.tblwrap tbody');
  if(tb&&!tb.getAttribute('data-v096mo')){
    tb.setAttribute('data-v096mo','1');
    new MutationObserver(soon).observe(tb,{childList:true});
  }
}
document.addEventListener('DOMContentLoaded',boot);
window.addEventListener('load',boot);
new MutationObserver(function(){
  if(!document.getElementById('map8'))return;
  patchTooltip();
  placePresenter();
}).observe(document.documentElement,{childList:true,subtree:true});
setTimeout(boot,500);setTimeout(boot,1500);
})();
</script>
"""
i = html.rfind("</body>")
assert i != -1
html = html[:i] + JS + html[i:]

checks = {
 "white hover stroke": "stroke:#ffffff!important" in html,
 "drop-shadow halo": "drop-shadow(0 0 2px rgba(15,23,42,.9))" in html,
 "tooltip shape-scope": "toMark" in html and "data-v096tip" in html,
 "presenter in legend": "lg.insertBefore(b,lg.firstChild)" in html,
 "rank hidden css": "td.rank,.tblwrap th.rank" in html.replace(" ", "") or "td.rank" in html,
 "column reorder": "NEW_ORDER=[1,2,6,3,7,4,5]" in html,
 "tfCmp remapped": "case 2:va=a.cred" in html,
 "app injected": 'id="v096-app"' in html,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS " if v else "FAIL ")+k)
if bad: sys.exit("verification failed: "+", ".join(bad))

with open(OUTPUT,"w",encoding="utf-8",newline="") as f: f.write(html)
print()
print("WROTE",os.path.basename(OUTPUT),os.path.getsize(OUTPUT),"bytes")
print("Verify: hover=white stroke, tooltip vanishes on shape exit; Presenter sits in legend row;")
print("columns read Jurisdiction|Region|Credibility|Score|Deployment|Band|Vetoes|Active Capital;")
print("sort each column incl. Credibility & Deployment; first numeric rank col gone.")
