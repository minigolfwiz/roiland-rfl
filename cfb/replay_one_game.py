"""Surgically replay a single stored game on the current engine.

Dan's ruling, 2035 R2: the rest of Round 2 stays canon; only the Verigon-Coachville
overtime game is replayed, because its fourth-down decision came from logic that
could not tie the game.

Determinism note: the fix in special_teams.fourth_down_decision consumes no
randomness on either branch, so replaying on the SAME seed reproduces the game
play-for-play up to that fourth down and diverges only from that snap forward --
which is exactly "replay that fourth down and play it out".

Reversal covers records, points, season stats, and injuries. Player REPUTATION is
an exponentially-weighted average with no stored history, so the voided game
leaves a small residue there; that is disclosed rather than silently patched.
"""
import sys, pickle, copy
sys.path.insert(0, '/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db, load_reg, save_db, save_reg


def reverse_game(s, box):
    h, a = box['home'], box['away']
    hs, as_ = box['home_score'], box['away_score']
    wt, lt = (h, a) if hs > as_ else (a, h)
    s['record'][wt]['W'] -= 1
    s['record'][lt]['L'] -= 1
    s['record'][h]['PF'] -= hs; s['record'][h]['PA'] -= as_
    s['record'][a]['PF'] -= as_; s['record'][a]['PA'] -= hs
    # season stats
    agg = s['season_stats']
    for pid, st in box['stats'].items():
        if pid not in agg:
            continue
        d = agg[pid]
        for k, v in st.items():
            if isinstance(v, (int, float)):
                d[k] = d.get(k, 0) - v
    # injuries caused by this game
    gone = {inj['pid'] for inj in box['injuries']}
    for pid in gone:
        s['inj_out'].pop(pid, None)
    s['inj_log'] = [x for x in s['inj_log'] if x.get('pid') not in gone]
    for inj in box['injuries']:
        for pl in E.ROSTERS.get(inj['team'], []):
            if pl['pid'] == inj['pid'] and pl.get('inj_hist'):
                pl['inj_hist'] = [x for x in pl['inj_hist']
                                  if not (isinstance(x, dict) and x.get('desc') == inj['desc']
                                          and x.get('week') == box.get('week'))]
    return wt, lt


def main(gid):
    SUB.register(E)
    s = SE.load_state()
    db, reg = load_db(), load_reg()
    old = db[gid]
    seed = old['seed']
    h, a = old['home'], old['away']
    print('REPLAYING %s' % gid)
    print('  voided result: %s %d - %d %s (%sOT), seed %s' % (
        a, old['away_score'], old['home_score'], h, old['ot'], seed))

    old_reg_plays = [p for p in old['scoring_plays'] if (p.get('q') or 0) <= 4]
    ow, ol = reverse_game(s, old)
    del db[gid]

    unavailable = frozenset(pid for pid, w in s['inj_out'].items() if w > 0)
    recent = frozenset(s['inj_recent'].keys())
    import zlib, json as _json
    box, pbp = E.simulate_game(h, a, seed, site='home', keep_pbp=True, postseason=True,
                               unavailable_home=unavailable, unavailable_away=unavailable,
                               recently_returned_home=recent, recently_returned_away=recent,
                               hfa_override=old.get('hfa_used'))
    box['pbp_z'] = zlib.compress(_json.dumps(pbp).encode(), 6)
    box['game_id'] = gid; box['week'] = old.get('week', 16)
    box['venue'] = old.get('venue'); box['hfa_used'] = old.get('hfa_used')
    box['pregame_home_wp'] = old.get('pregame_home_wp')
    box['replayed'] = 'OT fourth-down logic fixed; replayed on the original seed'
    db[gid] = box

    # re-apply
    hw = box['home_score'] > box['away_score']
    wt, lt = (h, a) if hw else (a, h)
    s['record'][wt]['W'] += 1; s['record'][lt]['L'] += 1
    s['record'][h]['PF'] += box['home_score']; s['record'][h]['PA'] += box['away_score']
    s['record'][a]['PF'] += box['away_score']; s['record'][a]['PA'] += box['home_score']
    for inj in box['injuries']:
        s['inj_out'][inj['pid']] = inj['weeks_out'] if inj['weeks_out'] < 99 else 99
        s['inj_log'].append(dict(inj, week=box['week']))
        for pl in E.ROSTERS[inj['team']]:
            if pl['pid'] == inj['pid']:
                pl['inj_hist'].append({'season': s.get('season', 1), 'week': box['week'],
                                       'desc': inj['desc'], 'weeks': inj['weeks_out']})
    SE.merge_stats(s['season_stats'], box)
    E.update_reputation(box)

    # ---- verification: regulation must be identical ----
    new_reg_plays = [p for p in box['scoring_plays'] if (p.get('q') or 0) <= 4]
    same = (len(old_reg_plays) == len(new_reg_plays) and
            all(o.get('desc') == n.get('desc') and o.get('team') == n.get('team')
                and o.get('clock') == n.get('clock')
                for o, n in zip(old_reg_plays, new_reg_plays)))
    print('  regulation identical through Q4: %s (%d scoring plays)' % (same, len(new_reg_plays)))
    print()
    print('  NEW RESULT: %s %d - %d %s%s' % (a, box['away_score'], box['home_score'], h,
                                             ' (%sOT)' % box['ot'] if box['ot'] else ''))
    print('  winner changed: %s' % ('YES  %s -> %s' % (ow, wt) if ow != wt else 'no (%s again)' % wt))
    print()
    print('  OVERTIME PLAYS:')
    for p in box['scoring_plays']:
        if (p.get('q') or 0) > 4:
            print('     %-12s %-44s -> %s' % (p.get('team'), p.get('desc'), p.get('score')))

    save_db(db); save_reg(reg); SE.save_state(s); E.persist_rosters()
    return box, ow, wt


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'S10PO_R2_Verigon_Coachville')
