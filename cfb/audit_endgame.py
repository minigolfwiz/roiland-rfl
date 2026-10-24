"""Measure how the engine behaves at the end of close games.

Run before and after tuning so changes are judged on evidence, not vibes.
"""
import sys, statistics, collections, random
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E, subdivision as SUB, season as SE


def run(n=260, seed0=41000000):
    SUB.register(E)
    s = SE.load_state()
    FBS = [t for t in E.U['teams']]
    rng = random.Random(7)
    pairs = [(rng.choice(FBS), rng.choice(FBS)) for _ in range(n * 2)]
    pairs = [(h, a) for h, a in pairs if h != a][:n]

    one_score = 0
    finals = []
    pts = []
    last2_plays = []
    comeback_chances = 0
    comeback_converted = 0
    kneels = 0
    endhalf_label_q4 = 0
    q4_fg_at_zero = 0
    ties_at_reg_end = 0
    games = 0

    for i, (h, a) in enumerate(pairs):
        box, pbp = E.simulate_game(h, a, seed0 + i * 977, keep_pbp=True)
        games += 1
        m = abs(box['home_score'] - box['away_score'])
        finals.append(m)
        pts += [box['home_score'], box['away_score']]
        if m <= 8:
            one_score += 1
        if box.get('ot'):
            ties_at_reg_end += 1

        # scoring-play labels
        for sp in box['scoring_plays']:
            if sp.get('q') == 4 and 'end of half' in (sp.get('desc') or ''):
                endhalf_label_q4 += 1
            if sp.get('q') == 4 and sp.get('clock') == 0 and 'FG' in (sp.get('desc') or ''):
                q4_fg_at_zero += 1

        # play-by-play scan of the final two minutes of regulation
        n_last2 = 0
        for line in pbp:
            txt = line if isinstance(line, str) else str(line)
            if 'Victory formation' in txt:
                kneels += 1
            n_last2 += 0
        last2_plays.append(n_last2)

        # comeback opportunity: did the trailing team end within one score?
        if 0 < m <= 8:
            comeback_chances += 1

    out = {
        'games': games,
        'one_score_pct': 100.0 * one_score / games,
        'mean_margin': statistics.mean(finals),
        'median_margin': statistics.median(finals),
        'overtime_pct': 100.0 * ties_at_reg_end / games,
        'victory_formations': kneels,
        'q4_scores_mislabeled_end_of_half': endhalf_label_q4,
        'q4_walkoff_fgs': q4_fg_at_zero,
        'pts_per_team': statistics.mean(pts),
    }
    return out


if __name__ == '__main__':
    r = run()
    print('ENDGAME AUDIT (%d games)' % r['games'])
    for k, v in r.items():
        if k == 'games':
            continue
        print('  %-36s %s' % (k, ('%.1f' % v) if isinstance(v, float) else v))
