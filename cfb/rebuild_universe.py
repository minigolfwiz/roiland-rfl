"""REBUILD STEP 1 — the universe, from the surviving exports.

Sources, in priority order:
  * roiland.html payload  -> conference, tier, state, mascot, colors for all 152 FBS
  * roiland_geography.json -> prestige, full_names, 372-school roll, coords, host cities
  * bundle universe.pkl    -> conferences, schemes, state_adj, directory, fixed_pairs

Canon applied (Dan, 2035): the three duplicate re-imports of FBS schools' RCBA display
names are deleted, and five RCBA institutions have no football -- leaving 369 schools
(152 FBS + 217 subdivision). The odd count is CORRECT by design.
"""
import json, pickle

PH = ['North Hatesei State', 'West Hatesei State', 'South Antiragal St']
NO_FOOTBALL = ['Crayellan Ag', 'East Costique Int.', 'Fiota Catskill',
               'Coachville Rev.', 'Eternal Fox JC']


def payload():
    h = open('/mnt/user-data/outputs/roiland_SNAPSHOT_s10w02_DO_NOT_OVERWRITE.html').read()
    i = h.index('const D = ') + len('const D = ')
    D, _ = json.JSONDecoder().raw_decode(h, i)
    return D


def main():
    D = payload()
    G = json.load(open('/mnt/user-data/outputs/roiland_geography.json'))
    U = pickle.load(open('state_s3_archive/universe.pkl', 'rb'))

    teams = sorted(D['teams'])
    assert len(teams) == 152, len(teams)

    # Corrections to the surviving geography export. It is the best source we have for
    # official RCBA display names, but it is not clean: two schools carry a third's name.
    # Dan caught this one. North Hatesei of the Great Fourteen are the Screamin' Goats --
    # the export gave them "North Hatesei State Tigers", which belongs to North Hatesei St
    # of the Brass Belt, a different school in the same state. The mascot field was right
    # the whole time, so only full_name was ever wrong, and no result or record was
    # touched: everything downstream keys off the school name, not the display name.
    FULL_NAME_FIXES = {
        'North Hatesei': "North Hatesei Screamin' Goats",
    }

    # ---- geo + conference, authoritative from the 2035 payload ----
    geo, team_conf = {}, {}
    for t in teams:
        e = D['teams'][t]
        gfull = (FULL_NAME_FIXES.get(t)
                 or G['schools'].get(t, {}).get('full_name')
                 or ('%s %s' % (t, e['mascot'])))
        geo[t] = {'state': e['state'], 'mascot': e['mascot'], 'full_name': gfull}
        team_conf[t] = e['conf']

    # ---- prestige from the geography export (S7-era; best surviving source) ----
    prestige = {t: G['schools'].get(t, {}).get('prestige', 50.0) for t in teams}

    # ---- the 369-school roll ----
    schools = {}
    for name, rec in G['schools'].items():
        if name in PH:
            continue
        schools[name] = ({'state': rec['state'], 'level': 'FBS'} if rec.get('level') == 'FBS'
                         else {'state': rec['state'], 'level': 'subdivision'})

    U['teams'] = teams
    U['team_conf'] = team_conf
    U['geo'] = geo
    U['prestige'] = prestige
    U['schools'] = schools
    U['no_football_schools'] = list(NO_FOOTBALL)
    # canon colors are the 152 FBS pairs Dan picked; subdivision guests were given
    # hash-random hsl at build time and are regenerated each build, never stored.
    U['team_colors'] = {t: D['colors'][t] for t in teams if t in D['colors']}
    U['state_coords'] = G.get('state_coords', U.get('state_coords', {}))
    U['state_adj'] = G.get('state_adj', U.get('state_adj', {}))
    U['host_cities'] = G.get('host_cities', {})
    U['bowls'] = G.get('bowls', {})
    # service academies (canon, stored as universe data in the lost build)
    U['service_academies'] = ['Northlight', 'Starfield', 'Marines', 'Eona Navy']

    # ---- locked rivalries, refreshed from the registry export ----
    R = json.load(open('/mnt/user-data/outputs/rivalry_data.json'))
    locked = R.get('locked') or []
    if locked:
        U['fixed_pairs'] = [{'week': p['week'], 'team_a': p['a'], 'team_b': p['b'],
                             'is_conf': bool(p.get('conf')),
                             'type': 'Rivalry Week' if p['week'] == 14 else 'Locked'}
                            for p in locked]
        U['rivalry_records'] = {('%s|%s' % (p['a'], p['b'])): p.get('record', {}) for p in locked}

    pickle.dump(U, open('state/universe.pkl', 'wb'))

    sub = len(schools) - 152
    print('universe rebuilt')
    print('  FBS teams          : %d' % len(teams))
    print('  conferences        : %d (%d P6 / %d L6)' % (
        len(set(team_conf.values())),
        sum(1 for c in set(team_conf.values()) if U['tiers'][c] == 'P6'),
        sum(1 for c in set(team_conf.values()) if U['tiers'][c] == 'L6')))
    print('  schools total      : %d = 152 FBS + %d subdivision  (%s)' % (
        len(schools), sub, 'EVEN' if len(schools) % 2 == 0 else 'ODD - canon'))
    print('  no-football schools: %d' % len(U['no_football_schools']))
    print('  team colors        : %d/152' % len(U['team_colors']))
    print('  locked rivalries   : %d' % len(U['fixed_pairs']))
    print('  prestige range     : %.1f - %.1f' % (min(prestige.values()), max(prestige.values())))


if __name__ == '__main__':
    main()
