"""REBUILD STEP 3 — the permanent games database and the seed registry.

RECOVERED for all 8,825 games (S1 2026 -> S10 2035 week 2): teams, scores, OT,
pregame win probability, the ORIGINAL mechanical seed, every scoring play with
quarter/clock/description/running score, and the injury log.

LOST: per-player box-score stat lines. Those lived only in the deleted pickle, so
stored boxes carry results and scoring plays but no player rows. Season totals for
the 2035 games played so far are preserved separately on each player's record.

The seed registry is rebuilt from the recovered seeds, which keeps the DOUBLE-SIM
GUARD intact -- no past game can ever be replayed into canon.
"""
import json, pickle, re, collections
import pbp_engine as E


def payload():
    h = open('/mnt/user-data/outputs/roiland_SNAPSHOT_s10w02_DO_NOT_OVERWRITE.html').read()
    i = h.index('const D = ') + len('const D = ')
    D, _ = json.JSONDecoder().raw_decode(h, i)
    return D


def clock_to_secs(clk):
    try:
        m, s = str(clk).split(':')
        return int(m) * 60 + int(s)
    except Exception:
        return 0


def parse_gid(gid):
    """S10W02_Home_Away / S9CCG_GreatFourteen / S8PO_QF1_... -> (season, week, kind)"""
    m = re.match(r'S(\d+)W(\d+)_', gid)
    if m:
        return int(m.group(1)), int(m.group(2)), 'reg'
    m = re.match(r'S(\d+)CCG', gid)
    if m:
        return int(m.group(1)), 15, 'ccg'
    m = re.match(r'S(\d+)PO', gid)
    if m:
        return int(m.group(1)), 16, 'po'
    return None, None, 'unknown'


def main():
    D = payload()
    db = {}
    kinds = collections.Counter()
    seasons = collections.Counter()
    seeds = {}

    for gid, b in D['boxes'].items():
        season, week, kind = parse_gid(gid)
        kinds[kind] += 1
        seasons[season] += 1
        plays = []
        for sp in (b.get('scoring') or []):
            sc = sp.get('score', '')
            try:
                a_, h_ = (int(x) for x in str(sc).split('-')[:2])
            except Exception:
                a_, h_ = 0, 0
            plays.append({'q': sp.get('q'), 'clock': clock_to_secs(sp.get('clk')),
                          'clk': sp.get('clk'), 'team': sp.get('team'),
                          'desc': sp.get('desc'), 'score': (a_, h_)})
        box = {
            'game_id': gid, 'home': b['home'], 'away': b['away'],
            'home_score': b['hs'], 'away_score': b['as'],
            'ot': b.get('ot', 0), 'seed': b.get('seed'),
            'pregame_home_wp': b.get('wp'),
            'scoring_plays': plays,
            'injuries': b.get('injuries', []),
            'stats': {},                      # LOST: player rows never recoverable
            'week': week, 'season': season, 'postseason': kind in ('ccg', 'po'),
            '_stats_lost': True,
        }
        db[gid] = box
        if b.get('seed') is not None:
            seeds[gid] = b['seed']

    pickle.dump(db, open('state/games_db.pkl', 'wb'))

    base = getattr(E, 'BASE_SEED', min(seeds.values()) if seeds else 0)
    counter = (max(seeds.values()) - base + 1) if seeds else 0
    reg = {'base': base, 'counter': max(0, counter), 'assigned': dict(seeds)}
    pickle.dump(reg, open('state/seed_registry.pkl', 'wb'))

    print('games database rebuilt')
    print('  games stored     : %d' % len(db))
    print('  by kind          : %s' % dict(kinds))
    print('  seasons present  : %s' % dict(sorted(seasons.items())))
    print('  scoring plays    : %d' % sum(len(b['scoring_plays']) for b in db.values()))
    print('  seeds recovered  : %d  (base %d, counter -> %d)' % (len(seeds), base, reg['counter']))
    print('  player stat rows : 0  (LOST with the pickle -- disclosed)')
    dup = len(seeds) - len(set(seeds.values()))
    print('  duplicate seeds  : %d' % dup)


if __name__ == '__main__':
    main()
