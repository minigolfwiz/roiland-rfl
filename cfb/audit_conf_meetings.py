"""Audit: how often conference foes have met in the REGULAR SEASON over the sim era
(2026-2039, S1-S14). Conference games only (both in the same conference), CCGs and
playoffs excluded. Dan asked for this at the end of 2039. Writes state/conf_meetings.json."""
import sys, re, json, collections
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E
from games_db import load_db

def main():
    U = E.U; db = load_db(); tc = U['team_conf']
    n_seasons = 0
    meets = collections.defaultdict(list)       # pair -> [season,...]
    home = collections.Counter()                 # (host, visitor)
    for gid, b in db.items():
        m = re.match(r'S(\d+)W(\d+)_', gid)
        if not m: continue
        sn = int(m.group(1)); n_seasons = max(n_seasons, sn)
        h, a = b['home'], b['away']
        if h not in tc or a not in tc or tc[h] != tc[a]: continue
        meets[tuple(sorted((h, a)))].append(sn)
        home[(h, a)] += 1
    out = {'seasons': n_seasons, 'conferences': {}}
    for conf in U['tiers']:
        teams = sorted(t for t in tc if tc[t] == conf)
        pairs = []
        for i, x in enumerate(teams):
            for y in teams[i + 1:]:
                ss = sorted(meets.get((x, y), []))
                pairs.append({'a': x, 'b': y, 'n': len(ss), 'seasons': ss,
                              'a_home': home[(x, y)], 'b_home': home[(y, x)],
                              'last': ss[-1] if ss else None,
                              'gap': n_seasons - ss[-1] if ss else n_seasons})
        cnt = collections.Counter(p['n'] for p in pairs)
        out['conferences'][conf] = {'teams': teams, 'pairs': pairs,
                                    'dist': dict(sorted(cnt.items())), 'size': len(teams)}
    json.dump(out, open('/home/claude/cfb2/state/conf_meetings.json', 'w'), separators=(',', ':'))
    return out

if __name__ == '__main__':
    o = main(); N = o['seasons']
    for conf, d in o['conferences'].items():
        ps = d['pairs']; n = d['size']
        # conference games per team per season
        per = sum(p['n'] for p in ps) * 2 / n / N
        print('\n%s (%d teams, %.1f conf games/team/yr): meetings per pair over %d seasons' % (conf, n, per, N))
        print('   dist', d['dist'], ' never met:', sum(1 for p in ps if p['n'] == 0),
              ' every year:', sum(1 for p in ps if p['n'] == N))
        hi = sorted(ps, key=lambda p: -p['n'])[:4]
        lo = sorted(ps, key=lambda p: (p['n'], -p['gap']))[:4]
        print('   most :', ', '.join('%s-%s %d' % (p['a'], p['b'], p['n']) for p in hi))
        print('   least:', ', '.join('%s-%s %d (last %s)' % (p['a'], p['b'], p['n'], 2025 + p['last'] if p['last'] else 'never') for p in lo))
        skew = [p for p in ps if p['n'] >= 4 and abs(p['a_home'] - p['b_home']) >= 3]
        if skew: print('   venue skew >=3:', ', '.join('%s %d-%d %s' % (p['a'], p['a_home'], p['b_home'], p['b']) for p in skew))
