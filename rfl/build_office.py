"""Rebuild the Schedule Office page for a year: python3 rfl/build_office.py 2043 -> out/rfl_office_<year>.html
Template = out/office_template.html (the published Schedule Office page; DATA.year drives the db doc 'rfl/schedule<year>')."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfl.engine import ROOT, load
yr = int(sys.argv[1]); h = open(f'{ROOT}/out/office_template.html', encoding='utf-8').read(); L = load(f'{ROOT}/data/league.json'); G = load(f'{ROOT}/data/matchups_{yr}.json')
i = h.index('const DATA = ') + len('const DATA = '); D, j = json.JSONDecoder().raw_decode(h, i)
old = D['year']; D['year'] = yr; D['games'] = [dict(id=g['id'], host=g['host'], visitor=g['visitor'], kind=g['kind']) for g in G]
h2 = h[:i] + json.dumps(D, separators=(',', ':')) + h[j:].replace(str(old), str(yr))
open(f'{ROOT}/out/rfl_office_{yr}.html', 'w', encoding='utf-8').write(h2); print('ok', old, '->', yr)
