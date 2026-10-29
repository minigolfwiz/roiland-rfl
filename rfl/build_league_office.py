"""Build the League Office page (out/league_office_<year>.html): this week's ballot plus the season's record.
Usage: python3 rfl/build_league_office.py   (reads the state, the pending ballot, and the club brand block of the Season page)"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import *

S = load(STATE); se = S['season']; year = se['year']
week = int(os.environ.get('RFL_OFFICE_WEEK', se['week_done']))
bpath = f'{ROOT}/data/office/ballot_{year}_w{week}.json'
pending = os.path.exists(bpath) and str(week) not in se.get('potw', {})
B = json.load(open(bpath)) if pending else None
season_page = open(f'{ROOT}/out/rfl_season_{year}.html').read()
i = season_page.index('const BRAND = '); BRAND = season_page[i:season_page.index('\n', i)]
j = season_page.index('const _lum = '); k = season_page.index('function tmn(')
CHIPJS = season_page[j:season_page.index('\n', k)]
hist = dict(potw=se.get('potw', {}), discipline=se.get('discipline', []))
from rfl.cases import RATES
D = dict(year=year, week=week, ballot=B, hist=hist, rates=RATES)

HTML = r"""<meta charset="utf-8"><title>League Office</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Barlow:wght@400;500;600&display=swap">
<style>
/* Layout: a single working column, the way a commissioner's desk memo reads: summary first, one decision block per item, one submit bar. */
:root{--paper:#eef1f4;--card:#fff;--ink:#15202a;--dim:#566673;--rule:#d3dce3;--chip:#e5ebf0;--navy:#1d3f6e;--gold:#8a5f06;--ok:#1f7a4d;
--minor:#566673;--moderate:#a8640a;--serious:#b8322a;--major:#8c1b2b;--club:#5b3a8c;--review:#2a7a8c;--appeal:#6b5a3a;
--display:"Barlow Condensed","Arial Narrow",Arial,sans-serif;--body:"Barlow",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#0e141a;--card:#16202a;--ink:#e7edf2;--dim:#93a4b2;--rule:#283542;--chip:#1f2b37;--navy:#9cc2f2;--gold:#e3b35a;--ok:#5ac28c;--minor:#93a4b2;--moderate:#e3a24a;--serious:#ee7a70;--major:#f0828f;--club:#b89ae8;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#0e141a;--card:#16202a;--ink:#e7edf2;--dim:#93a4b2;--rule:#283542;--chip:#1f2b37;--navy:#9cc2f2;--gold:#e3b35a;--ok:#5ac28c;--minor:#93a4b2;--moderate:#e3a24a;--serious:#ee7a70;--major:#f0828f;--club:#b89ae8;color-scheme:dark}
*{box-sizing:border-box} html{background:var(--paper)}
body{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.4;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:18px 120px}
.wrap{max-width:760px;margin:0 auto}
h1{font-family:var(--display);font-weight:800;font-size:clamp(34px,8vw,48px);line-height:1;margin:0;text-wrap:balance}
.sub{color:var(--dim);margin:6px 0 14px;max-width:62ch}
h2{font-family:var(--display);font-weight:800;font-size:22px;letter-spacing:.05em;text-transform:uppercase;margin:30px 0 4px;border-top:2px solid var(--ink);padding-top:10px;text-wrap:balance}
h2 small{font-weight:600;color:var(--dim);letter-spacing:.04em;font-size:14px;margin-left:6px}
.hint{color:var(--dim);font-size:13.5px;margin:0 0 10px;max-width:62ch}
.status{display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:9px 12px;margin:0 0 6px;font-size:14px}
.status b{font-family:var(--display);letter-spacing:.06em;text-transform:uppercase}
.dot{width:10px;height:10px;border-radius:50%;background:var(--moderate)} .status.done .dot{background:var(--ok)}
.grp{margin:12px 0 0} .grp h3{font-family:var(--display);font-weight:800;font-size:17px;letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px;color:var(--gold)}
.opt{display:grid;grid-template-columns:22px minmax(0,1fr);gap:4px 10px;align-items:start;background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:10px 12px;margin:0 0 6px;cursor:pointer}
.opt:has(input:checked){border-color:var(--navy);box-shadow:inset 0 0 0 1px var(--navy)}
.opt input{margin:2px 0 0;width:20px;height:20px;accent-color:var(--navy)}
.opt:focus-within{outline:2px solid var(--navy);outline-offset:2px}
.nm{font-weight:600} .pos{font-family:var(--display);font-weight:700;letter-spacing:.06em;color:var(--dim);margin-left:4px}
.pv{margin:5px 0 0;padding-left:17px;font-size:13px;color:var(--ink)} .pv li{margin:1px 0;font-variant-numeric:tabular-nums}
.ln{color:var(--ink);font-size:14px;margin-top:2px;font-variant-numeric:tabular-nums} .rs{color:var(--dim);font-size:12.5px}
.tm{display:inline-block;max-width:100%;overflow:hidden;text-overflow:ellipsis;vertical-align:bottom;padding:1px 7px 1px 6px;border-radius:6px;border:1px solid rgba(0,0,0,.15);border-left:4px solid var(--ac);background:var(--bg);color:var(--fg);font-weight:600;white-space:nowrap;line-height:1.35}
.tm.sm{font-size:.92em;padding:0 6px 0 5px;border-left-width:3px}
.case{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:12px 14px;margin:0 0 14px}
.case header{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.pill{font-family:var(--display);font-weight:800;letter-spacing:.08em;text-transform:uppercase;font-size:12px;border-radius:999px;padding:1px 9px;color:var(--bg);background:var(--c)}
.pill{color:#fff} .t-minor{--c:var(--minor)} .t-moderate{--c:var(--moderate)} .t-serious{--c:var(--serious)} .t-major{--c:var(--major)} .t-club{--c:var(--club)} .t-review{--c:var(--review)} .t-appeal{--c:var(--appeal)}
:root[data-theme="dark"] .pill{color:#0e141a}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .pill{color:#0e141a}}
.case h3{font-family:var(--display);font-weight:800;font-size:21px;margin:0;line-height:1.1}
.who{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:2px 0 6px}
.case p{margin:0 0 6px} .where{font-size:12.5px;color:var(--dim)}
.case .opt{background:var(--paper)} .sug{font-family:var(--display);font-weight:700;letter-spacing:.06em;text-transform:uppercase;font-size:11.5px;color:var(--gold);margin-left:6px}
textarea{width:100%;font:inherit;font-size:14px;background:var(--paper);color:var(--ink);border:1px solid var(--rule);border-radius:8px;padding:8px 10px;min-height:42px;resize:vertical;margin-top:4px}
.empty{background:var(--card);border:1px dashed var(--rule);border-radius:12px;padding:14px;color:var(--dim)}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--rule);padding:10px max(16px,env(safe-area-inset-right,0px)) calc(10px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px));z-index:5}
.bar .in{max-width:760px;margin:0 auto;display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.bar .need{font-size:13.5px;color:var(--dim);min-width:0}
button{font:inherit;font-family:var(--display);font-weight:800;letter-spacing:.07em;text-transform:uppercase;font-size:17px;border:0;border-radius:10px;padding:10px 20px;background:var(--navy);color:#fff;cursor:pointer}
:root[data-theme="dark"] button{color:#0e141a} @media (prefers-color-scheme:dark){:root:not([data-theme="light"]) button{color:#0e141a}}
button:disabled{opacity:.4;cursor:default} button.ghost{background:var(--chip);color:var(--ink);font-size:14px;padding:7px 12px} button:focus-visible{outline:2px solid var(--navy);outline-offset:2px}
table{width:100%;border-collapse:collapse;font-size:13.5px} td,th{padding:5px 6px;border-top:1px solid var(--rule);text-align:left;vertical-align:top} th{font-family:var(--display);letter-spacing:.06em;text-transform:uppercase;font-size:12px;color:var(--dim);border-top:0}
td.n{font-variant-numeric:tabular-nums;white-space:nowrap} .tw{overflow-x:auto}
.rec{border-top:1px solid var(--rule);padding:8px 0;font-size:14px} .rec b{font-family:var(--display);letter-spacing:.05em}
details{margin-top:6px} summary{cursor:pointer;font-family:var(--display);font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--navy)}
.sev{font-family:var(--display);font-weight:700;letter-spacing:.06em;text-transform:uppercase;font-size:12.5px;color:var(--dim);border:1px solid var(--rule);border-radius:999px;padding:0 8px}
.sev i{display:inline-block;width:46px;height:6px;background:var(--chip);border-radius:3px;margin:0 5px 1px;vertical-align:middle;position:relative;overflow:hidden} .sev i b{position:absolute;left:0;top:0;bottom:0;background:var(--c)}
.txt p{margin:0 0 8px} .ctx{background:var(--paper);border-radius:8px;padding:6px 10px;margin:4px 0 6px;font-size:13px;color:var(--dim)} .ctx b{font-family:var(--display);letter-spacing:.06em;text-transform:uppercase;color:var(--ink);font-size:12px} .ctx ul{margin:3px 0 0;padding-left:17px}
.blurb{display:block;color:var(--dim);font-size:12.5px;margin-top:1px}
.note{font-size:12.5px;color:var(--dim)} .warn{color:var(--serious)}
</style>
<div class="wrap">
<h1>League Office</h1>
<p class="sub">Your desk between weeks. Pick the Players of the Week, rule on any cases, and submit. Then tell Claude, and the next week plays.</p>
<div id="status" class="status"><span class="dot"></span><span id="stxt"></span></div>
<div id="main"></div>
<h2>How often cases come<small>drawn at random, no quota</small></h2>
<p class="hint">Each week the desk draws a number of cases from these averages. Some weeks have none, some have several. Most are fines; a suspension-level case is a few a season; a criminal case is rare.</p>
<div class="tw"><table id="rates"></table></div>
<h2>The record<small>decided weeks</small></h2>
<div id="hist"></div>
</div>
<div class="bar" id="bar" hidden><div class="in"><span class="need" id="need"></span><span><button class="ghost" id="copy" type="button" hidden>Copy summary</button> <button id="submit" type="button" disabled>Submit decisions</button></span></div></div>
<script>
__BRAND__
__CHIPJS__
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const D = __DATA__;
const $ = id => document.getElementById(id);
const chip = (t, small) => (typeof _chip === 'function' && BRAND[t]) ? _chip(t, small, t) : esc(t);
const TIER = {minor:'Minor', moderate:'Moderate', serious:'Serious', major:'Major', club:'Club', review:'Review', appeal:'Appeal'};
const STAGE = {findings:'Findings', resolution:'Resolution', review:'Reinstatement review', appeal:'Appeal'};
const PERSEASON = {minor:'about 18', moderate:'about 5', serious:'1 to 2', major:'1 every 3 years', club:'about 1'};
const COVERS = {minor:'Late hits, taunting, helmet contact, gestures, fan incidents, comments, social posts, missed media, equipment, sideline conduct. Fines, sometimes a game.', moderate:'Ejections, fights, benches clearing, dangerous hits with injuries, bounty and hazing complaints. Fines or games.', serious:'Substance violations, DUI, gambling, firearms, reckless driving, assault charges. Games missed, programs, probation.', major:'Felony charges (domestic violence, assault, sexual assault, DUI with injury, trafficking, weapons, burglary, fraud). League policy: exempt list or indefinite suspension, then a resolution weeks later, up to a permanent ban.', club:'Tampering, illegal filming, cap side payments, injury reports, draft leaks, facility conditions, executive and owner conduct. Club fines, picks, coach suspensions. Appeals, findings and reinstatement reviews arrive on top of these.'};
const fmtMean = m => m < .1 ? m.toFixed(3) : m.toFixed(2);
$('rates').innerHTML = '<tr><th>Tier</th><th>Per week</th><th>Per season</th><th>Covers</th></tr>' + D.rates.map(r => `<tr><td><b>${TIER[r[0]]}</b></td><td class="n">${fmtMean(r[1])}</td><td class="n">${PERSEASON[r[0]]}</td><td>${COVERS[r[0]]}</td></tr>`).join('');

const B = D.ballot, WK = D.week;
const CATS = [['off','Offensive Player of the Week'],['defense','Defensive Player of the Week'],['st','Special Teams Player of the Week']];
function candidate(c, name, val){
  return `<label class="opt"><input type="radio" name="${name}" value="${esc(val)}"><span><span class="nm">${esc(c.name)}</span><span class="pos">${esc(c.pos)}</span> ${chip(c.club, true)}<div class="ln">${esc(c.line)}</div><div class="rs">${esc(c.res)}</div>${(c.plays && c.plays.length) ? '<ul class="pv">' + c.plays.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul>' : ''}</span></label>`;
}
function option(o, name){
  return `<label class="opt"><input type="radio" name="${name}" value="${esc(o.key)}"><span><span class="nm">${esc(o.label)}</span>${o.suggested ? '<span class="sug">Suggested</span>' : ''}${o.status === 'indef' ? '<span class="sug warn">Stays out until reinstated</span>' : ''}${o.status === 'ban' ? '<span class="sug warn">Permanent</span>' : ''}${(o.blurb && (o.program || o.probation || o.coach_games || o.pick_round || o.indef_min || o.exempt || o.adjust || o.reinstate || o.ban)) ? '<span class="blurb">' + esc(o.blurb) + '</span>' : ''}</span></label>`;
}
function render(){
  const m = $('main');
  if (!B){ m.innerHTML = '<div class="empty">Nothing is waiting. The ballot for the next week appears here once that week has been played.</div>'; $('bar').hidden = true;
    $('status').classList.add('done'); $('stxt').innerHTML = '<b>All caught up.</b> Week ' + WK + ' is decided.'; return; }
  let h = CATS.some(([k]) => (B.potw[k] || []).length) ? `<h2>Players of the Week<small>week ${WK}</small></h2><p class="hint">One from each list. Candidates are the top performers by the week's box scores.</p>` : '';
  for (const [k, label] of CATS){ const L = B.potw[k] || []; if (!L.length) continue;
    h += `<div class="grp"><h3>${label}</h3>` + L.map(c => candidate(c, 'p-' + k, c.pid)).join('') + '</div>'; }
  h += `<h2>Cases<small>${B.cases.length ? B.cases.length + ' this week' : 'none this week'}</small></h2>`;
  if (!B.cases.length) h += '<div class="empty">No cases reached the league office this week.</div>';
  for (const c of B.cases){
    const sev = c.severity ? `<span class="sev t-${c.tier}" style="--c:var(--${c.tier})">Severity <i><b style="width:${Math.round(c.severity * 10)}%"></b></i>${c.severity.toFixed(1)}</span>` : '';
    const paras = String(c.text || '').split('\n\n').map(x => '<p>' + esc(x) + '</p>').join('');
    h += `<div class="case" data-id="${c.id}"><header><span class="pill t-${c.tier}">${TIER[c.tier]}</span>${c.stage && c.stage !== 'new' ? '<span class="sev">' + (STAGE[c.stage] || c.stage) + '</span>' : ''}${sev}</header><h3>${esc(c.title)}</h3>
      <div class="who">${c.who.map(w => w.club_level ? chip(w.club) : (w.coach ? `<span class="nm">${esc(w.name)}</span><span class="pos">${esc(w.pos || 'HC')}</span> ${chip(w.club, true)}` : `<span class="nm">${esc(w.name)}</span><span class="pos">${esc(w.pos)}</span> ${chip(w.club, true)}`)).join('<span class="rs">&nbsp;and&nbsp;</span>')}</div>
      <div class="txt">${paras}</div>
      ${(c.chain && c.chain.length) ? '<div class="ctx"><b>How we got here</b><ul>' + c.chain.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul></div>' : ''}
      ${(c.precedent && c.precedent.length) ? '<div class="ctx"><b>Precedent, similar severity</b><ul>' + c.precedent.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul></div>' : ''}
      <div class="where">${esc(c.where)}${c.prior ? ' · earlier cases: ' + c.prior : ''}</div><div style="margin-top:8px">${c.options.map(o => option(o, 'c-' + c.id)).join('')}</div>
      <textarea id="note-${c.id}" placeholder="Optional note for the record" rows="1"></textarea></div>`; }
  if ((B.open || []).length) h += `<h2>Open matters<small>still unresolved</small></h2><div class="ctx">` + B.open.map(x => `<div>${esc(x.title)}: <span class="nm">${esc(x.who)}</span> ${chip(x.club, true)} <span class="rs">${esc(x.since)}${x.ruling ? ' · your ruling: ' + esc(x.ruling) : ''}</span></div>`).join('') + '</div>';
  m.innerHTML = h; $('bar').hidden = false;
  m.addEventListener('change', update); m.addEventListener('input', e => { if (e.target.tagName === 'TEXTAREA') dirty(); });
  update();
}
function val(name){ const x = document.querySelector(`input[name="${name}"]:checked`); return x ? x.value : null; }
function collect(){
  const potw = {}; for (const [k] of CATS){ if ((B.potw[k] || []).length){ const v = val('p-' + k); if (v) potw[k] = +v; } }
  const rulings = {}; for (const c of B.cases){ const v = val('c-' + c.id); if (v) rulings[c.id] = {key: v, note: ($('note-' + c.id).value || '').trim()}; }
  return {week: WK, potw, rulings};
}
function missing(){
  const d = collect(); let n = 0;
  for (const [k] of CATS) if ((B.potw[k] || []).length && d.potw[k] == null) n++;
  for (const c of B.cases) if (!d.rulings[c.id]) n++;
  return n;
}
function summary(){
  const d = collect(); const L = ['Week ' + WK + ' decisions'];
  for (const [k, label] of CATS){ const c = (B.potw[k] || []).find(x => x.pid === d.potw[k]); if (c) L.push(label + ': ' + c.name + ' (' + c.pos + ', ' + c.club + ')'); }
  for (const c of B.cases){ const r = d.rulings[c.id]; if (r){ const o = c.options.find(x => x.key === r.key); L.push(c.id + ' ' + c.title + ' - ' + c.who.map(w => w.name).join(' & ') + ': ' + o.label + (r.note ? ' [' + r.note + ']' : '')); } }
  return L.join('\n');
}
let saved = false, dbRef = null;
function dirty(){ if (saved){ saved = false; update(); } }
function update(){
  if (!B) return; if (saved) saved = false;
  const n = missing(); $('submit').disabled = n > 0; $('need').textContent = n ? n + ' decision' + (n === 1 ? '' : 's') + ' to go' : 'All decided. Ready to submit.';
  setStatus();
}
function setStatus(){
  const s = $('status'); s.classList.toggle('done', saved);
  $('stxt').innerHTML = saved ? '<b>Submitted.</b> Tell Claude you are done and week ' + (WK + 1) + ' plays. You can still change answers until then.' : '<b>Waiting on you.</b> ' + (WK > 20 ? 'The season is over; these matters came due.' : 'Week ' + WK + ' is played.') + ' Make your picks and rulings, then submit.';
}
function apply(d){
  if (!d) return;
  for (const k in (d.potw || {})){ const x = document.querySelector(`input[name="p-${k}"][value="${d.potw[k]}"]`); if (x) x.checked = true; }
  for (const id in (d.rulings || {})){ const r = d.rulings[id]; const x = document.querySelector(`input[name="c-${id}"][value="${r.key}"]`); if (x) x.checked = true; const t = $('note-' + id); if (t && r.note) t.value = r.note; }
}
async function init(){
  render();
  if (B){
    try { const db = await claude.use('db'); if (db){ dbRef = db.doc(D.year === 2043 ? 'office/w' + WK : 'office/y' + D.year + 'w' + WK);
        const snap = await dbRef.get(); if (snap.exists){ apply(snap.data()); update(); saved = true; setStatus(); } } } catch (e) {}
    $('copy').hidden = !!dbRef; if (!dbRef){ $('copy').hidden = false; }
    $('submit').onclick = async () => {
      const d = collect(); d.submitted = new Date().toISOString(); $('submit').disabled = true;
      try { if (!dbRef) throw new Error('nodb'); await dbRef.set(d); saved = true; $('need').textContent = 'Saved.'; setStatus(); }
      catch (e) { $('need').innerHTML = '<span class="warn">Could not save from this view.</span> Use Copy summary and paste it to Claude.'; $('copy').hidden = false; $('submit').disabled = false; }
    };
    $('copy').onclick = async () => { const t = summary(); try { await navigator.clipboard.writeText(t); $('need').textContent = 'Summary copied.'; } catch (e) { $('need').textContent = 'Copy blocked. Select and copy from the note below.'; const pre = document.createElement('textarea'); pre.value = t; pre.readOnly = true; pre.rows = 6; $('main').appendChild(pre); pre.select(); } };
  }
  renderHist();
}
function renderHist(){
  const H = D.hist, weeks = Object.keys(H.potw).map(Number).sort((a, b) => b - a);
  if (!weeks.length){ $('hist').innerHTML = '<div class="empty">No weeks decided yet. Your first picks and rulings will be recorded here.</div>'; return; }
  const CL = {off:'Offense', defense:'Defense', st:'Special teams'};
  $('hist').innerHTML = weeks.map(w => {
    const p = H.potw[w]; const cases = H.discipline.filter(d => d.week === w);
    return `<div class="rec"><b>WEEK ${w}</b><div>${['off','defense','st'].filter(k => p[k]).map(k => `${CL[k]}: <span class="nm">${esc(p[k].name)}</span> ${chip(p[k].club, true)} <span class="rs">${esc(p[k].line)}</span>`).join('<br>')}</div>` +
      (cases.length ? '<div style="margin-top:6px">' + cases.map(c => `<div><span class="pill t-${c.tier}">${TIER[c.tier] || c.tier}</span> ${esc(c.title)}: ${c.who.map(esc).join(' &amp; ')} (${c.clubs.map(x => chip(x, true)).join(' ')}) <b>${esc(c.ruling)}</b>${c.note ? ' <span class="rs">' + esc(c.note) + '</span>' : ''}</div>`).join('') + '</div>' : '<div class="rs" style="margin-top:6px">No cases.</div>') + '</div>'; }).join('');
}
init();
</script>
"""
page = HTML.replace('__BRAND__', BRAND).replace('__CHIPJS__', CHIPJS).replace('__DATA__', json.dumps(D, separators=(',', ':'), ensure_ascii=False))
out = f'{ROOT}/out/league_office_{year}.html'; open(out, 'w').write(page); print(out, len(page) // 1024, 'KB', 'pending week' if pending else 'no pending ballot', week)
