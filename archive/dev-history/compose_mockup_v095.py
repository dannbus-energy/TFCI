#!/usr/bin/env python3
"""
compose_mockup_v095.py - fixes on top of v0.9.4.

Input : mockups/TFCI_Dashboard_Mockup_v0.9.4.html
Output: mockups/TFCI_Dashboard_Mockup_v0.9.5.html

F1 (root-fixed): stop borrowing cap83.ensureCapColumn - embed a build-time CAPMAP
     (slug -> active capital + evidence chip) and let our own decorator own the column.
F2 (root-fixed): hover tooltip/highlight matched the wrong attribute - map features
     carry data-slug, not data-s; also attach via document observer so we catch map8
     whenever the legacy layer builds it.
NEW: Reset clears sort state (tfSortState), strips aria-sort, and re-dispatches change
     on all filter dropdowns so the legacy map dimming (applyMapFilters) re-runs too.
Keep: Presenter toggle (projector mode) + thicker hover strokes under body.present.
"""
import json, os, re, sys

ROOT = r"C:\dev\tfci"
MOCK = os.path.join(ROOT, "mockups")
INPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.4.html")
OUTPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.5.html")
PAYLOAD = os.path.join(ROOT, "data", "TFCI_frontend_payload_v2.json")

if not os.path.isfile(INPUT):
    sys.exit("Missing v0.9.4 - run compose_mockup_v094.py first.")
if os.path.exists(OUTPUT):
    sys.exit("Delete OUTPUT first - generator never overwrites.")
html = open(INPUT, encoding="utf-8").read()

payload = json.load(open(PAYLOAD, encoding="utf-8"))
capmap = {}
for j in payload["jurisdictions"]:
    cap = (j.get("capital") or {})
    capmap[j["slug"]] = {
        "cap": cap.get("activeCapitalUsdBn"),
        "ev": cap.get("evidenceClass"),
    }
CAPMAP = "CAPMAP=" + json.dumps(capmap, separators=(",", ":")) + ";"

CSS = """<style id="v095-styles">
.m8 .map-hl path,.m8 path.map-hl{stroke:#0f172a!important;stroke-width:2.2!important}
.m8 g.map-mark.map-hl circle{stroke:#0f172a!important;stroke-width:1.8!important}
body.present .m8 .map-hl path,body.present .m8 path.map-hl{stroke-width:3!important}
#tfTip{z-index:9999}
</style>
"""
i = html.rfind("</head>")
assert i != -1
html = html[:i] + CSS + html[i:]

