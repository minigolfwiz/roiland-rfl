"""Playoff pedigree of the current field: every title and final since 1929 from the
canon book, and the season-by-season record and playoff depth for the simulated era
(2026 on) from the games database. Written for the 2039 field (Dan, 2026-10-12).
Output: state/pedigree.json for pedigree_template.html."""
import sys, re, json, pickle, os, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E
from games_db import load_db

ROUNDS = {'R1': 1, 'R2': 2, 'QF': 3, 'SF': 4, 'CHAMP': 5}
FIRST_SIM_YEAR = 2026


def main(out='/home/claude/cfb2/state/pedigree.json'):
    s = SE.load_state(); db = load_db(); U = E.U
    season = s['season']; year = 2025 + season
    book = s['history']['book']; champ = s['history']['champ']
    po = pickle.load(open('/home/claude/cfb2/state/playoff_s%d.pkl' % season, 'rb'))
    seeds = {t: int(v) for t, v in po['seeds'].items()}

    # ---- sim era, from the games database ----
    recs = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    depth = collections.defaultdict(dict)
    for gid, b in db.items():
        m = re.match(r'S(\d+)', gid)
        if not m: continue
        sn = int(m.group(1))
        h, a = b['home'], b['away']
        hw = b['home_score'] > b['away_score']
        w, l = (h, a) if hw else (a, h)
        if 'PO_' in gid:
            r = ROUNDS[re.search(r'PO_(R1|R2|QF|SF|CHAMP)', gid).group(1)]
            depth[l][sn] = max(depth[l].get(sn, 0), r)
            depth[w][sn] = max(depth[w].get(sn, 0), r + 1)      # a title is 6
            continue
        for t, won in ((h, hw), (a, not hw)):
            if t in U['teams']:
                recs[t][sn][0 if won else 1] += 1

    teams = []
    for t, seed in sorted(seeds.items(), key=lambda x: x[1]):
        b = book.get(t, {})
        titles = sorted(b.get('titles', [])); ru = sorted(b.get('runnerup', []))
        semis = sorted(b.get('semis', []))
        sim = []
        for sn in range(1, season + 1):
            yr = 2025 + sn
            w, l = recs[t].get(sn, [0, 0])
            d = depth[t].get(sn, 0)
            # a title-year in the book is authoritative if the db round is missing
            if yr in titles and d < 6: d = 6
            sim.append({'year': yr, 'w': w, 'l': l, 'depth': d})
        teams.append({
            'team': t, 'seed': seed, 'conf': U['team_conf'][t], 'tier': U['tiers'][U['team_conf'][t]],
            'colors': U['team_colors'].get(t, ['#444', '#999']),
            'rec': '%d-%d' % (s['record'][t]['W'], s['record'][t]['L']),
            'titles': titles, 'runnerup': ru, 'semis': semis,
            'first_title': titles[0] if titles else None, 'last_title': titles[-1] if titles else None,
            'n_titles': len(titles), 'n_finals': len(titles) + len(ru),
            'sim': sim,
            'po_trips': sum(1 for x in sim if x['depth'] > 0) + (1 if seed else 0),
        })
    payload = {'season': season, 'year': year, 'first_year': min(champ), 'sim_from': FIRST_SIM_YEAR,
               'teams': teams}
    json.dump(payload, open(out, 'w'), separators=(',', ':'))
    return payload


if __name__ == '__main__':
    p = main()
    for t in p['teams']:
        print('%2d %-20s titles %2d (last %s)  finals %2d  sim: %s' % (
            t['seed'], t['team'], t['n_titles'], t['last_title'] or '-', t['n_finals'],
            ' '.join(str(x['depth']) for x in t['sim'])))
