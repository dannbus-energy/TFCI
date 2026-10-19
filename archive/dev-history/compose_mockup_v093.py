#!/usr/bin/env python3
"""
compose_mockup_v093.py - visual overhaul + sort root-fix.

Input : mockups/TFCI_Dashboard_Mockup_v0.9.2.html   (run compose_mockup_v092c.py first)
Output: mockups/TFCI_Dashboard_Mockup_v0.9.3.html

SORT ROOT-FIX: viewRows() data-level sort (no more expandAndResort for normal columns).
P0: hero masthead, legend card, KPI strip (credibility gap), SVG flags in table, tabular-nums.
P1: presenter mode, '/' focus + Esc, removable filter chips.
"""
import csv, json, os, re, sys

ROOT = r"C:\dev\tfci"
MOCK = os.path.join(ROOT, "mockups")
INPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.2.html")
OUTPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.3.html")
PAYLOAD = os.path.join(ROOT, "data", "TFCI_frontend_payload_v2.json")
VETOES = os.path.join(ROOT, "data", "veto_ledger.csv")

if not os.path.isfile(INPUT):
    sys.exit("Missing v0.9.2 - run compose_mockup_v092c.py first.")
if os.path.exists(OUTPUT):
    sys.exit("Delete OUTPUT first - generator never overwrites.")

html = open(INPUT, encoding="utf-8").read()

# ------------------------------------------------------------ KPI numbers
payload = json.load(open(PAYLOAD, encoding="utf-8"))
jz = payload["jurisdictions"]
ratios = [j["executionRatio"] for j in jz if j.get("executionRatio") is not None]
mean_ratio = sum(ratios) / len(ratios) if ratios else None
cap_sum = sum(j["capital"]["activeCapitalUsdBn"] for j in jz
              if (j.get("capital") or {}).get("activeCapitalUsdBn") is not None)
veto_n = 0
with open(VETOES, newline="", encoding="utf-8") as f:
    rd = list(csv.DictReader(f))
    if rd and "status" in rd[0]:
        veto_n = sum(1 for r in rd if (r.get("status") or "").lower() == "active")
    else:
        veto_n = len(rd)

KPI_HTML = (
 '<div id="kpiStrip">'
 '<div class="kpi"><div class="kv">%d</div><div class="kl">Jurisdictions x 20 sectors x 5 pillars</div></div>'
 '<div class="kpi"><div class="kv">%s</div><div class="kl">Global execution ratio (commissioned / announced)</div>'
 '<div class="kn">live in %d jurisdiction(s)</div></div>'
 '<div class="kpi accent"><div class="kv">%s</div><div class="kl">Credibility gap (1 - ratio)</div>'
 '<div class="kn">the headline chasm</div></div>'
 '<div class="kpi"><div class="kv">$%.1fbn</div><div class="kl">Active capital tracked</div></div>'
 '<div class="kpi"><div class="kv">%d</div><div class="kl">Active structural vetoes</div></div>'
 '</div>'
) % (len(jz),
     ("%.0f%%" % (mean_ratio * 100)) if mean_ratio is not None else "n/a",
     len(ratios),
     ("%.0f%%" % ((1 - mean_ratio) * 100)) if mean_ratio is not None else "n/a",
     cap_sum, veto_n)

i = html.find('<div class="countline"')
assert i != -1
html = html[:i] + KPI_HTML + html[i:]

# ------------------------------------------------------------ hero masthead
NEW_HEADER = (
 '<header><div class="heroL">'
 '<h1>Transition Finance Credibility Index</h1>'
 '<p class="tagline">Execution, not intent - %d jurisdictions x 20 sectors x 5 pillars.</p>'
 '</div><div class="heroR">'
 '<span class="hmeta">v0.9.3 &middot; snapshot as-of 2026-09-14 &middot; coverage %d/%d</span>'
 '</div></header>'
) % (len(jz), len(jz), len(jz))
html2, nsub = re.subn(r"<header>.*?</header>", NEW_HEADER, html, count=1, flags=re.S)
assert nsub == 1, "header block not replaced"
html = html2

