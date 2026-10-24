"""Map of every campus the Morning Gameview has visited this season (or a past one),
with the route, scores, and the rank each team held going INTO the game.
  python3 build_gameview_map.py            current season, plus next week's candidates as dashed pins
  python3 build_gameview_map.py 15         a finished season (reads gameview_s15 / season_archive)
Writes gameview_<year>.html from gameview_map_template.html."""
import sys, json, base64, pickle
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db
U = E.U; s = SE.load_state(); db = load_db()
cur = s['season']
sn = int(sys.argv[1]) if len(sys.argv) > 1 else cur
year = 2025 + sn
if sn == cur:
    gv = s.get('gameview') or {}; mh = s.get('media_history') or {}
    ch = {int(k): v for k, v in (s.get('committee_history') or {}).items()}
else:
    gv = s.get('gameview_s%d' % sn) or {}
    a = s['season_archive'].get(str(sn), {})
    mh = {(int(k) if k != 'pre' else k): v for k, v in (a.get('media_history') or {}).items()}
    ch = {int(k): v for k, v in (a.get('committee_history') or {}).items()}
def rank(t, w):
    # rank going INTO week w: the committee board after w-1 if one existed, else the media poll
    prev = w - 1
    lst = ch.get(prev) if prev in ch else (mh['pre'] if w == 0 else mh.get(prev))
    if lst and lst and not isinstance(lst[0], str): lst = [x[1] if isinstance(x, (list, tuple)) else x for x in lst]
    return (lst.index(t) + 1) if lst and t in lst[:25] else None
sc = U['school_coords']; played = {wk for wk, _ in s['results']} if sn == cur else set(range(15))
stops = []
for w in sorted(int(k) for k in gv):
    if w not in played: continue
    v = gv[w] if w in gv else gv[str(w)]; h, a = v['host'], v['away']
    g = db.get('S%dW%02d_%s_%s' % (sn, w, h, a))
    if not g: continue
    stops.append({'w': w, 'host': h, 'away': a, 'hs': g['home_score'], 'as': g['away_score'], 'ot': g.get('ot', 0),
                  'x': sc[h][0], 'y': sc[h][1], 'hr': rank(h, w), 'ar': rank(a, w),
                  'col': U['team_colors'].get(h, ['#444', '#999']), 'acol': U['team_colors'].get(a, ['#444', '#999']),
                  'state': U['geo'][h]['state']})
nxt = []
if sn == cur and s.get('next_week', 15) <= 14:
    import gameview as GV
    top, _ = GV.candidates(s, s['next_week'])
    nxt = [{'host': r['host'], 'x': sc[r['host']][0], 'y': sc[r['host']][1], 'col': U['team_colors'].get(r['host'], ['#444', '#999'])} for r in top]
n = len(stops)
sub = ('%d Saturday%s so far, %d campus%s · ranks are the board of record going into the game' % (n, '' if n == 1 else 's', n, '' if n == 1 else 'es')
       if sn == cur else 'Fifteen Saturdays, fifteen campuses · ranks are the ranking of record going into the game')
tpl = open('/home/claude/cfb2/gameview_map_template.html').read()
img = base64.b64encode(open('/home/claude/cfb2/state/roiland_map.png', 'rb').read()).decode()
out = tpl.replace('__IMG__', img).replace('__STOPS__', json.dumps(stops)).replace('__NEXT__', json.dumps(nxt)).replace('__YEAR__', str(year)).replace('__SUB__', sub)
path = '/home/claude/cfb2/gameview_%d.html' % year
open(path, 'w').write(out)
print('%s: %d stops, %d candidate pins' % (path, n, len(nxt)))
for x in stops: print('  wk %2d  %s%s at %s%s  %d-%d' % (x['w'], ('#%d ' % x['ar']) if x['ar'] else '', x['away'], ('#%d ' % x['hr']) if x['hr'] else '', x['host'], x['as'], x['hs']))
