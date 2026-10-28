# Adds a fixed bottom dock listing the ten most important matchups. Applied to the built page text.
CSS = """
#dock{position:fixed;left:0;right:0;bottom:0;z-index:45;background:color-mix(in srgb,var(--card) 96%,transparent);backdrop-filter:blur(8px);
  border-top:2px solid var(--fg);padding:7px max(16px,env(safe-area-inset-right,0px)) calc(8px + env(safe-area-inset-bottom,0px)) max(16px,env(safe-area-inset-left,0px))}
#dock .dh{display:flex;gap:10px;align-items:baseline;margin-bottom:6px}
#dock .dh b{font-family:var(--display);font-weight:800;font-size:14px;letter-spacing:.12em;text-transform:uppercase}
#dock .dh span{font-family:var(--data);font-size:11px;color:var(--dim)}
#dock .ds{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x proximity;padding-bottom:2px}
#dock .dc{flex:0 0 232px;min-width:0;scroll-snap-align:start;text-align:left;border:1px solid var(--rule);background:var(--bg);border-radius:9px;padding:6px 9px;display:grid;gap:3px;align-content:start}
#dock .dc[aria-pressed="true"]{border-color:var(--fg);box-shadow:inset 0 0 0 1px var(--fg)}
#dock .dt{display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:13px}
#dock .dn{font-family:var(--display);font-weight:800;font-size:15px;color:var(--dim);min-width:1.1em}
#dock .dw{font-size:11.5px;line-height:1.3;color:var(--dim);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
#dock .ds2{font-family:var(--data);font-size:10.5px;color:var(--warn)} #dock .ds2.on{color:var(--good)}
body:not(.nodock){padding-bottom:calc(150px + env(safe-area-inset-bottom,0px))}
body:not(.nodock) #toast{bottom:calc(170px + env(safe-area-inset-bottom,0px))}
"""
HTML = '<div id="dock" aria-label="Ten most important matchups"></div>\n'
JS = r"""
const TOPW = {rematch:.55, series:.4, derby:.3, top:.3, qb:.25, unit:.25, last:.2, lead:.15, drought:.15, cellar:.1, draft:.2, class:.1, former:.1, staff:.1};
function weight(g){ return juice(g) + (INTR[g.id] || []).reduce((a, [k]) => a + (TOPW[k] || .1), 0); }
function topTen(){ const used = {}, pairs = {}, out = [];
  DATA.games.slice().sort((a, b) => weight(b) - weight(a) || (a.id < b.id ? -1 : 1)).forEach(g => {
    if (g.kind === 'division') return; const pk = sides(g).slice().sort().join('|'); if (out.length >= 10 || pairs[pk] || sides(g).some(t => (used[t] || 0) >= 2)) return;
    pairs[pk] = 1; sides(g).forEach(t => used[t] = (used[t] || 0) + 1); out.push(g); });
  return out; }
const TOP10 = topTen();
function renderDock(){
  const placed = TOP10.filter(g => where(g.id)).length;
  const done = placed === TOP10.length; el('dock').hidden = done; document.body.classList.toggle('nodock', done); if (done) return;
  el('dock').innerHTML = `<div class="dh"><b>Ten key non-division matchups</b><span>${placed} of 10 placed · tap one to open it</span></div><div class="ds">` + TOP10.map((g, i) => {
    const wh = where(g.id), f = (INTR[g.id] || []).slice().sort((a, b) => (TOPW[b[0]] || 0) - (TOPW[a[0]] || 0))[0];
    return `<button class="dc" data-top="${g.id}" aria-pressed="${gsel === g.id}"><span class="dt"><span class="dn">${i + 1}</span>${tmn(g.visitor, true)} <i style="font-style:normal;color:var(--dim);font-size:12px">at</i> ${tmn(g.host, true)}</span><span class="dw">${f ? esc(f[1]) : esc(KINDTAG[g.kind] || '')}</span><span class="ds2${wh ? ' on' : ''}">${wh ? esc(wh) : 'not placed yet'}</span></button>`; }).join('') + '</div>';
}
document.addEventListener('click', e => { const t = e.target.closest('[data-top]'); if (!t) return;
  const g = GM[t.dataset.top]; view = 'clubs'; sel = gsel === g.id ? sel : g.host; if (!sides(g).includes(sel)) sel = g.host; gsel = g.id; render();
  el('main').querySelector('.wgrid')?.scrollIntoView({block:'nearest'}); });
"""
def apply(page):
    assert page.count('</style>') == 1
    page = page.replace('</style>', CSS + '</style>')
    page = page.replace('<div id="toast" role="status"></div>', HTML + '<div id="toast" role="status"></div>')
    a = 'function render(){'
    assert page.count(a) == 1
    page = page.replace(a, JS + a)
    b = "renderChecks(S); renderBlob();"
    assert page.count(b) == 1
    page = page.replace(b, "renderChecks(S); renderBlob(); renderDock();")
    return page
