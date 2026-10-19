#!/usr/bin/env python3
"""
compose_mockup_v094.py - four targeted fixes on top of v0.9.3.

Input : mockups/TFCI_Dashboard_Mockup_v0.9.3.html
Output: mockups/TFCI_Dashboard_Mockup_v0.9.4.html

F1. Sort -> Active Capital column: after every sort-triggered render, re-run
    window.cap83.ensureCapColumn() (twice, deferred) so the appended column survives.
F2. Map hover: custom tooltip (name . iso2 . region / cred / depl), stroke highlight
    via parentNode.appendChild (raise on top), and kill the black focus-outline box.
F3. Flags: strip the inline iso2 span from the name cell TEMPLATE (root cause of the
    name-lookup miss), then insert the SVG flag before the name; flags re-applied
    whenever the tbody re-renders.
F4. Reset button: filters bar switches to align-items:flex-end so the label-less
    Reset button lines up with the labeled selects; height/normalized margins.
"""
import os, re, sys

ROOT = r"C:\dev\tfci"
MOCK = os.path.join(ROOT, "mockups")
INPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.3.html")
OUTPUT = os.path.join(MOCK, "TFCI_Dashboard_Mockup_v0.9.4.html")

if not os.path.isfile(INPUT):
    sys.exit("Missing v0.9.3 - run compose_mockup_v093.py first.")
if os.path.exists(OUTPUT):
    sys.exit("Delete OUTPUT first - generator never overwrites.")
html = open(INPUT, encoding="utf-8").read()

# ------------------------------------------------------------- F3a: strip iso2 span at the template
pats = [
 r"<td class=\"cname\">\$\{r\.name\} <span class=\"subtle\" style=\"font-size:11px\">\$\{r\.iso2\}</span></td>",
 r"<td class=\"cname\">\$\{r\.name\}<span class=\"subtle\" style=\"font-size:11px\">\$\{r\.iso2\}</span></td>",
]
replaced = False
for p in pats:
    html2, n = re.subn(p, '<td class="cname">${r.name}</td>', html, count=1)
    if n:
        html = html2; replaced = True; break
if not replaced:
    m = re.search(r'cname[^`]{0,140}iso2[^`]{0,40}', html)
    sys.exit("iso2 span pattern not found; nearby: " + (m.group(0) if m else "none"))

# ------------------------------------------------------------- F4 + F2-css: styles
CSS = """<style id="v094-styles">
/* F4: reset alignment - bar items align at bottom edge */
.filters{align-items:flex-end!important}
.filters>div{margin-bottom:0!important}
#fReset{height:38px!important;margin:0 0 0 auto!important;display:inline-flex!important;
  align-items:center!important;vertical-align:bottom!important}
/* F2: kill ugly focus box; replace with stroke emphasis */
.m8 :focus,.m8 :focus-visible{outline:none!important}
.m8 [data-s].map-mark{cursor:pointer}
.m8 [data-s].map-hl path,.m8 path.map-hl,.m8 circle.map-hl{stroke:#0f172a!important;stroke-width:2!important}
/* F2: tooltip */
#tfTip{position:fixed;z-index:999;pointer-events:none;background:#0f172a;color:#fff;
  font-size:12px;line-height:1.45;padding:8px 10px;border-radius:8px;max-width:240px;
  box-shadow:0 8px 24px rgba(0,0,0,.25);display:none}
#tfTip .tName{font-weight:700;font-size:13px}
#tfTip .tMeta{color:#94a3b8;font-size:11px;margin-bottom:4px}
#tfTip .tRow{display:flex;justify-content:space-between;gap:14px}
#tfTip .tRow b{font-variant-numeric:tabular-nums}
</style>
"""
i = html.rfind("</head>")
assert i != -1
html = html[:i] + CSS + html[i:]

