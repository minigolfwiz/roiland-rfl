"""REBUILD STEP 4 — season state at 2035 (Season 10), ready to simulate Week 3.

RECOVERED: the full 2035 schedule (with Dan's bye spec and the anti-previous-season
rivalry hosts baked in), every record, conference record, PF/PA, the media poll and
its previous week, storylines, and the complete 106-season championship canon.

REGENERATED: heat / pressure / streak / preseason ratings (these are derived
in-season signals, not results).
"""
import json, pickle, re, collections

# ---------------------------------------------------------------------------
# THE CHAMPIONSHIP CANON, 1929-2034 (106 seasons).
# Poll Era 1929-1978 could crown co-champions; 21 seasons did, including the
# four-way 1946 and 1962. Championship Game Era 1979- crowns one, with a
# runner-up. Greene's 1937-40 four-peat and North Hatesei's 1956-58 three-peat
# are the era's landmarks.
# ---------------------------------------------------------------------------
POLL_ERA = {
    1929: ['Greene'], 1930: ['Greene', 'Wolford'], 1931: ['Greene', 'Verigon State'],
    1932: ['North Hatesei'], 1933: ['Crayellan', 'Greene'], 1934: ['Crayellan', 'Will Tech'],
    1935: ['Central Stanton', 'Fiota Bay'], 1936: ['Diamond City', 'Hatesei'],
    1937: ['Greene'], 1938: ['Greene'], 1939: ['Greene'], 1940: ['Greene'],
    1941: ['Barhold'], 1942: ['Vaughn Bay'], 1943: ['North Hatesei', 'Verigon State'],
    1944: ['Verigon State'], 1945: ['Ciarralotta', 'S Antiragal State'],
    1946: ['Kaji Daun', 'Marines', 'North Hatesei', 'Will Tech'],
    1947: ['Eona'], 1948: ['Central Stanton'], 1949: ['Stanton', 'Tasson'],
    1950: ['Antiragal'], 1951: ['Greene', 'Yrei Trobniy'], 1952: ['Greene'],
    1953: ['Dove Island', 'Ranroman', 'Will Tech'], 1954: ['Stanton'],
    1955: ['Far Farris', 'North Hatesei'], 1956: ['North Hatesei'],
    1957: ['North Hatesei'], 1958: ['North Hatesei'], 1959: ['Krobe', 'North Hatesei'],
    1960: ['Ciarralotta'], 1961: ['Hatesei'],
    1962: ['Costique', 'Hatesei', 'Kaji Daun', 'Will Tech'],
    1963: ['Wolford'], 1964: ['Tasson'], 1965: ['Will Tech'], 1966: ['Central Stanton'],
    1967: ['Rogaela State'], 1968: ['Central Stanton', 'Roosevelt State'],
    1969: ['Orlot'], 1970: ['South Antiragal', 'Will Tech'],
    1971: ['Marblehead', 'North Hatesei'],
    1972: ['Natzumakis', 'Phangrine State', 'UNN'], 1973: ['Tasson'],
    1974: ['Central Stanton'], 1975: ['Central Stanton', 'Ranroman State'],
    1976: ['Barhold', 'Dove Island', 'North Hatesei'], 1977: ['Harrell'],
    1978: ['North Hatesei'],
}
TITLE_GAME_ERA = {
    1979: ('North Hatesei', 'Northlight'), 1980: ('Costique River', 'Ranroman'),
    1981: ('Crayellan', 'North Hatesei'), 1982: ('Ranroman', 'Dove Island'),
    1983: ('Ranroman', 'Kaji Kita'), 1984: ('Eternal Fox', 'Yrei Trobniy'),
    1985: ('Verigon State', 'Hatesei'), 1986: ('Hatesei', 'Dove Island'),
    1987: ('Barhold', 'Orlot'), 1988: ('North Hatesei', 'Northlight'),
    1989: ('Greene', 'Northlight'), 1990: ('South Antiragal', 'UNN'),
    1991: ('Greene', 'Crayellan'), 1992: ('Crayellan', 'Greene'),
    1993: ('Will Tech', 'Natzumakis'), 1994: ('Dove Island', 'Greene'),
    1995: ('North Hatesei', 'Barhold State'), 1996: ('Greene', 'Lornaman'),
    1997: ('Riveral', 'Will Tech'), 1998: ('Will Tech', 'Riveral'),
    1999: ('Riveral', 'Will Tech'), 2000: ('S Antiragal State', 'UNN'),
    2001: ('Will Tech', 'Eona'), 2002: ('Will Tech', 'Ranroman'),
    2003: ('Crayellan', 'Will Tech'), 2004: ('North Hatesei', 'Diveo State'),
    2005: ('Dietsche', 'UNN'), 2006: ('Northlight', 'East Costique'),
    2007: ('Ranroman State', 'Crayellan'), 2008: ('Dove Island', 'UNN'),
    2009: ('North Hatesei', 'Dietsche'), 2010: ('North Hatesei', 'Dietsche'),
    2011: ('Crayellan', 'Hatesei'), 2012: ('Ciarralotta', 'Costique'),
    2013: ('Kaji Daun', 'Will Tech'), 2014: ('UNN', 'Tengus'),
    2015: ('North Hatesei', 'Fiota Bay'), 2016: ('Fiota Bay', 'Far Farris'),
    2017: ('Fiota Bay', 'Crayellan'), 2018: ('UNN', 'Barhold'),
    2019: ('Dietsche', 'UNN'), 2020: ('Greene', 'Ciarralotta State'),
    2021: ('Barhold', 'Crayellan'), 2022: ('Stanton', 'Kingdom Valley'),
    2023: ('Barhold', 'Kingdom Valley'), 2024: ('North Hatesei', 'Crayellan'),
    2025: ('North Hatesei', 'Coachville'),
    # ---- the simulated era: nine seasons, nine different champions ----
    2026: ('Tengus State', 'Barhold Valley'), 2027: ('Diamond City', 'Ranroman'),
    2028: ('Park Island', 'Ciarralotta'), 2029: ('Central Stanton', 'Ciarralotta State'),
    2030: ('North Hatesei', 'Stanton State'), 2031: ('Ek Tech', 'UN Ediville'),
    2032: ('Kaji Daun', 'Marblehead'), 2033: ('UN Ediville', 'Ranroman State'),
    2034: ('Ranroman State', 'Orlot'),
}


