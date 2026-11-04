// Broadcast Desk section of the League Office: the original Broadcast Desk (week strip, Thursday/Monday window cards, game list with pick buttons, hold/armed taps,
// "prime N (H·A)" per club, short-rest warning, club-history dialog), ported from the 2042 desk. Window cards are Thursday and Monday only: Sunday primetime has its own section below.
const Desk = (() => {
  let X = null, week = 1, picks = {}, hold = null, armed = null, root = null, G = {};
  const hooks = { change: () => {}, sunday: () => null, sundayApp: () => ({}) };
  const SLOTS_STD = [['thu', 'Thursday night', '--thu'], ['mnf', 'Monday night', '--mnf']];
  const SLOTS_W20 = [['thu', 'Thursday night', '--thu']];
  const slotsFor = w => w === 20 ? SLOTS_W20 : SLOTS_STD;
  const SLOTNAME = { thu: 'Thursday night', mnf: 'Monday night' };
  const NARROW = window.matchMedia('(max-width: 760px)');
  const g$ = id => document.getElementById(id);
  const lastRow = t => X.hist[t].rows.slice(-1)[0];
  const recOf = t => { const r = lastRow(t); return `${r.w}-${r.l}${r.t ? '-' + r.t : ''}`; };
  const tr = (t, small) => _chip(t, small, `${BRAND[t].nick} ${recOf(t)}`);
  const trf = (t, small) => _chip(t, small, `${t} ${recOf(t)}`);
  const byWeek = w => X.games.filter(g => g.week === w).sort((a, b) => b.juice - a.juice);
  const pickOf = w => picks[w] || {};
  const slotOfGame = (gid, w) => { const p = pickOf(w); return slotsFor(w).map(s => s[0]).find(k => p[k] === gid) || null; };
  function own() {
    const n = {}; const add = (t, k) => { n[t] = n[t] || { h: 0, a: 0 }; n[t][k]++; };
    for (const w in picks) for (const k in picks[w]) { const g = G[picks[w][k]]; if (g) { add(g.host, 'h'); add(g.visitor, 'a'); } }
    return n;
  }
  function appearances() {
    const n = own(); const ex = hooks.sundayApp(); for (const t in ex) { n[t] = n[t] || { h: 0, a: 0 }; n[t].h += ex[t].h; n[t].a += ex[t].a; }
    return n;
  }
  const fmtApp = x => x ? `${x.h + x.a} <small>(${x.h}H·${x.a}A)</small>` : '0';
  function thuWeeks(t) { const out = []; for (const w in picks) { const g = picks[w].thu && G[picks[w].thu]; if (g && (g.host === t || g.visitor === t)) out.push(+w); } return out.sort((a, b) => a - b); }
  const fmtThu = t => { const ws = thuWeeks(t); return ws.length ? `<span class="thuw">Thu wk ${ws.join(', ')}</span>` : ''; };
  function shortRest(g, k) {      // Monday night the week before, or Thursday this week after a Monday
    const warn = [];
    for (const t of [g.host, g.visitor]) {
      const prev = pickOf(g.week - 1); if (k === 'thu' && prev.mnf && [G[prev.mnf].host, G[prev.mnf].visitor].includes(t)) warn.push(`${BRAND[t].nick} played Monday night in week ${g.week - 1} — four days' rest`);
      const next = pickOf(g.week + 1); if (k === 'mnf' && next.thu && [G[next.thu].host, G[next.thu].visitor].includes(t)) warn.push(`${BRAND[t].nick} is already Thursday night in week ${g.week + 1} — four days' rest`);
    }
    return warn;
  }
  function render() {
    if (!root) return;
    const app = appearances();
    g$('bdweeks').innerHTML = X.weeks.map(w => { const p = pickOf(w), need = slotsFor(w).length, n = slotsFor(w).filter(s => p[s[0]]).length; return `<button class="btab" type="button" data-w="${w}" aria-pressed="${w === week}">Wk ${w}${n === need ? '<i></i>' : n ? '<i class="part"></i>' : ''}</button>`; }).join('');
    const p = pickOf(week); const gs = byWeek(week);
    let h = `<div class="wkh">Week ${week} <small>${gs.length} games${week === 1 ? ` · the champion (${esc(X.champion)}) traditionally opens Thursday night at home` : week === 20 ? ' · no Monday night game in the final week' : ''}</small></div>`;
    h += '<div class="slots">' + slotsFor(week).map(([k, name, v]) => { const g = p[k] && G[p[k]]; const warns = g ? shortRest(g, k) : [];
      return `<div class="slot" style="--sc:var(${v})"><h3><span>${name}</span>${g ? `<button class="slotb" type="button" data-clear="${k}">clear</button>` : `<small>${armed === k ? 'tap a game below' : ''}</small>`}</h3>
        ${g ? `<div class="teams">${tr(g.visitor, true)} <span class="at">at</span> ${tr(g.host, true)}</div>${warns.map(x => `<div class="bwarn">⚠ ${esc(x)}</div>`).join('')}` : `<button class="g bempty" type="button" data-arm="${k}">${armed === k ? 'choose a game below' : hold ? 'put the held game here' : 'tap to choose'}</button>`}
      </div>`; }).join('') + '</div>';
    h += '<div class="list">' + gs.map(g => { const k = slotOfGame(g.id, week); const sun = hooks.sunday(g.id); const na = app[g.host], nb = app[g.visitor];
      return `<div class="g${k ? ' picked' : ''}${hold === g.id ? ' holding' : ''}${sun ? ' sunday' : ''}" data-g="${g.id}" role="button" tabindex="0" style="--sc:var(--${k || 'thu'})">
        <div class="teams">${NARROW.matches ? tr(g.visitor, true) : trf(g.visitor, true)} <span class="at">at</span> ${NARROW.matches ? tr(g.host, true) : trf(g.host, true)}
          <span class="tag${k ? ' ' + k : sun ? ' sun' : ''}">${k ? SLOTNAME[k] : sun ? esc(sun) : { division: 'DIV', conference: 'CONF', interconference: 'INTER' }[g.kind]}</span></div>
        <div class="meta"><button class="bpk${k ? ' on' : ''}" type="button">${k ? 'clear' : sun ? 'Sunday' : armed ? 'set ' + SLOTNAME[armed].split(' ')[0] : hold === g.id ? 'held' : 'pick'}</button><b>${g.juice.toFixed(2)}</b>prime ${esc(BRAND[g.visitor].nick)} ${fmtApp(nb)} ${fmtThu(g.visitor)}<br>prime ${esc(BRAND[g.host].nick)} ${fmtApp(na)} ${fmtThu(g.host)}</div>
      </div>`; }).join('') + '</div>';
    h += `<p class="bnote">The number on each game is a rough draw score from ${X.year - 1} records, playoff runs and whether it is a division game — a guide, not a rule. "prime" counts each club's stand-alone games picked so far across the season (Thursday, Monday and the Sunday primetime picks below), split into home (H) and away (A). Tap a club to see its history.</p>`;
    g$('bdout').innerHTML = h;
    const top = Object.entries(app).sort((a, b) => (b[1].h + b[1].a) - (a[1].h + a[1].a));
    const done = X.weeks.filter(w => slotsFor(w).every(s => pickOf(w)[s[0]])).length;
    g$('bdcounts').innerHTML = `<b>${done} of 20 weeks set.</b> Stand-alone appearances: ` + (top.length ? `<span class="bcounts">${top.map(([t, n]) => `<span>${esc(BRAND[t].nick)} ${n.h + n.a} (${n.h}H·${n.a}A)</span>`).join('')}</span>` : 'none yet');
  }
  function setPick(w, k, gid) {
    picks[w] = { ...pickOf(w) };
    if (gid) { for (const s of slotsFor(w)) if (picks[w][s[0]] === gid) delete picks[w][s[0]]; picks[w][k] = gid; } else delete picks[w][k];
    hooks.change();
  }
  function onClick(e) {
    const wb = e.target.closest('#bdweeks .btab'); if (wb) { week = +wb.dataset.w; hold = null; armed = null; render(); return; }
    const chip = e.target.closest('.tm'); if (chip) { openHist(chip.title); return; }
    const arm = e.target.closest('[data-arm]'); if (arm) { const k = arm.dataset.arm; if (hold) { setPick(week, k, hold); hold = null; armed = null; } else armed = (armed === k ? null : k); render(); return; }
    const cl = e.target.closest('[data-clear]'); if (cl) { setPick(week, cl.dataset.clear, null); render(); return; }
    const gb = e.target.closest('.g[data-g]'); if (gb) { const gid = gb.dataset.g;
      if (hooks.sunday(gid) && !slotOfGame(gid, week)) return;      // already a Sunday primetime pick: clear it there first
      if (armed) { setPick(week, armed, gid); armed = null; hold = null; }
      else if (slotOfGame(gid, week)) { setPick(week, slotOfGame(gid, week), null); }
      else { hold = (hold === gid ? null : gid); }
      render(); return; }
  }
  // ---- club history
  const EXN = k => { const e = String(k || '').toLowerCase(); return e === 'none' ? '—' : e === 'mega bowl champion' ? '<b>Mega Bowl champion</b>' : esc(k); };
  const luma = h => { const f = c => c <= .04045 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); return .2126 * f(parseInt(h.slice(1, 3), 16) / 255) + .7152 * f(parseInt(h.slice(3, 5), 16) / 255) + .0722 * f(parseInt(h.slice(5, 7), 16) / 255); };
  function mark(name, size) {
    const b = BRAND[name]; if (!b) return esc(name); const w = b.wordmark; const txt = b.case === 'upper' ? b.nick.toUpperCase() : b.nick;
    const fid = 'bdfont-' + b.font.replace(/\W/g, ''); if (!document.getElementById(fid)) { const l = document.createElement('link'); l.id = fid; l.rel = 'stylesheet'; l.href = 'https://fonts.googleapis.com/css2?family=' + encodeURIComponent(b.font) + '&display=swap'; document.head.appendChild(l); }
    const halo = luma(w.bg) < .12 ? '#ffffff' : '#0a0a0a'; const sw = /halo|edge/.test(w.treatment) && w.treatment.indexOf('noshadow') < 0 ? '.05em' : '.035em';
    return `<span class="mk ${w.treatment}" style="font-family:'${b.font}';font-size:${size || 28}px;--bg:${w.bg};--fg:${w.fill};--ac:${w.accent};--halo:${halo};--sw:${sw}"><span class="l halo drop" aria-hidden="true">${txt}</span><span class="l halo" aria-hidden="true">${txt}</span><span class="l drop" aria-hidden="true">${txt}</span><span class="l edge" aria-hidden="true">${txt}</span><span class="l fill">${txt}</span></span>`;
  }
  function openHist(t) {
    const c = X.hist[t]; if (!c) return; const m = g$('bdhist'); const rows = c.rows, T = X.teams[t];
    const wp = r => (r.w + r.t / 2) / (r.w + r.l + r.t);
    const pct = ((c.w + c.t / 2) / (c.w + c.l + c.t)).toFixed(3); const recent = rows.slice(-10).reverse();
    let h = `<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:4px 0 8px">${mark(t, 22)}<div><h3 style="margin:0;font-family:var(--display);font-weight:800;font-size:22px">${esc(t)}</h3><div class="bnote">${esc(T.conf)} ${esc(T.div)} · ${esc(T.stadium)}, ${esc(T.city)} · in the league since ${c.joined}<br>HC ${esc(c.coach)} · GM ${esc(c.gm)}</div></div></div>`;
    h += `<div class="kv"><span><b>${c.w}-${c.l}${c.t ? '-' + c.t : ''}</b> all-time (${pct})</span><span><b>${c.po}</b> playoff seasons</span><span><b>${c.dt}</b> division titles</span><span><b>${c.ct.length}</b> conference titles</span><span><b>${c.titles.length}</b> Mega Bowl${c.titles.length === 1 ? '' : 's'}${c.titles.length ? ': ' + c.titles.join(', ') : ''}</span></div>`;
    h += `<h4>Last ${Math.min(30, rows.length)} seasons</h4><div class="spark" title="win percentage by season; blue = playoffs, gold = champion">${rows.slice(-30).map(r => `<i style="height:${Math.max(6, wp(r) * 100)}%" class="${r.exit === 'Mega Bowl champion' ? 'ch' : r.exit !== 'none' ? 'po' : ''}" title="${r.y}: ${r.w}-${r.l}"></i>`).join('')}</div>`;
    h += `<h4>Recent seasons</h4><table class="h">${recent.map(r => `<tr class="${r.exit === 'Mega Bowl champion' ? 'ch' : ''}"><td>${r.y}</td><td>${r.w}-${r.l}${r.t ? '-' + r.t : ''}</td><td>${r.div ? 'won division' : (r.seed ? 'wild card' : '')}</td><td>${EXN(r.exit)}</td></tr>`).join('')}</table>`;
    const best = rows.slice().sort((a, b) => wp(b) - wp(a))[0], worst = rows.slice().sort((a, b) => wp(a) - wp(b))[0];
    h += `<h4>Marks</h4><div class="kv"><span>Best season <b>${best.y}</b> ${best.w}-${best.l}</span><span>Worst season <b>${worst.y}</b> ${worst.w}-${worst.l}</span>${c.titles.length ? `<span>Last title <b>${c.titles[c.titles.length - 1]}</b></span>` : '<span>Still chasing a first Mega Bowl</span>'}</div>`;
    m.querySelector('.hbody').innerHTML = h; m.showModal();
  }
  return {
    mount(el, data) {
      X = data; G = Object.fromEntries(X.games.map(g => [g.id, g])); root = el;
      el.innerHTML = `<h2>Broadcast Desk<small>Thursday and Monday nights, all 20 weeks</small></h2><p class="hint">Pick the <b style="color:var(--thu)">Thursday night</b> and <b style="color:var(--mnf)">Monday night</b> game for every week of ${X.year}. Tap a window, then <b>pick</b> the game that gets it, or pick a game first and then tap the window. Each club's chip carries its ${X.year - 1} record; tap it for the full history. Week 20 has a Thursday game and no Monday game. Whatever you pick here drops out of the Sunday primetime list below.</p>
        <div class="bsticky"><div class="bweeks" id="bdweeks"></div></div><div id="bdout"></div><p class="bnote" id="bdcounts"></p>`;
      el.addEventListener('click', onClick);
      el.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.classList.contains('g') && e.target.dataset.g) e.target.click(); });
      render();
    },
    render, hooks,
    get() { const o = {}; for (const w in picks) { const p = {}; for (const [k] of slotsFor(+w)) if (picks[w][k]) p[k] = picks[w][k]; if (Object.keys(p).length) o[w] = p; } return o; },
    load(o) { picks = {}; for (const w in (o || {})) { const p = {}; for (const k in o[w]) if (G[o[w][k]]) p[k] = o[w][k]; picks[w] = p; } render(); },
    missing() { let n = 0; for (const w of X.weeks) for (const [k] of slotsFor(w)) if (!pickOf(w)[k]) n++; return n; },
    slotOf(gid) { for (const w in picks) for (const k in picks[w]) if (picks[w][k] === gid) return SLOTNAME[k]; return null; },
    gameLine(gid) { const g = G[gid]; return g ? g.visitor + ' at ' + g.host : ''; },
    lines() { const L = []; for (const w of X.weeks) for (const [k, name] of slotsFor(w)) { const g = G[pickOf(w)[k]]; if (g) L.push('Week ' + w + ' ' + name.toLowerCase() + ': ' + g.visitor + ' at ' + g.host); } return L; },
    own,
  };
})();