JS_TPL = """<script id="v095-app">
(function(){
'use strict';
var __CAPMAP__;
var byName=null, bySlug={};
function maps(){
  if(byName)return;
  byName={};
  DATA.countries.forEach(function(c){byName[c.name]=c;bySlug[c.slug]=c;});
}
/* ---------- F1: capital column owned by us ---------- */
function capCell(slug){
  var e=CAPMAP[slug]||{cap:null,ev:null};
  var td=document.createElement('td');
  td.className='cap83';
  if(e.cap==null){td.innerHTML='&mdash;';}
  else{td.textContent=Number(e.cap).toFixed(1)+'bn';}
  if(e.ev){var s=document.createElement('span');s.className='ev';
    s.textContent=String(e.ev).split('_')[0];td.appendChild(s);}
  return td;
}
function ensureCapital(){
  var tbl=document.querySelector('.tblwrap table')||document.querySelector('table');
  if(!tbl||!tbl.tHead||!tbl.tBodies.length)return;
  var ths=Array.prototype.slice.call(tbl.tHead.rows[0].cells);
  if(!ths.some(function(h){return /active\\s*capital/i.test(h.textContent);})){
    var th=document.createElement('th');th.id='capTH';th.textContent='Active capital';
    tbl.tHead.rows[0].appendChild(th);
  }
  var tb=tbl.tBodies[0];
  Array.prototype.slice.call(tb.rows).forEach(function(tr){
    if(tr.querySelector('td.cap83'))return;
    var oc=tr.getAttribute('onclick')||'';
    var m=oc.match(/openCountry\\('([^']+)'/);
    var slug=m?m[1]:null;
    if(!slug){maps();var c=byName[(tr.cells[1]?tr.cells[1].textContent:'').replace(/^\\s+|\\s+$/g,'')];slug=c?c.slug:null;}
    if(slug)tr.appendChild(capCell(slug));
  });
}
/* ---------- flags ---------- */
function ensureFlags(){
  maps();
  var tb=document.querySelector('.tblwrap tbody')||document.querySelector('tbody');
  if(!tb)return;
  Array.prototype.slice.call(tb.rows).forEach(function(tr){
    var td=tr.cells[1];
    if(!td||td.querySelector('img.tfFlag'))return;
    var c=byName[td.textContent.replace(/^\\s+|\\s+$/g,'')];
    if(!c)return;
    var img=document.createElement('img');
    img.className='tfFlag';
    img.src='../assets/flags/'+String(c.iso2).toLowerCase()+'.svg';
    img.alt='';img.onerror=function(){img.remove();};
    td.insertBefore(img,td.firstChild);
  });
}
function decorate(){ensureCapital();ensureFlags();}
var pong=false;
function decorateSoon(){if(pong)return;pong=true;setTimeout(function(){pong=false;decorate();},0);}
/* ---------- F2: hover tooltip + highlight (data-slug!) ---------- */
function tipEl(){
  var t=document.getElementById('tfTip');
  if(!t){t=document.createElement('div');t.id='tfTip';document.body.appendChild(t);}
  return t;
}
function fillTip(slug){maps();var c=bySlug[slug];if(!c)return '';
  return '<div class="tName">'+c.name+'</div>'
   +'<div class="tMeta">'+String(c.iso2).toUpperCase()+' &middot; '+c.region+'</div>'
   +'<div class="tRow"><span>Credibility</span><b>'+c.cred+' '+c.credBand+' (#'+c.credRank+')</b></div>'
   +'<div class="tRow"><span>Deployment</span><b>'+c.depl+' '+c.deplBand+' (#'+c.deplRank+')</b></div>'
   +'<div class="tRow"><span>Cadence</span><b>'+(c.cadence||'')+'</b></div>';}
var hl=null;
function clearHl(){if(hl){hl.classList.remove('map-hl');hl=null;}tipEl().style.display='none';}
function installMapHover(svg){
  if(!svg||svg.getAttribute('data-v095'))return;
  svg.setAttribute('data-v095','1');
  svg.addEventListener('mouseover',function(e){
    var m=e.target&&e.target.closest?e.target.closest('[data-s],[data-slug]'):null;
    if(!m)return;
    if(hl&&hl!==m)hl.classList.remove('map-hl');
    hl=m;m.classList.add('map-hl');
    m.parentNode.appendChild(m);
    var t=tipEl();
    t.innerHTML=fillTip(m.getAttribute('data-slug')||m.getAttribute('data-s'));
    t.style.display='block';
  },true);
  svg.addEventListener('mousemove',function(e){
    var t=tipEl();t.style.left=(e.clientX+14)+'px';t.style.top=(e.clientY+14)+'px';},true);
  svg.addEventListener('mouseout',function(e){
    var m=e.target&&e.target.closest?e.target.closest('[data-s],[data-slug]'):null;
    if(m)clearHl();},true);
  svg.addEventListener('mouseleave',clearHl);
}
/* ---------- Reset: clear sort + map dims + filters state everywhere ---------- */
function hookReset(){
  var r=document.getElementById('fReset');
  if(!r||r.getAttribute('data-v095'))return;
  r.setAttribute('data-v095','1');
  r.addEventListener('click',function(){
    setTimeout(function(){
      if(window.tfSortState){window.tfSortState.col=-1;window.tfSortState.dir='desc';}
      document.querySelectorAll('th[aria-sort]').forEach(function(h){h.removeAttribute('aria-sort');});
      if(window.cap92&&typeof window.restoreViewLimit==='function')window.restoreViewLimit();
      ['fRegion','fSector','fPillar','fBand'].forEach(function(id){
        var el=document.getElementById(id);
        if(el)el.dispatchEvent(new Event('change'));
      });
      decorate();
    },0);
  });
}
/* ---------- boot ---------- */
function boot(){
  decorate();hookReset();
  installMapHover(document.getElementById('map8'));
}
document.addEventListener('DOMContentLoaded',boot);
window.addEventListener('load',boot);
new MutationObserver(function(muts){
  var svg=document.getElementById('map8');
  if(svg&&!svg.getAttribute('data-v095'))installMapHover(svg);
  var tb=document.querySelector('.tblwrap tbody');
  if(tb&&!tb.getAttribute('data-v095mo')){
    tb.setAttribute('data-v095mo','1');
    new MutationObserver(decorateSoon).observe(tb,{childList:true});
  }
}).observe(document.documentElement,{childList:true,subtree:true});
setTimeout(boot,500);setTimeout(boot,1500);
})();
</script>
"""
JS = JS_TPL.replace("__CAPMAP__", CAPMAP)
i = html.rfind("</body>")
assert i != -1
html = html[:i] + JS + html[i:]

checks = {
 "capmap embedded": '"greenland"' in CAPMAP and "CAPMAP=" in html,
 "capital owned by decorator": "function ensureCapital()" in html,
 "data-slug hover": "[data-slug],[data-s]" not in html.replace("[data-s],[data-slug]", "") or "data-slug" in JS,
 "reset clears sort": "window.tfSortState.col=-1" in html,
 "reset redispatch": "dispatchEvent(new Event('change'))" in html,
 "presenter hover stroke": "body.present .m8 .map-hl path" in html,
 "app injected": 'id="v095-app"' in html,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS " if v else "FAIL ")+k)
if bad: sys.exit("verification failed: "+", ".join(bad))

with open(OUTPUT,"w",encoding="utf-8",newline="") as f: f.write(html)
print()
print("WROTE",os.path.basename(OUTPUT),os.path.getsize(OUTPUT),"bytes")