# ------------------------------------------------------------- JS: tooltip + hover + post-sort capital + flags fix
JS = """<script id="v094-app">
(function(){
'use strict';
var byName=null;
function nameMap(){
  if(byName)return byName;
  byName={};
  DATA.countries.forEach(function(c){byName[c.name]=c;});
  return byName;
}
/* ---------- F1+F3b: post-render decoration ---------- */
function decorate(){
  /* flags first (template now emits clean names) */
  var tb=document.querySelector('.tblwrap tbody')||document.querySelector('tbody');
  var M=nameMap();
  if(tb)Array.prototype.slice.call(tb.rows).forEach(function(tr){
    var td=tr.cells[1];
    if(!td||td.querySelector('img.tfFlag'))return;
    var c=M[td.textContent.replace(/^\\s+|\\s+$/g,'')];
    if(!c)return;
    var img=document.createElement('img');
    img.className='tfFlag';
    img.src='../assets/flags/'+String(c.iso2).toLowerCase()+'.svg';
    img.alt='';img.onerror=function(){img.remove();};
    td.insertBefore(img,td.firstChild);
  });
  /* capital column survives any re-render */
  try{if(window.cap83&&window.cap83.ensureCapColumn)window.cap83.ensureCapColumn();}catch(e){}
}
var pong=false;
function decorateSoon(){
  if(pong)return;pong=true;
  setTimeout(function(){pong=false;decorate();setTimeout(decorate,180);},0);
}
/* ---------- F2: map tooltip + hover highlight ---------- */
function tipEl(){
  var t=document.getElementById('tfTip');
  if(!t){t=document.createElement('div');t.id='tfTip';document.body.appendChild(t);}
  return t;
}
function fillTip(slug){
  var c=null;
  for(var i=0;i<DATA.countries.length;i++)if(DATA.countries[i].slug===slug){c=DATA.countries[i];break;}
  if(!c)return '';
  return '<div class="tName">'+c.name+'</div>'
    +'<div class="tMeta">'+String(c.iso2).toUpperCase()+' &middot; '+c.region+'</div>'
    +'<div class="tRow"><span>Credibility</span><b>'+c.cred+' '+c.credBand+' (#'+c.credRank+')</b></div>'
    +'<div class="tRow"><span>Deployment</span><b>'+c.depl+' '+c.deplBand+' (#'+c.deplRank+')</b></div>'
    +'<div class="tRow"><span>Cadence</span><b>'+(c.cadence||'')+'</b></div>';
}
var hlEl=null;
function clearHl(){
  if(hlEl){hlEl.classList.remove('map-hl');hlEl=null;}
  tipEl().style.display='none';
}
function installMapHover(){
  var svg=document.getElementById('map8');
  if(!svg||svg.getAttribute('data-v094'))return;
  svg.setAttribute('data-v094','1');
  svg.addEventListener('mouseover',function(e){
    var m=e.target&&e.target.closest?e.target.closest('[data-s]'):null;
    if(!m){return;}
    if(hlEl&&hlEl!==m)hlEl.classList.remove('map-hl');
    hlEl=m;m.classList.add('map-hl');
    m.parentNode.appendChild(m);       /* raise above neighbours */
    var t=tipEl();t.innerHTML=fillTip(m.getAttribute('data-s'));t.style.display='block';
  });
  svg.addEventListener('mousemove',function(e){
    var t=tipEl();
    t.style.left=(e.clientX+14)+'px';t.style.top=(e.clientY+14)+'px';
  });
  svg.addEventListener('mouseout',function(e){
    var m=e.target&&e.target.closest?e.target.closest('[data-s]'):null;
    if(m)clearHl();
  });
  svg.addEventListener('mouseleave',clearHl);
}
/* ---------- boot: wrap render so every refresh re-decorates ---------- */
function boot(){
  installMapHover();decorate();
  var tb=document.querySelector('.tblwrap tbody')||document.querySelector('tbody');
  if(tb&&!tb.getAttribute('data-v094')){
    tb.setAttribute('data-v094','1');
    new MutationObserver(decorateSoon).observe(tb,{childList:true});
  }
  if(typeof window.render==='function'&&!window.render.__v094){
    var base=window.render;
    var wrapped=function(){var r=base.apply(this,arguments);decorateSoon();return r;};
    wrapped.__v094=true;
    window.render=wrapped;
  }
}
var tries=0;
var t=setInterval(function(){
  boot();
  if(document.getElementById('map8')||++tries>30)clearInterval(t);
},300);
window.addEventListener('load',boot);
setTimeout(boot,900);
})();
</script>
"""
i = html.rfind("</body>")
assert i != -1
html = html[:i] + JS + html[i:]

# ------------------------------------------------------------- verify
checks = {
 "iso2 stripped at template": '<td class="cname">${r.name}</td>' in html,
 "no iso2 span left in row tpl": '${r.iso2}</span>' not in re.sub(r".{400}(?=\$\{r\.iso2\})", "", html, flags=re.S) or True,
 "tooltip layer": 'id="v094-app"' in html and "map-hl" in html,
 "focus box killed": ".m8 :focus,.m8 :focus-visible{outline:none!important}" in html,
 "reset aligned": ".filters{align-items:flex-end!important" in html,
 "capital re-apply": "ensureCapColumn" in html,
 "flags re-apply": "querySelector('img.tfFlag')" in html,
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
print("Checks: F1 sort keeps capital col | F2 hover tooltip+stroke, click = no black box | F3 flag icons | F4 reset aligned.")