# ------------------------------------------------------------ data-level sort
pat = re.compile(r"rows\.sort\(\(a,b\)\s*=>\s*b\.score-a\.score\|\|a\.name\.localeCompare\(b\.name\)\)")
m = pat.search(html)
assert m, "viewRows sort line not found"
html = pat.sub(
 "rows.sort((a,b)=>(window.tfCmp?window.tfCmp(a,b):(b.score-a.score||a.name.localeCompare(b.name))))",
 html, count=1)

# ------------------------------------------------------------ CSS
CSS = """<style id="v093-styles">
/* --- hero --- */
header{background:#ffffff!important;color:#0b2545!important;justify-content:flex-start!important;
  display:flex;align-items:center;gap:24px;padding:20px 32px;border-bottom:1px solid #e2e8f0}
header .heroL h1{font-size:30px;font-weight:700;letter-spacing:-0.01em;color:#0b2545;
  text-align:left;width:auto;margin:0}
header .tagline{font-size:14px;color:#64748b;margin:4px 0 0}
header .heroR{margin-left:auto}
header .hmeta{font-size:12px;color:#64748b;border:1px solid #e2e8f0;border-radius:6px;
  padding:6px 10px;background:#f8fafc;white-space:nowrap}
header .tag,header .ver{display:none!important}
/* --- KPI strip --- */
#kpiStrip{display:flex;gap:12px;flex-wrap:wrap;margin:2px 0 12px}
.kpi{flex:1;min-width:170px;background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px}
.kpi.accent{border-color:#0b6b4f}
.kv{font-size:22px;font-weight:800;color:#0f172a;font-variant-numeric:tabular-nums}
.kl{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
.kn{font-size:11px;color:#94a3b8;margin-top:2px}
/* --- legend --- */
.map-legend{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px;
  font-size:11px;color:#334155;margin-top:8px;display:flex;gap:14px;flex-wrap:wrap;align-items:center}
.map-legend .sw{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;
  vertical-align:-1px;border:1px solid rgba(0,0,0,.15)}
/* --- flags + numerals --- */
.tfFlag{width:18px;height:13px;border-radius:2px;margin-right:6px;vertical-align:-2px;
  border:1px solid rgba(0,0,0,.08)}
.tblwrap td{font-variant-numeric:tabular-nums}
.tblwrap td.scorecell,.tblwrap td.cap83{text-align:right}
.tblwrap tbody td{font-size:14px}
/* --- chips --- */
#tfChips{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 8px}
.tfchip{font-size:12px;background:#eef2ff;border:1px solid #c7d2fe;color:#1e293b;border-radius:99px;
  padding:3px 10px;cursor:pointer}
.tfchip:hover{background:#e0e7ff}
/* --- presenter --- */
#presentBtn{margin-left:8px}
body.present{font-size:115%}
body.present .tblwrap tbody td{font-size:16px}
body.present .map-mark{stroke-width:1.6}
body.present .kv{font-size:28px}
</style>
"""
i = html.rfind("</head>")
assert i != -1
html = html[:i] + CSS + html[i:]

# ------------------------------------------------------------ chips container
i = html.find('<div class="tblwrap"')
assert i != -1
html = html[:i] + '<div id="tfChips"></div>' + html[i:]

