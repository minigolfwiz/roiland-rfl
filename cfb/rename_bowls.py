"""Dan's 2037 ruling on the bowl pool.

  * drop the Lumber Bowl (Burke Bay, Dove Island) from the pool
  * rename the Wharf Bowl (Port Logan, Fiota)        -> Lumber Bowl
  * rename the Tinsel Bowl (Ediville, Natzumakis)    -> Star Bowl
  * rename the Steampower Bowl (Coachville, Stanton) -> Steam Bowl

That leaves six, which is what the rotation rule needs: four quarterfinal sites and two
semifinal sites a year, no bowl a semifinal site more often than every three seasons.

NOTE: when this was first run, `state/universe.pkl` had ALREADY had the drop and the
Wharf->Lumber rename applied by something outside this session (it wrote
`universe.pkl.pre_bowlpool` at 15:19:17 on 2037-10-08, a minute before Dan gave the
instruction). So this works by CITY, not by name: the city is the thing that does not
move, which makes the script idempotent and safe to re-run whatever state it finds.

History is NOT rewritten. Every box score keeps the venue string it was played under, so
the record book says what it said. The consequence is that "Lumber Bowl" means Burke Bay
in 2036-37 and Port Logan from 2038, which the city in each venue string disambiguates.
`bowls_defunct` and `bowls_renamed` are written into the universe so anything reading an
old name can resolve it without guessing.
"""
import sys, pickle, shutil
sys.path.insert(0, '/home/claude/cfb2')

PATH = '/home/claude/cfb2/state/universe.pkl'

# keyed on city, which never changes: city -> (final name, state)
TARGET = {
    'Stamford':   ('501 Bowl',    'Ciarralotta'),
    'Kirkwood':   ('Redwood Bowl', 'Crayellan'),
    'Ediville':   ('Star Bowl',   'Natzumakis'),     # was Tinsel
    'Coachville': ('Steam Bowl',  'Stanton'),        # was Steampower
    'Port Logan': ('Lumber Bowl', 'Fiota'),          # was Wharf
    'Billiataho': ('Copper Bowl', 'Roosevelt'),
}
DROP_CITY = 'Burke Bay'                              # the old Lumber Bowl, out of the pool
ROLL = ['501 Bowl', 'Redwood Bowl', 'Star Bowl', 'Steam Bowl', 'Lumber Bowl', 'Copper Bowl']
RENAMED = {'Wharf Bowl': 'Lumber Bowl', 'Tinsel Bowl': 'Star Bowl',
           'Steampower Bowl': 'Steam Bowl'}


def main(write=True):
    U = pickle.load(open(PATH, 'rb'))
    old = dict(U['bowls'])

    new, seen_drop = {}, False
    for name, (city, state) in old.items():
        if city == DROP_CITY:
            seen_drop = True
            continue
        if city not in TARGET:
            raise SystemExit("unexpected bowl city %r (%s) -- not in the ruling" % (city, name))
        final, st = TARGET[city]
        if st != state:
            raise SystemExit("%s: state is %r, expected %r" % (city, state, st))
        new[final] = [city, state]

    missing = [c for c in TARGET if c not in {v[0] for v in new.values()}]
    if missing:
        raise SystemExit("these bowls are not in the universe at all: %s" % missing)
    assert len(new) == 6, (len(new), sorted(new))
    assert sorted(new) == sorted(ROLL), (sorted(new), sorted(ROLL))

    U['bowls'] = {n: new[n] for n in ROLL}            # stored in rotation order
    U['bowl_roll'] = list(ROLL)
    U['bowls_defunct'] = {'Lumber Bowl': [DROP_CITY, 'Dove Island',
                                          'dropped from the pool, 2037']}
    U['bowls_renamed'] = dict(RENAMED)

    if write:
        shutil.copy(PATH, PATH + '.pre_bowl_rename')
        pickle.dump(U, open(PATH, 'wb'))
    return U, old, seen_drop


if __name__ == '__main__':
    U, old, dropped_here = main()
    print("was (%d): %s" % (len(old), ", ".join("%s @ %s" % (k, v[0]) for k, v in old.items())))
    print("\nthe pool, in rotation order (%d):" % len(U['bowls']))
    for i, n in enumerate(U['bowl_roll'], 1):
        city, state = U['bowls'][n]
        print("  %d. %-14s %s, %s" % (i, n, city, state))
    print("\nrenamed:", ", ".join("%s -> %s" % kv for kv in U['bowls_renamed'].items()))
    print("defunct:", ", ".join("%s (%s, %s) -- %s" % (k, v[0], v[1], v[2])
                                for k, v in U['bowls_defunct'].items()))
    print("Burke Bay removed by this run:" , dropped_here)
