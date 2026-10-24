"""REBUILD STEP 2 — rosters and coaching staffs.

RECOVERED from the 2035 snapshot: every player's name, position, class, archetype,
current ability, season stat line and status tags, for all 152 teams.

REGENERATED (disclosed -- these were lost with the pickles and are fresh dice):
  pid, dur, rep, discipline, mob, attrs, inj_hist, pot(ceiling)
Past canon is unaffected: results already played are immutable. Only FUTURE
trajectories differ from what the lost state would have produced.

Coaching: HC names and tenure are RECOVERED. HC skill is INFERRED from program
prestige and current form rather than rolled blind, which keeps the sport's
coaching hierarchy roughly where the canon says it is. OC/DC are fully regenerated.
"""
import json, pickle, random, re, collections

SEED = 20350003
rng = random.Random(SEED)


def payload():
    h = open('/mnt/user-data/outputs/roiland_SNAPSHOT_s10w02_DO_NOT_OVERWRITE.html').read()
    i = h.index('const D = ') + len('const D = ')
    D, _ = json.JSONDecoder().raw_decode(h, i)
    return D


def load_derive_attrs():
    """Pull derive_attrs out of gen_rosters.py so attribute shapes stay engine-faithful."""
    src = open('gen_rosters.py').read()
    a = src.index('def derive_attrs(')
    b = src.index('rosters = {}', a)
    ns = {'rng': rng}
    exec(src[a:b], ns)
    return ns['derive_attrs']


# position-weighted discipline (handoff: OL/DL/DB higher, K/QB lower; range ~0.45-1.9)
DISC_MU = {'OL': 1.22, 'DL': 1.20, 'CB': 1.15, 'S': 1.10, 'LB': 1.05, 'TE': 0.95,
           'WR': 0.92, 'RB': 0.88, 'ATH': 0.90, 'QB': 0.72, 'K': 0.60, 'P': 0.60}

# ceiling headroom by class: underclassmen have more room left
POT_HEAD = {'Fr': (0.55, 1.75), 'So': (0.35, 1.30), 'Jr': (0.18, 0.85),
            'Sr': (0.05, 0.40), 'RS': (0.30, 1.10)}


