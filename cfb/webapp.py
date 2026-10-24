"""Phase 4: single-file interactive HTML site, rebuilt automatically after every sim window.
Standings (conf + overall), Top 25, team pages (roster w/ per-game stats, Fr/transfer tags,
full schedule), clickable results -> full box scores, storylines, injury report."""
import json, html, collections
import sys; sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E
import season as SE
from committee import committee_rank

U = E.U

def _box_json(box):
    def rows(side):
        out = {"passing": [], "rushing": [], "receiving": [], "defense": [], "kicking": []}
        for pid, s in box["stats"].items():
            if s["team"] != side: continue
            if s.get("Att"): out["passing"].append([s["name"], f"{s.get('Comp',0)}/{s.get('Att',0)}", s.get("PassYds",0), s.get("PassTD",0), s.get("INT",0)])
            if s.get("RushAtt"): out["rushing"].append([s["name"], s.get("RushAtt",0), s.get("RushYds",0), s.get("RushTD",0)])
            if s.get("Rec") or s.get("Targets"): out["receiving"].append([s["name"], s.get("Rec",0), s.get("RecYds",0), s.get("RecTD",0)])
            if s.get("Tackles") or s.get("Sacks") or s.get("INT_def"): out["defense"].append([s["name"], s.get("Tackles",0), round(s.get("Sacks",0),1), s.get("INT_def",0)])
            if s.get("FGAtt") or s.get("Punts"): out["kicking"].append([s["name"], f"{s.get('FGMade',0)}/{s.get('FGAtt',0)}", f"{s.get('XPMade',0)}/{s.get('XPAtt',0)}", s.get("Punts",0)])
        for k in out: out[k].sort(key=lambda r: -(r[2] if isinstance(r[2], (int,float)) else 0))
        return out
    return {"home": box["home"], "away": box["away"], "hs": box["home_score"], "as": box["away_score"],
            "ot": box.get("ot",0), "wp": box.get("pregame_home_wp"), "seed": box["seed"],
            "scoring": [{"q": sp["q"], "clk": f'{sp["clock"]//60}:{sp["clock"]%60:02d}',
                          "team": sp["team"], "desc": sp["desc"],
                          "score": f'{sp["score"][0]}-{sp["score"][1]}'} for sp in box["scoring_plays"]],
            "injuries": [f'{i["name"]} ({i["pos"]}) - {i["desc"]}' for i in box.get("injuries",[])],
            "H": rows(box["home"]), "A": rows(box["away"])}