def payload():
    h = open('/mnt/user-data/outputs/roiland_SNAPSHOT_s10w02_DO_NOT_OVERWRITE.html').read()
    i = h.index('const D = ') + len('const D = ')
    D, _ = json.JSONDecoder().raw_decode(h, i)
    return D


def build_history(old):
    hist = dict(old) if old else {}
    champ, book = {}, collections.defaultdict(lambda: {'titles': [], 'runnerup': []})
    for yr, winners in POLL_ERA.items():
        champ[yr] = (winners[0], None) if len(winners) == 1 else (tuple(winners), None)
        for w in winners:
            book[w]['titles'].append(yr)
    for yr, (w, ru) in TITLE_GAME_ERA.items():
        champ[yr] = (w, ru)
        book[w]['titles'].append(yr)
        if ru:
            book[ru]['runnerup'].append(yr)
    for t in book:
        book[t]['titles'].sort()
        book[t]['runnerup'].sort()
    hist['champ'] = champ
    hist['book'] = {k: dict(v) for k, v in book.items()}
    hist['eras'] = {
        'poll': '1929-1978 (selectors could crown co-champions; 21 split seasons)',
        'championship': '1979-2015 (single national championship game)',
        'playoff_8': '2016-2025 (8-team playoff)',
        'current': '2026- (24-team playoff)',
    }
    return hist


