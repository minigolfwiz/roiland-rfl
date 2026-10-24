"""Dan's 2037 award of championship sites: the 2028-2034 backfill and 2037-2044.

Sites are AWARDED, not rotated. This writes `U["champ_sites"]` and nothing interprets it
further -- `committee.champ_venue` is a pure lookup and raises for an unawarded season.

Five cities are new to the bid pool and are added to it: Stanton City (Stanton),
Chapel Rock (West Hatesei), Charlesville (Vaughn Bay), Palm Creek (Natzumakis) and
Canesta (Kaji Daun). Every state is checked against `U["state_coords"]` before anything
is written, because a title game in a state that does not exist would only surface years
later when something tried to compute a distance to it.

The 2028-2034 games were played before venues were stored, so their box scores carry no
venue at all. Those EMPTY fields are filled with the sites Dan has now declared. No
result, score or participant is touched -- this populates a field that was never
populated, which is restoring the record rather than rewriting it.
"""
import sys, pickle, shutil
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E
from games_db import load_db, save_db

UNI = '/home/claude/cfb2/state/universe.pkl'

AWARDS = {
    # --- backfill, 2028-2034 (these games are played; only the venue was missing) ---
    2028: ('Perth',        'Eona'),
    2029: ('San Saltadac', 'Orlot'),
    2030: ('Port Logan',   'Fiota'),
    2031: ('Ediville',     'Natzumakis'),
    2032: ('Denning',      'Diveo'),
    2033: ('Stanton City', 'Stanton'),
    2034: ('Burke Bay',    'Dove Island'),
    # --- awarded forward, 2037-2044 ---
    2037: ('Fiota Bay',    'Fiota'),
    2038: ('El Latigo',    'Skeenerland'),
    2039: ('Chapel Rock',  'West Hatesei'),
    2040: ('Stamford',     'Ciarralotta'),
    2041: ('Charlesville', 'Vaughn Bay'),
    2042: ('Palm Creek',   'Natzumakis'),
    2043: ('Canesta',      'Kaji Daun'),
    2044: ('Coachville',   'Stanton'),
}
BACKFILL = range(2028, 2035)


def main():
    U = pickle.load(open(UNI, 'rb'))
    states = set(U['state_coords'])

    bad = [(c, s) for c, s in AWARDS.values() if s not in states]
    if bad:
        raise SystemExit("these states are not in the universe: %s" % bad)

    sites = dict(U.get('champ_sites') or {})
    clash = [y for y in AWARDS if y in sites and tuple(sites[y]) != AWARDS[y]]
    if clash:
        raise SystemExit("these years already have a DIFFERENT site on record: %s"
                         % [(y, sites[y], AWARDS[y]) for y in clash])

    for y, (c, s) in AWARDS.items():
        sites[y] = [c, s]
    U['champ_sites'] = dict(sorted(sites.items()))

    cand = dict(U.get('champ_site_candidates') or {})
    added = []
    for c, s in AWARDS.values():
        if c not in cand:
            cand[c] = s
            added.append(c)
    U['champ_site_candidates'] = cand

    shutil.copy(UNI, UNI + '.pre_champ_awards')
    pickle.dump(U, open(UNI, 'wb'))

    # ---- fill the empty venue fields on the 2028-2034 title games -----------------
    db = load_db()
    filled, skipped = [], []
    for gid, b in db.items():
        g = str(gid)
        if 'CHAMP' not in g:
            continue
        sn = int(g[1:g.index('P')].rstrip('O_')) if False else int(g[1:].split('PO')[0])
        year = 2025 + sn
        if year not in BACKFILL:
            continue
        if b.get('venue'):
            skipped.append((year, b['venue']))
            continue
        c, s = AWARDS[year]
        b['venue'] = f"{c} ({s})"
        filled.append((year, b['venue']))
    if filled:
        save_db(db)
    return U, sorted(filled), sorted(skipped), added


if __name__ == '__main__':
    U, filled, skipped, added = main()
    print("new cities added to the bid pool:", ", ".join(added) or "none")
    print("\nchampionship sites on record (%d seasons):" % len(U['champ_sites']))
    for y, (c, s) in U['champ_sites'].items():
        print("   %d  %-14s %s" % (y, c, s))
    print("\nvenues written onto previously blank title-game box scores:")
    for y, v in filled:
        print("   %d  %s" % (y, v))
    if skipped:
        print("already had a venue, left alone:", skipped)