def build_site(out_path='/mnt/user-data/outputs/roiland.html'):
    s = SE.load_state()
    from games_db import load_db
    db = load_db()
    wk_done = s["next_week"] - 1
    # postseason-aware header label
    try:
        import pickle as _pk
        _P = _pk.load(open(f'/home/claude/cfb2/state/playoff_s{s.get("season",1)}.pkl','rb'))
        _rr = _P.get("round_reached")
        _labelmap = {"R1":"Playoff First Round","R2":"Playoff Second Round","QF":"Quarterfinals",
                     "SF":"Semifinals","CHAMP":"National Championship"}
        _postlabel = _labelmap.get(_rr)
    except Exception:
        _postlabel = None
    ranked40, RT = SE.top40(s, with_ratings=True)
    lines = SE.storylines(s, n_weeks=min(2, max(1, wk_done)))
    P = {p["pid"]: p for tm in E.ROSTERS.values() for p in tm}

    season = s.get("season", 1)
    reg_pfx = f"S{season}W"          # current-season regular-game id prefix
    po_pfx = f"S{season}PO_"         # current-season playoff prefix
    ccg_pfx = f"S{season}CCG_"       # current-season conference-championship prefix
    teams_json = {}
    for t in U["teams"]:
        r = s["record"][t]
        cs = E.COACHES[t]
        sched = []
        for wk, h, a, ic in s["sched"]:
            if t not in (h, a): continue
            gid = f"{reg_pfx}{wk:02d}_{h}_{a}"
            e = {"wk": wk, "opp": a if t == h else h, "ha": "vs" if t == h else "at",
                 "type": "Conf" if ic else "Non-Conf"}
            if gid in db:
                b = db[gid]
                own = b["home_score"] if t == h else b["away_score"]
                opp = b["away_score"] if t == h else b["home_score"]
                e["res"] = f'{"W" if own > opp else "L"} {own}-{opp}'
                e["gid"] = gid
            sched.append(e)
        sched.sort(key=lambda x: x["wk"])
        # current-season postseason games only (CCG + playoff)
        for gid in sorted(db):
            if not (gid.startswith(po_pfx) or gid.startswith(ccg_pfx)): continue
            b = db[gid]
            if t not in (b["home"], b["away"]): continue
            own = b["home_score"] if t == b["home"] else b["away_score"]
            opp_s = b["away_score"] if t == b["home"] else b["home_score"]
            if gid.startswith(ccg_pfx): ptype = "Conf Championship @ " + b.get("venue","")
            elif "PO_CHAMP" in gid: ptype = "NATIONAL CHAMPIONSHIP @ " + b.get("venue","")
            elif "PO_SF" in gid: ptype = "Semifinal @ " + b.get("venue","")
            elif "PO_QF" in gid: ptype = "Quarterfinal @ " + b.get("venue","")
            elif "PO_R2" in gid: ptype = "Playoff R2 @ " + b.get("venue","")
            elif "PO_R1" in gid: ptype = "Playoff R1 @ " + b.get("venue","")
            else: ptype = b.get("venue","Postseason")
            sched.append({"wk": b.get("week", 99), "opp": (b["away"] if t == b["home"] else b["home"]),
                          "ha": "vs" if t == b["home"] else "at",
                          "type": ptype,
                          "res": f'{"W" if own > opp_s else "L"} {own}-{opp_s}', "gid": gid})
        sched.sort(key=lambda x: x["wk"])
        roster = []
        for pl in sorted(E.ROSTERS[t], key=lambda p: ("QB RB WR TE OL DL LB CB S K P ATH".split().index(p["pos"]), p["name"])):
            st = s["season_stats"].get(pl["pid"], {})
            gp = st.get("GP", None)
            line = []
            if st.get("Att"): line.append(f'{int(st.get("PassYds",0))} pass yds, {int(st.get("PassTD",0))} TD, {int(st.get("INT",0))} INT')
            if st.get("RushAtt"): line.append(f'{int(st.get("RushYds",0))} rush yds, {int(st.get("RushTD",0))} TD')
            if st.get("Rec"): line.append(f'{int(st.get("Rec",0))} rec, {int(st.get("RecYds",0))} yds, {int(st.get("RecTD",0))} TD')
            if st.get("Tackles"): line.append(f'{int(st.get("Tackles",0))} tkl' + (f', {st.get("Sacks",0):.0f} sk' if st.get("Sacks") else '') + (f', {int(st.get("INT_def",0))} INT' if st.get("INT_def") else ''))
            if st.get("FGAtt"): line.append(f'{int(st.get("FGMade",0))}/{int(st.get("FGAtt",0))} FG')
            tags = []
            if pl["cls"] == "Fr": tags.append("FR")
            if pl.get("transfer"): tags.append("TRANSFER")
            out_wks = s["inj_out"].get(pl["pid"], 0)
            if out_wks: tags.append("OUT (season)" if out_wks >= 99 else f"OUT {out_wks}wk")
            roster.append({"name": pl["name"], "pos": pl["pos"], "cls": pl["cls"], "arch": pl["arch"],
                           "stats": "; ".join(line), "tags": tags})
        teams_json[t] = {"conf": U["team_conf"][t], "tier": U["tiers"][U["team_conf"][t]],
                          "state": U["geo"][t]["state"], "mascot": U["geo"][t]["mascot"],
                          "rec": f'{r["W"]}-{r["L"]}', "conf_rec": f'{r["confW"]}-{r["confL"]}',
                          "pf": r["PF"], "pa": r["PA"],
                          "hc": f'{cs["HC"]["name"]}' + (" (interim)" if t in s.get("interims", {}) else ""),
                          "hfa": round(SE.dyn_hfa(s, t), 1),
                          "sched": sched, "roster": roster}
    standings = {}
    for conf, tl in U["conferences"].items():
        rows = sorted(tl, key=lambda t: (-(s["record"][t]["confW"] - s["record"][t]["confL"]),
                                          -(s["record"][t]["W"] - s["record"][t]["L"])))
        standings[conf] = [[t, f'{s["record"][t]["confW"]}-{s["record"][t]["confL"]}',
                             f'{s["record"][t]["W"]}-{s["record"][t]["L"]}'] for t in rows]
    boxes = {gid: _box_json(db[gid]) for gid in db}
    sos_rank = {t: i+1 for i, t in enumerate(sorted(SE.TEAMS, key=lambda x: -RT["sos"][x]))}
    po_rounds = [("Conference Championships",f"S{season}CCG_"), ("Playoff First Round",f"S{season}PO_R1_"),
                 ("Playoff Second Round",f"S{season}PO_R2_"), ("Quarterfinals",f"S{season}PO_QF_"),
                 ("Semifinals",f"S{season}PO_SF_"), ("National Championship",f"S{season}PO_CHAMP")]
    postseason = []
    for label, pref in po_rounds:
        games = []
        for gid in sorted(db):
            if not gid.startswith(pref): continue
            b = db[gid]
            games.append({"gid": gid, "home": b["home"], "away": b["away"],
                          "hs": b["home_score"], "as": b["away_score"], "ot": b["ot"],
                          "venue": b.get("venue","")})
        if games: postseason.append({"round": label, "games": games})
    media = s.get("media_poll_current") or s.get("media_poll_s2") or []
    media_json = [[rank, t, teams_json[t]["rec"]] for rank, t in media]
    data = {"week": wk_done, "season": season, "postlabel": _postlabel, "postseason": postseason, "top25": [[i+1, t, teams_json[t]["rec"], f"{RT['net'][t]:.1f}", f"{RT['adjO'][t]:.1f}", f"{RT['adjD'][t]:.1f}", f"{RT['em'][t]:+.1f}", sos_rank[t]] for i, t in enumerate(ranked40)],
            "media": media_json,
            "storylines": lines, "teams": teams_json, "standings": standings, "boxes": boxes,
            "firings": s["firings"]}
    payload = json.dumps(data).replace("</", "<\\/")
    tpl = HTML_TEMPLATE.replace("__DATA__", payload)
    with open(out_path, "w") as f:
        f.write(tpl)
    return out_path, len(tpl)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Roiland College Football</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f2f2ee;color:#1c2333}