def main():
    D = payload()
    U = pickle.load(open('state/universe.pkl', 'rb'))
    teams = set(U['teams'])
    old = pickle.load(open('state_s3_archive/season_state.pkl', 'rb'))

    # ---- schedule: rebuilt from the per-team views, deduped by game id ----
    # Played games carry a gid (S10Wnn_<home>_<away>); future games carry only
    # ha/opp, so dedupe on (week, matchup) and take home/away from 'ha'.
    sched, seen = [], set()
    guests = set()
    for t in U['teams']:
        for g in D['teams'][t]['sched']:
            wk, opp = g['wk'], g['opp']
            key = (wk, frozenset((t, opp)))
            if key in seen:
                continue
            seen.add(key)
            home, away = (t, opp) if g['ha'] == 'vs' else (opp, t)
            gid = g.get('gid')
            if gid:                       # played: the id is authoritative on hosting
                body = gid.split('_', 1)[1]
                if not body.startswith(home):
                    home, away = away, home
            sched.append((wk, home, away, g['type'] == 'Conf'))
            if opp not in teams:
                guests.add(opp)
    sched.sort()

    # ---- records, straight from the snapshot ----
    record = {}
    for t in U['teams']:
        e = D['teams'][t]
        w, l = (int(x) for x in e['rec'].split('-')[:2])
        cw, cl = (int(x) for x in e['conf_rec'].split('-')[:2])
        record[t] = {'W': w, 'L': l, 'confW': cw, 'confL': cl,
                     'PF': e['pf'], 'PA': e['pa']}

    media = [(r[0], r[1]) for r in D.get('media', [])] if D.get('media') else []
    prev = [(r[0], r[1]) for r in D.get('pollprev', [])] if D.get('pollprev') else []

    inj_out = {int(k): v for k, v in json.load(open('state/_inj_out_seed.json')).items()}

    s = {
        'season': 10, 'next_week': 3,
        'sched': sched, 'schedule_s10': list(sched),
        'record': record,
        'media_poll_current': media, 'media_poll_prev': prev,
        'sub_opponents': sorted(guests),
        'storylines': D.get('storylines', []),
        'firings': [], 'interims': {}, 'results': [], 'weekly_perf': [],
        'season_stats': {}, 'inj_log': [], 'inj_recent': {}, 'inj_out': inj_out,
        'heat': {t: 0.0 for t in U['teams']},
        'pressure': {t: 0.0 for t in U['teams']},
        'streak': {t: 0 for t in U['teams']},
        'preseason': {t: round(3.5 + U['prestige'][t] / 100 * 4.5, 2) for t in U['teams']},
        'patience': {t: 0.0 for t in U['teams']},
        'history': build_history(old.get('history')),
        'rebuild_note': ('Rebuilt 2035-10 from the S10W02 site snapshot after the container '
                         'reset. Results are canon and untouched; hidden player fields, '
                         'coordinator staffs and coach skills were regenerated.'),
    }
    pickle.dump(s, open('state/season_state.pkl', 'wb'))

    wk = collections.Counter(x[0] for x in sched)
    per = collections.defaultdict(set)
    for w, h, a, ic in sched:
        per[h].add(w); per[a].add(w)
    byes = {t: [w for w in range(0, 15) if w not in per[t]] for t in U['teams']}
    consec = [t for t, b in byes.items() if any(b[i + 1] == b[i] + 1 for i in range(len(b) - 1))]

    print('season state rebuilt -> 2035 (season 10), next week 3')
    print('  schedule games   : %d across weeks %d-%d' % (len(sched), min(wk), max(wk)))
    print('  week 0 slate     : %d games' % wk[0])
    print('  byes per team    : %s  (consecutive-bye teams: %d)' % (
        sorted(set(len(b) for b in byes.values())), len(consec)))
    print('  subdivision guests: %d' % len(guests))
    print('  poll recovered   : current %d / previous %d' % (len(media), len(prev)))
    print('  injured carried  : %d' % len(inj_out))
    print('  champions canon  : %d seasons (%d-%d), %d split-title years' % (
        len(s['history']['champ']), min(s['history']['champ']), max(s['history']['champ']),
        sum(1 for v in s['history']['champ'].values() if isinstance(v[0], tuple))))
    nh = s['history']['book']['North Hatesei']
    print('  North Hatesei    : %d titles (latest %d)' % (len(nh['titles']), max(nh['titles'])))
    rs = s['history']['book']['Ranroman State']
    print('  Ranroman State   : titles %s | runner-up %s' % (rs['titles'], rs['runnerup']))


if __name__ == '__main__':
    main()