def main():
    D = payload()
    U = pickle.load(open('state/universe.pkl', 'rb'))
    derive_attrs = load_derive_attrs()

    rosters = {}
    pid = 0
    tagcount = collections.Counter()
    inj_out = {}

    for team in U['teams']:
        out = []
        for r in D['teams'][team]['roster']:
            pid += 1
            pos, abil, cls, arch = r['pos'], float(r['abil']), r['cls'], r['arch']
            lo, hi = POT_HEAD.get(cls, (0.3, 1.0))
            pot = round(min(9.99, abil + rng.uniform(lo, hi)), 2)
            attrs = derive_attrs(pos, abil, arch, cls)
            disc = round(max(0.45, min(1.9, rng.gauss(DISC_MU.get(pos, 1.0), 0.22))), 3)
            pl = {
                'pid': pid, 'name': r['name'], 'team': team, 'pos': pos, 'cls': cls,
                'arch': arch, 'abil': abil,
                'pot': pot,
                'dur': round(max(0.15, min(0.95, rng.gauss(0.62, 0.15))), 3),
                'rep': 0.0,
                'inj_hist': [],
                'discipline': disc,
                'attrs': attrs,
                'mob': attrs.get('mob', round(3.5 + rng.gauss(0, 1.0), 2)),
                '_s10_stats': r.get('stats', ''),
            }
            for tg in (r.get('tags') or []):
                tagcount[tg] += 1
                if tg == 'TRANSFER':
                    pl['transfer'] = True
                elif tg.startswith('OUT'):
                    pl['inj_hist'] = ['2035']
                    inj_out[pid] = 99 if 'season' in tg else int(re.sub(r'\D', '', tg) or 1)
            out.append(pl)
        rosters[team] = out

    pickle.dump(rosters, open('state/rosters.pkl', 'wb'))

    # ---------------- coaching staffs ----------------
    coaches = {}
    OFF = list(U['OFF_SCHEMES']); DEF = list(U['DEF_SCHEMES'])
    for team in U['teams']:
        e = D['teams'][team]
        p = U['prestige'][team]
        w, l = (int(x) for x in e['rec'].split('-')[:2])
        form = (w / max(1, w + l)) - 0.5
        # HC skill inferred: prestige-anchored, nudged by current form, noise kept small
        hc_skill = max(1.0, min(9.8, rng.gauss(3.6 + (p / 100) * 4.6 + form * 1.2, 0.85)))
        hc_age = int(max(33, min(70, rng.gauss(50 - min(12, e['hc_yrs']) * 0.3, 8))))
        staff = {'HC': {'name': e['hc'], 'skill': round(hc_skill, 2),
                        'tenure': int(e['hc_yrs']), 'aggression': round(rng.uniform(.08, .92), 2),
                        'age': hc_age,
                        'retire_age': int(max(hc_age + 3, min(74, rng.gauss(66, 3.2))))}}
        for role in ('OC', 'DC'):
            sk = max(1.0, min(9.6, rng.gauss(3.4 + (p / 100) * 3.6, 1.25)))
            age = int(max(31, min(62, rng.gauss(44, 7))))
            staff[role] = {'name': None, 'skill': round(sk, 2),
                           'tenure': rng.choices([0, 1, 2, 3, 4, 6, 9], weights=[18, 16, 15, 14, 12, 15, 10])[0],
                           'aggression': round(rng.uniform(.08, .92), 2),
                           'age': age,
                           'retire_age': int(max(age + 4, min(74, rng.gauss(66, 3.2))))}
        staff['patience'] = round(rng.gauss(0, 1.0), 3)
        staff['hfa_base'] = float(e.get('hfa', 3.0))
        staff['team_discipline'] = round(max(0.8, min(1.25, 1.0 + (hc_skill - 5) * 0.03 + rng.gauss(0, 0.05))), 3)
        staff['off_scheme'] = rng.choice(OFF)
        staff['def_scheme'] = rng.choice(DEF)
        coaches[team] = staff

    # name the coordinators from the engine's own generator, avoiding every HC name
    import importlib.util
    spec = importlib.util.spec_from_file_location('names_v2', 'names_v2.py')
    nv = importlib.util.module_from_spec(spec); spec.loader.exec_module(nv)
    used = {c['HC']['name'] for c in coaches.values()}
    used |= {p['name'] for r in rosters.values() for p in r}
    for team in U['teams']:
        for role in ('OC', 'DC'):
            nm = nv.pick_name_v2(rng, used)
            nm = nm[0] if isinstance(nm, (tuple, list)) else nm
            used.add(nm)
            coaches[team][role]['name'] = nm

    pickle.dump(coaches, open('state/coaches.pkl', 'wb'))

    sizes = [len(v) for v in rosters.values()]
    print('rosters + staffs rebuilt   (regen seed %d)' % SEED)
    print('  teams %d | players %d | sizes %d-%d' % (len(rosters), sum(sizes), min(sizes), max(sizes)))
    print('  classes:', dict(sorted(collections.Counter(
        p['cls'] for r in rosters.values() for p in r).items())))
    print('  tags carried over:', dict(tagcount))
    print('  injured carried into wk3: %d' % len(inj_out))
    print('  HC skill range %.2f-%.2f | coordinators generated %d' % (
        min(c['HC']['skill'] for c in coaches.values()),
        max(c['HC']['skill'] for c in coaches.values()), len(coaches) * 2))
    dupes = [n for n, c in collections.Counter(
        [c[r]['name'] for c in coaches.values() for r in ('HC', 'OC', 'DC')]).items() if c > 1]
    print('  duplicate coach names:', dupes or 'none')
    json.dump(inj_out, open('state/_inj_out_seed.json', 'w'))


if __name__ == '__main__':
    main()
