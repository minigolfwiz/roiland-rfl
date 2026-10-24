"""Export the college draft pool for the RFL conversation (the pro league runs the draft).
Uses draft.run_draft's declaration logic (seniors auto, juniors on stock, no Fr/So, a
subdivision sprinkle); the sim's picks are discarded. Writes state/draft_pool_<year>.json
in the 2041 format and the Project doc claude/cfb_draft_pool_<year>.json is written by hand."""
import sys, json, pickle
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, draft as D
s0 = SE.load_state(); N = s0['season']; year = 2025 + N + 1
s, picks, pool = D.run_draft()
U = E.U; stats = s['season_stats']
KEYS = ('PassYds','PassTD','INT','RushYds','RushTD','RecYds','RecTD','Tackles','Sacks','INT_def','FF','PD')
P = {p['pid']: p for t in E.ROSTERS for p in E.ROSTERS[t]}
out = []
for e in sorted(pool, key=lambda e: -e['stock']):
    sub = bool(e.get('subdivision'))
    pl = None if sub else P.get(e['pid'])
    st = {} if sub else stats.get(e['pid'], {})
    conf = None if sub else U['team_conf'].get(e['team'])
    out.append({'pid': e['pid'], 'name': e['name'], 'pos': e['pos'], 'cls': e['cls'], 'college': e['team'],
                'conference': conf if conf else ('Subdivision' if sub else None),
                'tier': (U['tiers'][conf] if conf else ('SUB' if sub else None)),
                'state': (U['geo'].get(e['team'], {}).get('state') if not sub else None),
                'early_entrant': bool(e.get('early')), 'subdivision': sub,
                'abil': round(e['abil'], 2), 'pot': (round(pl.get('pot', 0), 2) if pl else None),
                'dur': (round(pl.get('dur', 0), 2) if pl else None), 'arch': (pl.get('arch') if pl else None),
                'attrs': ({k: round(v, 2) for k, v in (pl.get('attrs') or {}).items()} if pl else None),
                'age': (pl.get('age') if pl else None), 'prod': round(e['prod'], 1),
                'college_draft_grade': round(e['base'], 3), 'college_scout_stock': round(e['stock'], 3),
                'final_season_stats': {k: st[k] for k in KEYS if st.get(k)}})
doc = {'what': 'Roiland CFB %d draft pool -- every player declared for the draft held after the %d season (college sim season %d).' % (year, year - 1, N),
       'rules': '280 picks, 7 rounds x 40. Eligibility: seniors (Sr/RS5) are automatically in; juniors (Jr/RS4) declared on their own stock; no true freshmen or sophomores. Subdivision (guest-school) prospects are included and marked.',
       'how_to_return': 'Send back picks as JSON: {"season":%d,"picks":[{"overall":1,"round":1,"pick":1,"rfl_team":"...","pid":<pid>}, ...]} (280 entries). Undrafted declared underclassmen mostly return to school; undrafted seniors leave.' % N,
       'ordering': "Sorted by the college sim's own scouting stock (its placeholder board). The RFL should grade on its own terms; abil/pot/dur/arch/attrs are the sim's internal 1-10 ratings.",
       'n_declared': len(out), 'n_seniors': sum(1 for e in out if not e['early_entrant'] and not e['subdivision']),
       'n_early': sum(1 for e in out if e['early_entrant']), 'n_subdivision': sum(1 for e in out if e['subdivision']),
       'pool': out}
path = '/home/claude/cfb2/state/draft_pool_%d.json' % year
json.dump(doc, open(path, 'w'))
print(path, {k: doc[k] for k in ('n_declared', 'n_seniors', 'n_early', 'n_subdivision')})