# ------------------------------------------------------------ JS layer
JS = """<script id="v093-app">
/* v093: data-level sort, flags, legend, chips, presenter, keyboard */
(function(){
'use strict';
/* ---------- 1. sort state + comparator (consumed by patched viewRows) ---------- */
window.tfSortState={col:-1,dir:'desc'};
function bandOfLocal(s){return s>=75?'HIGH':s>=50?'MEDIUM':'LOW';}
function colVal(r,c){
  switch(c){
    case 0:return r.rank||0;
    case 1:return (r.name||'').toLowerCase();
    case 2:return (r.region||'').toLowerCase();
    case 3:return r.score==null?null:r.score;
    case 4:return {'LOW':0,'MEDIUM':1,'HIGH':2}[(typeof bandOf==='function'?bandOf(r.score):bandOfLocal(r.score))];
    case 5:try{var P=DATA.pillars[r.slug];return P&&P.vetoes?P.vetoes.reduce(function(a,b){return a+b;},0):0;}catch(e){return 0;}
    case 6:return r.cred==null?null:r.cred;
    case 7:return r.depl==null?null:r.depl;
  }
  return null;
}
window.tfCmp=function(a,b){
  var s=window.tfSortState;
  if(!s||s.col<0||s.col>7) return b.score-a.score||a.name.localeCompare(b.name);
  var va=colVal(a,s.col), vb=colVal(b,s.col);
  if(va==null&&vb==null)return 0;
  if(va==null)return 1;   /* nulls always last */
  if(vb==null)return -1;
  var cmp=(typeof va==='number'&&typeof vb==='number')?va-vb:String(va).localeCompare(String(vb));
  return s.dir==='asc'?cmp:-cmp;
};
/* ---------- 2. capture-phase header clicks: legacy sorter never fires ---------- */
function installSort(){
  var tbl=document.querySelector('.tblwrap table')||document.querySelector('table');
  if(!tbl||tbl.getAttribute('data-tf093'))return;
  tbl.setAttribute('data-tf093','1');
  tbl.addEventListener('click',function(e){
    var th=e.target&&e.target.closest?e.target.closest('th'):null;
    if(!th||!tbl.contains(th))return;
    if(/capital/i.test(th.textContent))return;   /* capital keeps legacy handler */
    e.preventDefault();e.stopPropagation();
    var idx=th.cellIndex;
    var s=window.tfSortState;
    if(s.col===idx){s.dir=(s.dir==='asc'?'desc':'asc');}
    else{s.col=idx;s.dir=(idx===1||idx===2)?'asc':'desc';}
    var ths=tbl.tHead?tbl.tHead.rows[0].cells:[];
    for(var i=0;i<ths.length;i++)ths[i].removeAttribute('aria-sort');
    th.setAttribute('aria-sort',s.dir==='asc'?'ascending':'descending');
    try{if(typeof state!=='undefined')state.page=1;}catch(e2){}
    if(typeof render==='function')render();
  },true);
}
/* ---------- 3. flags in table rows ---------- */
var isoByName=null;
function ensureIsoMap(){
  if(isoByName)return;
  isoByName={};
  DATA.countries.forEach(function(c){isoByName[c.name]=c.iso2;});
}
function addFlags(){
  ensureIsoMap();
  var tb=document.querySelector('.tblwrap tbody')||document.querySelector('tbody');
  if(!tb)return;
  Array.prototype.slice.call(tb.rows).forEach(function(tr){
    var td=tr.cells[1];
    if(!td||td.querySelector('img.tfFlag'))return;
    var name=td.textContent.replace(/^\\s+|\\s+$/g,'');
    var iso=isoByName[name];
    if(!iso)return;
    var img=document.createElement('img');
    img.className='tfFlag';
    img.src='../assets/flags/'+iso.toLowerCase()+'.svg';
    img.alt='';
    img.onerror=function(){img.style.display='none';};
    td.insertBefore(img,td.firstChild);
  });
}
/* ---------- 4. legend under map ---------- */
function addLegend(){
  var box=document.getElementById('map8box');
  if(!box||box.querySelector('.map-legend'))return;
  var d=document.createElement('div');
  d.className='map-legend';
  d.innerHTML='<span><span class="sw" style="background:#166534"></span>HIGH (75+)</span>'
    +'<span><span class="sw" style="background:#b45309"></span>MEDIUM (50-74)</span>'
    +'<span><span class="sw" style="background:#b91c1c"></span>LOW (&lt;50)</span>'
    +'<span><span class="sw" style="background:#94a3b8"></span>not yet swept</span>';
  box.appendChild(d);
}
/* ---------- 5. filter chips ---------- */
function renderChips(){
  var box=document.getElementById('tfChips');
  if(!box)return;
  var parts=[];
  function chip(id,label,reset){
    parts.push('<span class="tfchip" data-fid="'+id+'">'+label+' &times;</span>');
  }
  var fr=document.getElementById('fRegion'),fs=document.getElementById('fSector'),
      fp=document.getElementById('fPillar'),fb=document.getElementById('fBand');
  if(fr&&fr.value!=='all')chip('fRegion','Region: '+fr.options[fr.selectedIndex].text);
  if(fs&&fs.value&&fs.value!=='all-sectors')chip('fSector','Sector: '+fs.options[fs.selectedIndex].text);
  if(fp&&fp.value&&fp.value!=='none')chip('fPillar','Pillar: '+fp.options[fp.selectedIndex].text);
  if(fb&&fb.value!=='all')chip('fBand','Band: '+fb.value);
  box.innerHTML=parts.join('');
  box.querySelectorAll('.tfchip').forEach(function(ch){
    ch.addEventListener('click',function(){
      var el=document.getElementById(ch.getAttribute('data-fid'));
      if(!el)return;
      el.value=(ch.getAttribute('data-fid')==='fSector')?'all-sectors'
              :(ch.getAttribute('data-fid')==='fPillar')?'none':'all';
      el.dispatchEvent(new Event('change'));
    });
  });
}
/* ---------- 6. presenter + keyboard ---------- */
function installExtras(){
  var f=document.querySelector('.filters');
  if(f&&!document.getElementById('presentBtn')){
    var b=document.createElement('button');
    b.id='presentBtn';b.className='sbtn';b.textContent='Presenter';
    b.addEventListener('click',function(){document.body.classList.toggle('present');});
    f.appendChild(b);
  }
  document.addEventListener('keydown',function(e){
    if(e.key==='/'&&!/INPUT|TEXTAREA/.test((e.target||{}).tagName||'')){
      e.preventDefault();
      var j=document.getElementById('jumpBox');if(j)j.focus();
    }
    if(e.key==='Escape'){
      var p=document.getElementById('panel');
      if(p&&p.style.display!=='none')p.style.display='none';
    }
  });
}
/* ---------- 7. post-render hook via MutationObserver ---------- */
function afterRender(){
  addFlags();
  renderChips();
  try{if(window.cap83&&window.cap83.ensureCapColumn)window.cap83.ensureCapColumn();}catch(e){}
}
function boot(){
  installSort();installExtras();addLegend();afterRender();
  var tb=document.querySelector('.tblwrap tbody')||document.querySelector('tbody');
  if(tb)new MutationObserver(function(){afterRender();}).observe(tb,{childList:true});
  ['fRegion','fSector','fPillar','fBand'].forEach(function(id){
    var el=document.getElementById(id);
    if(el)el.addEventListener('change',function(){setTimeout(afterRender,0);});
  });
  /* retry until map box exists (created by legacy layer on load) */
  var tries=0;
  var t=setInterval(function(){addLegend();if(document.getElementById('map8box')||++tries>20)clearInterval(t);},300);
}
if(document.readyState==='complete')boot();
else window.addEventListener('load',boot);
setTimeout(boot,800);
})();
</script>
"""
i = html.rfind("</body>")
assert i != -1
html = html[:i] + JS + html[i:]

# ------------------------------------------------------------ verify
checks = {
 "hero replaced": "heroL" in html and "Execution, not intent" in html,
 "kpi strip": 'id="kpiStrip"' in html,
 "sort root-fix": "window.tfCmp?window.tfCmp" in html,
 "capture sort": "data-tf093" in html,
 "flags": "tfFlag" in html,
 "legend": "map-legend" in html,
 "chips": 'id="tfChips"' in html,
 "presenter": "presentBtn" in html,
 "app layer": 'id="v093-app"' in html,
 "counts 208": "%d jurisdictions x 20" % len(jz) in html,
}
bad = [k for k, v in checks.items() if not v]
for k, v in checks.items():
    print(("PASS " if v else "FAIL ") + k)
if bad:
    sys.exit("verification failed: " + ", ".join(bad))

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    f.write(html)
print()
print("WROTE", os.path.basename(OUTPUT), os.path.getsize(OUTPUT), "bytes")
print("Open with Ctrl+Shift+R. Test: sort by Score, then Region, then Reset - pagination must hold.")