header{background:#14213d;color:#fff;padding:14px 22px}
header h1{margin:0;font-size:21px} header .sub{color:#a9b4d0;font-size:12px;margin-top:3px}
nav{background:#0e1830;padding:0 22px;display:flex;gap:4px}
nav button{background:none;border:none;color:#c8d2ea;padding:11px 14px;cursor:pointer;font-size:13px;border-bottom:3px solid transparent}
nav button.on{color:#fff;border-color:#fca311}
main{max-width:1120px;margin:16px auto;padding:0 16px}
.panel{display:none}.panel.on{display:block}
.card{background:#fff;border:1px solid #dcdcd2;border-radius:8px;padding:14px;margin-bottom:14px}
table{border-collapse:collapse;width:100%;font-size:13px}
th{background:#e8eaf2;text-align:left;padding:5px 8px} td{padding:4px 8px;border-top:1px solid #eee}
tr.click:hover{background:#fef3dd;cursor:pointer}
.tag{display:inline-block;background:#fca311;color:#14213d;font-size:10px;font-weight:bold;border-radius:3px;padding:1px 5px;margin-left:4px}
.tag.out{background:#c1121f;color:#fff}
select,input{padding:7px;font-size:14px;border:1px solid #bbb;border-radius:5px}
.story{padding:6px 10px;border-left:4px solid #fca311;background:#fff;margin-bottom:6px;font-size:13px;border-radius:0 6px 6px 0}
#modal{display:none;position:fixed;inset:0;background:rgba(10,14,25,.72);z-index:50}
#modal .inner{background:#fff;max-width:860px;margin:4vh auto;max-height:88vh;overflow:auto;border-radius:10px;padding:18px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
h3{margin:8px 0 6px} .muted{color:#777;font-size:12px}
.confgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
</style></head><body>
<header><h1>Roiland College Football</h1><div class="sub" id="sub"></div></header>
<nav>
<button data-p="post">Postseason</button>
<button data-p="media">Media Top 40</button>
<button data-p="top" class="on">Top 25 & Storylines</button>
<button data-p="stand">Standings</button>
<button data-p="team">Teams</button>
</nav>
<main>
<div class="panel on" id="p-top">
  <div class="grid2">
    <div class="card"><h3>Top 40 - NET Rankings</h3><table id="t25"></table></div>
    <div class="card"><h3>Storylines</h3><div id="stories"></div></div>
  </div>
</div>
<div class="panel" id="p-post"><div id="postview"></div></div>
<div class="panel" id="p-media"><div id="mediaview"></div></div>
<div class="panel" id="p-stand"><div class="confgrid" id="standings"></div></div>
<div class="panel" id="p-team">
  <div class="card"><input id="tsearch" placeholder="Search team..." style="width:280px"> <select id="tsel"></select></div>
  <div id="tview"></div>
</div>
</main>
<div id="modal" onclick="this.style.display='none'"><div class="inner" onclick="event.stopPropagation()" id="minner"></div></div>
<script>
const D = __DATA__;
document.getElementById('sub').textContent = 'Season ' + D.season + (D.postlabel ? ' - ' + D.postlabel : ' - through Week ' + D.week) + '  |  every game simulated play-by-play with a mechanical seed (shown in each box score)';
function renderPost(){
  let v='';
  D.postseason.forEach(r=>{
    v+=`<div class="card"><h3>${r.round}</h3><table><tr><th>Matchup</th><th>Venue</th><th>Result</th></tr>`;
    r.games.forEach(g=>{
      v+=`<tr class="click" onclick="showBox('${g.gid}')"><td>${g.away} at ${g.home}</td><td>${g.venue}</td><td>${g.as}-${g.hs}${g.ot?' ('+g.ot+'OT)':''}</td></tr>`;
    });
    v+='</table></div>';
  });
  document.getElementById('postview').innerHTML=v;
}
renderPost();
function renderMedia(){
  let v='<div class="card"><h3>Media Top 40 <span style="font-weight:400;font-size:13px">(subjective voter poll — biased toward pedigree, hype, and flash; distinct from the objective NET ratings)</span></h3><table><tr><th>#</th><th>Team</th><th>Record</th></tr>';
  (D.media||[]).forEach(r=>{ v+=`<tr class="click" onclick="showTeam('${r[1]}')"><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td></tr>`; });
  v+='</table></div>';
  document.getElementById('mediaview').innerHTML=v;
}
renderMedia();
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); document.getElementById('p-'+b.dataset.p).classList.add('on');
});
// top25
let h='<tr><th>#</th><th>Team</th><th>Rec</th><th>NET</th><th>AdjO</th><th>AdjD</th><th>AdjEM</th><th>SOS rk</th></tr>';
D.top25.forEach(r=>h+=`<tr class="click" onclick="showTeam('${r[1]}')"><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}</td><td>${r[5]}</td><td>${r[6]}</td><td>${r[7]}</td></tr>`);
document.getElementById('t25').innerHTML=h;
document.getElementById('stories').innerHTML = D.storylines.map(s=>`<div class="story">${s}</div>`).join('');
// standings
let sh='';
for(const [conf,rows] of Object.entries(D.standings)){
  sh+=`<div class="card"><h3>${conf}</h3><table><tr><th>Team</th><th>Conf</th><th>Overall</th></tr>`;
  rows.forEach(r=>sh+=`<tr class="click" onclick="showTeam('${r[0]}')"><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td></tr>`);
  sh+='</table></div>';
}
document.getElementById('standings').innerHTML=sh;
// teams
const sel=document.getElementById('tsel');
Object.keys(D.teams).sort().forEach(t=>{const o=document.createElement('option');o.value=t;o.textContent=t;sel.appendChild(o)});
sel.onchange=()=>showTeam(sel.value);
document.getElementById('tsearch').oninput=e=>{
  const q=e.target.value.toLowerCase();
  const m=Object.keys(D.teams).find(t=>t.toLowerCase().includes(q));
  if(m){sel.value=m;showTeam(m);}
};
function showTeam(t){
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('on'));
  document.querySelector('[data-p=team]').classList.add('on');
  document.getElementById('p-team').classList.add('on');
  sel.value=t;
  const T=D.teams[t];
  let v=`<div class="card"><h3>${t} ${T.mascot} <span class="muted">(${T.state})</span></h3>
  <div class="muted">${T.conf} (${T.tier}) | HC ${T.hc} | Record ${T.rec} (${T.conf_rec}) | PF ${T.pf} / PA ${T.pa} | current HFA ${T.hfa} pts</div></div>`;
  v+='<div class="card"><h3>Schedule</h3><table><tr><th>Wk</th><th></th><th>Opponent</th><th>Type</th><th>Result</th></tr>';
  T.sched.forEach(g=>{
    const res=g.res?g.res:'-';
    const cl=g.gid?'click':'';
    v+=`<tr class="${cl}" ${g.gid?`onclick="showBox('${g.gid}')"`:''}><td>${g.wk}</td><td>${g.ha}</td><td>${g.opp}</td><td>${g.type}</td><td>${res}</td></tr>`;
  });
  v+='</table></div>';
  v+='<div class="card"><h3>Roster</h3><table><tr><th>Player</th><th>Pos</th><th>Class</th><th>Archetype</th><th>Season stats</th></tr>';
  T.roster.forEach(p=>{
    const tags=p.tags.map(x=>`<span class="tag ${x.startsWith('OUT')?'out':''}">${x}</span>`).join('');
    v+=`<tr><td>${p.name}${tags}</td><td>${p.pos}</td><td>${p.cls}</td><td>${p.arch}</td><td>${p.stats||''}</td></tr>`;
  });
  v+='</table></div>';
  document.getElementById('tview').innerHTML=v;
  window.scrollTo(0,0);
}
function rows(title,arr,heads){
  if(!arr.length)return'';
  let s=`<h3>${title}</h3><table><tr>${heads.map(x=>'<th>'+x+'</th>').join('')}</tr>`;
  arr.forEach(r=>s+='<tr>'+r.map(x=>'<td>'+x+'</td>').join('')+'</tr>');
  return s+'</table>';
}
function showBox(gid){
  const b=D.boxes[gid];
  let s=`<h2>${b.away} ${b.as} @ ${b.home} ${b.hs}${b.ot?' ('+b.ot+'OT)':''}</h2>
  <div class="muted">seed ${b.seed}${b.wp!=null?' | pregame home win prob '+Math.round(b.wp*100)+'%':''} - deterministic replay available on request</div>`;
  s+='<h3>Scoring</h3><table><tr><th>Q</th><th>Time</th><th>Team</th><th>Play</th><th>Score</th></tr>';
  b.scoring.forEach(p=>s+=`<tr><td>${p.q<=4?'Q'+p.q:'OT'+(p.q-4)}</td><td>${p.clk||''}</td><td>${p.team}</td><td>${p.desc}</td><td>${p.score}</td></tr>`);
  s+='</table>';
  if(b.injuries.length)s+='<h3>Injuries</h3>'+b.injuries.map(x=>`<div class="story">${x}</div>`).join('');
  s+='<div class="grid2"><div>'+ [rows(b.away+' Passing',b.A.passing,['Player','C/A','Yds','TD','INT']),
    rows(b.away+' Rushing',b.A.rushing,['Player','Car','Yds','TD']),
    rows(b.away+' Receiving',b.A.receiving,['Player','Rec','Yds','TD']),
    rows(b.away+' Defense',b.A.defense,['Player','Tkl','Sk','INT']),
    rows(b.away+' Kicking',b.A.kicking,['Player','FG','XP','Punts'])].join('') + '</div><div>' +
    [rows(b.home+' Passing',b.H.passing,['Player','C/A','Yds','TD','INT']),
    rows(b.home+' Rushing',b.H.rushing,['Player','Car','Yds','TD']),
    rows(b.home+' Receiving',b.H.receiving,['Player','Rec','Yds','TD']),
    rows(b.home+' Defense',b.H.defense,['Player','Tkl','Sk','INT']),
    rows(b.home+' Kicking',b.H.kicking,['Player','FG','XP','Punts'])].join('') + '</div></div>';
  document.getElementById('minner').innerHTML=s;
  document.getElementById('modal').style.display='block';
}
</script></body></html>"""
