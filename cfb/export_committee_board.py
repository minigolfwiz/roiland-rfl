"""Export the selection-committee board for Dan's committee room -- the playoff builder.

Season-agnostic: everything keys off `state['season']`, so this runs for whatever season
has just finished. It was written for 2035 with the season number hardcoded in four
places (the CCG prefix, the game-log prefix, and the payload's season/year); all four now
derive from state. The output also moved into `state/` so `build_pages.py` can pick it up
like every other page.

Produces one JSON payload with:
  * the candidate board (top ~50 by rating, plus EVERY conference champion, since
    champions auto-qualify and must appear however they rank)
  * each candidate's full resume: record, conference record, points, ratings, and a
    game-by-game log with the opponent's strength and record at season's end
  * a strength lookup for all 152 FBS teams so any opponent can be judged
"""
import json, sys, collections
sys.path.insert(0, '/home/claude/cfb2')
import season as SE
import resume_marks as RM, committee as CM, pbp_engine as E, subdivision as SUB
from games_db import load_db

BOARD_SIZE = 50


def main():
    SUB.register(E)
    s = SE.load_state()
    db = load_db()
    U = E.U
    seas = s.get('season', 12)
    CCG_PRE = 'S%dCCG' % seas
    SEAS_PRE = 'S%dW' % seas
    FBS = set(U['teams'])
    net = SE.net_ratings(s, db)
    rec = s['record']

    # ---- conference champions (auto-qualifiers) ----
    champs = {}
    for gid, b in db.items():
        if not str(gid).startswith(CCG_PRE):
            continue
        w = b['home'] if b['home_score'] > b['away_score'] else b['away']
        champs[w] = str(gid).replace(CCG_PRE + '_', '')

    champs_by_conf = {c: t for t, c in champs.items()}

    # ---- the engine's own field and seeding, for "seed from the computer" ----
    try:
        order, _seeds, _r, _sc = CM.select_playoff_field(s, db, champs_by_conf)
        engine_field = list(order)
    except Exception as ex:
        print('[engine_field] unavailable:', ex)
        engine_field = []

    # ---- the engine's own board, offered as a reference ordering only ----
    try:
        cr = CM.committee_rank(s, db)
        cr = cr[0] if isinstance(cr, tuple) else cr
        engine_board = [x[1] if isinstance(x, (list, tuple)) else x for x in cr]
    except Exception:
        engine_board = []
    engine_rank = {t: i + 1 for i, t in enumerate(engine_board)}
    media_rank = {t: r for r, t in (s.get('media_poll_current') or [])}
    poll_rank = RM.current_rank(s)
    # Dan's ballot of record (the last committee board he installed) -- the board opens in
    # THIS order, his 25 first, then everyone else by rating (Dan, 2039)
    ballot_rank = {t: r for r, t in (s.get('committee_poll_current') or [])} if s.get('committee_official') else {}

    # ---- strength lookup for every FBS team ----
    strength = {}
    rating_order = sorted(FBS, key=lambda t: -net['net'][t])
    rating_rank = {t: i + 1 for i, t in enumerate(rating_order)}
    for t in FBS:
        r = rec[t]
        strength[t] = {
            'rec': '%d-%d' % (r['W'], r['L']),
            'net': round(net['net'][t], 1),
            'em': round(net['em'][t], 1),
            'rank': rating_rank[t],
            'conf': U['team_conf'][t],
            'tier': U['tiers'][U['team_conf'][t]],
        }

    # ---- candidates: top N by rating, union all champions, union the engine's field ----
    # The board ranks by NET RATING; the engine seeds the field by `committee_rank`, a
    # different measure. An at-large can therefore make the engine's 24 and still sit
    # outside the top 50 by rating -- in 2037 that was Stanton State, which the board
    # left out entirely, so "seed from the computer" could only place 23 teams.
    cand = [t for t in rating_order[:BOARD_SIZE]]
    for c in list(champs) + list(engine_field) + list(ballot_rank):
        if c not in cand:
            cand.append(c)

    # ---- game logs ----
    logs = collections.defaultdict(list)
    for gid, b in db.items():
        gid = str(gid)
        if not (gid.startswith(SEAS_PRE) or gid.startswith(CCG_PRE)):
            continue
        for t, opp in ((b['home'], b['away']), (b['away'], b['home'])):
            if t not in cand:
                continue
            us = b['home_score'] if b['home'] == t else b['away_score']
            them = b['away_score'] if b['home'] == t else b['home_score']
            wk = 15 if gid.startswith(CCG_PRE) else int(gid[len(SEAS_PRE):len(SEAS_PRE) + 2])
            logs[t].append({
                'wk': wk,
                'opp': opp,
                # P6 title games are at named neutral bowls -- neither team is at home
                'ha': ('vs' if b['home'] == t else 'at')
                      if '(campus)' in str(b.get('venue', '')) or 'CCG' not in gid else 'vs',
                'ccg': 'CCG' in gid,
                'won': us > them,
                'score': '%d-%d' % (us, them),
                'pf': us, 'pa': them,
                'ot': b.get('ot', 0),
                'sub': opp not in FBS,
                'opp_rec': strength.get(opp, {}).get('rec', '-'),
                'opp_net': strength.get(opp, {}).get('net'),
                'opp_rank': strength.get(opp, {}).get('rank'),
                'opp_poll': poll_rank.get(opp),
                'mark': RM.mark(us > them, opp, poll_rank, strength.get(opp, {}).get('rank')),
                'opp_conf': strength.get(opp, {}).get('conf', 'Subdivision'),
            })
    for t in logs:
        logs[t].sort(key=lambda g: g['wk'])

    teams = []
    for t in cand:
        r = rec[t]
        gl = logs[t]
        wins = [g for g in gl if g['won'] and not g['sub']]
        losses = [g for g in gl if not g['won']]
        q = sum(1 for g in wins if g['mark'] == 'qw')
        bad = sum(1 for g in losses if g['mark'] == 'bl')
        teams.append({
            'team': t,
            'mascot': U['geo'][t]['mascot'],
            'conf': U['team_conf'][t],
            'tier': U['tiers'][U['team_conf'][t]],
            'state': U['geo'][t]['state'],
            'rec': '%d-%d' % (r['W'], r['L']),
            'w': r['W'], 'l': r['L'],
            'conf_rec': '%d-%d' % (r['confW'], r['confL']),
            'pf': r['PF'], 'pa': r['PA'],
            'net': round(net['net'][t], 1),
            'em': round(net['em'][t], 1),
            'sos': round(net['sos'][t], 1),
            'rating_rank': rating_rank[t],
            'engine_rank': engine_rank.get(t),
            'media_rank': media_rank.get(t),
            'ballot_rank': ballot_rank.get(t),
            'champ': champs.get(t),
            'colors': U['team_colors'].get(t, ['#444', '#999']),
            'q_wins': q,
            'bad_losses': bad,
            'games': gl,
        })
    teams.sort(key=lambda x: (x['ballot_rank'] or 999, x['rating_rank']))

    payload = {
        'season': seas, 'year': 2025 + seas,
        'field_size': 24, 'byes': 8,
        'champions': champs,
        'teams': teams,
        'strength': strength,
        # the engine's own 24, in its own seed order -- what "seed from the computer"
        # fills in, and the thing Dan is overriding
        'engine_field': engine_field,
    }
    out = '/home/claude/cfb2/state/committee_board.json'
    json.dump(payload, open(out, 'w'))
    print('board exported: %d candidates (%d conference champions)' % (len(teams), len(champs)))
    print('champions:', ', '.join('%s (%s)' % (t, c) for t, c in sorted(champs.items())))
    print('unranked-by-rating champions forced onto the board:',
          [t for t in champs if rating_rank[t] > BOARD_SIZE] or 'none')
    print('payload size: %.0f KB' % (len(json.dumps(payload)) / 1024))


if __name__ == '__main__':
    main()
