"""Dan's 2038 rule: a conference title game is played in a state that hosts no team from
that conference, at a fixed site per conference.

This ends the drift that started in 2036, when `ccg.py` began drawing title-game sites
from `committee.assign_venue` -- i.e. from the playoff bowl pool. Since then the title
games have been consuming bowl slots, which is also why the Tinsel Bowl's first ever
appearance was a 2037 conference final. Each conference now has its own home for the
game, and the bowls are left entirely to the playoff.

Validated before anything is written: the state must exist in the universe, and it must
host NO member of that conference. All twelve passed. Dan picked these cities himself off
the distance tables; three of them (Diamond City, El Latigo, Denning) are also in the
championship host pool and three (Diamond City, Queensville, Underwood) share a name with
a programme, which is allowed and already had precedent -- Fiota Bay and Chapel Rock are
both host cities and schools.
"""
import sys, pickle, shutil
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E

UNI = '/home/claude/cfb2/state/universe.pkl'

SITES = {
    'Broad South':     ('Hughes City',  'South Antiragal'),
    'Great Fourteen':  ('Diamond City', 'Phangrine'),
    'Jyras Bay':       ('Queensville',  'Parchynt'),
    'Mountain Valley': ('El Latigo',    'Skeenerland'),
    'Power North':     ('Riverwake',    'Rogaela'),
    'Western Coast':   ('Denning',      'Diveo'),
    'Brass Belt':      ('Underwood',    'Hatesei'),
    'East Forest':     ('Classetto',    'Harrell'),
    'Evening Star':    ('Verigon City', 'Verigon'),
    'Low Sixteen':     ('Flatting',     'Ciarralotta'),
    'Southwestern':    ('Niana Vaw',    'North Hatesei'),
    'Vapor Stream':    ('Landon',       'Far Farris'),
}

FIRST_SEASON = 13      # 2038; 2037 and earlier stay as played


def main(write=True):
    U = pickle.load(open(UNI, 'rb'))
    CO, GEO, CONF = U['state_coords'], U['geo'], U['conferences']

    if set(SITES) != set(CONF):
        raise SystemExit("conference mismatch: %s" % (set(SITES) ^ set(CONF)))
    for conf, (city, st) in SITES.items():
        if st not in CO:
            raise SystemExit("%s: state %r is not in the universe" % (conf, st))
        bad = sorted(t for t in CONF[conf] if GEO[t]['state'] == st)
        if bad:
            raise SystemExit("%s: %s hosts conference members %s -- breaks the rule"
                             % (conf, st, bad))

    U['ccg_sites'] = {c: [city, st] for c, (city, st) in SITES.items()}
    U['ccg_sites_from_season'] = FIRST_SEASON
    if write:
        shutil.copy(UNI, UNI + '.pre_ccg_sites')
        pickle.dump(U, open(UNI, 'wb'))
    return U


if __name__ == '__main__':
    U = main()
    print("conference title-game sites, from %d (%d):" % (FIRST_SEASON, 2025 + FIRST_SEASON))
    for c in sorted(U['ccg_sites']):
        city, st = U['ccg_sites'][c]
        print("   %-17s %-14s %s" % (c, city, st))
