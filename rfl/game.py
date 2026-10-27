"""Drive-by-drive game engine (rebuilt). Clock-aware: possessions end at 0:00, halftime and the final gun are hard stops,
two-minute hurry-up and clock-milking, timeouts, 4th-down and two-point decisions by score and time, onside kicks,
Hail Marys, kneel-downs, NFL overtime (both teams possess; regular season can tie after one 10-minute period).
Returns a result dict with score, plays (scoring + turnovers), per-player stats, injuries."""
import random, math
from rfl.engine import depth_chart, ovr, age, DEPTH
from rfl import discipline as DISC

Q_LEN = 900
PENALTIES = True  # forward-only from the 2043 offseason: in-game penalties, driven by player and coach discipline (separate random stream, switch off to reproduce the old engine)
TRAITS = True     # False = every club and player equally disciplined (used to prove the traits do not move league-wide totals)
COACH_OUT_DIP = 0.14   # unit-rating points lost while the head coach is suspended: about -1 point of margin and -4% win probability (measured over 1,500 paired games)
PEN_SCALE = 1.2   # global calibration knob (about 5.3 accepted flags and 40 penalty yards per team-game)
PEN_ADJ = dict(cmp=.0122, run=.095)   # tiny offsetting nudge so that flags (which cancel snaps) do not lower league scoring; applied only while PENALTIES is on
TACKLES = True  # forward-only from 2043 week 3: tackles and punts inside the 20 (separate random stream; results are unchanged)
def mmss(t): t = max(0, int(t)); return f"{t // 60}:{t % 60:02d}"
def clamp(x, a, b): return max(a, min(b, x))

class Side:
    def __init__(self, S, t, year, rnd):
        self.name = t; self.S = S; dc = depth_chart(S, t); self.dc = dc; self.rnd = rnd
        g = lambda pos, i: dc[pos][i] if len(dc[pos]) > i else None
        self.qb = g('QB', 0); self.rbs = [p for p in dc['RB'][:2] if p]; self.wrs = [p for p in dc['WR'][:3] if p]; self.te = g('TE', 0)
        self.ol = dc['OL'][:5]; self.dl = dc['DL'][:4]; self.lb = dc['LB'][:3]; self.cb = dc['CB'][:2]; self.s = dc['S'][:2]; self.k = g('K', 0); self.p = g('P', 0)
        a = lambda p, k, d=5.0: (p['attrs'].get(k, p['abil']) if p else d)
        m = lambda ps, k, d=5.0: (sum(a(p, k) for p in ps) / len(ps)) if ps else d
        # unit ratings 1-10
        self.pass_off = .45 * (.6 * a(self.qb, 'acc') + .4 * a(self.qb, 'arm')) + .3 * m(self.wrs, 'hands') * .5 + .3 * m(self.wrs, 'route') * .5 + .1 * a(self.te, 'route') + .15 * m(self.ol, 'pblk')
        self.deep = .5 * a(self.qb, 'arm') + .5 * m(self.wrs, 'spd')
        self.run_off = .45 * a(self.rbs[0] if self.rbs else None, 'run') + .15 * a(self.rbs[0] if self.rbs else None, 'spd') + .3 * m(self.ol, 'rblk') + .1 * a(self.te, 'blk', 5.5)
        self.qb_mob = a(self.qb, 'mob')
        self.pass_def = .35 * m(self.cb, 'cov') + .2 * m(self.s, 'cov') + .15 * m(self.lb, 'cov') + .3 * m(self.dl, 'rush')
        self.rush = .7 * m(self.dl, 'rush') + .3 * m(self.lb, 'rush')
        self.run_def = .5 * m(self.dl, 'rdef') + .35 * m(self.lb, 'tkl') + .15 * m(self.s, 'tkl')
        self.ball = .5 * m(self.cb, 'ball') + .5 * m(self.s, 'ball')
        self.coach = S['clubs'][t]['coach']; self.style = self.coach.get('style', 'balanced')
        if S['clubs'][t].get('coach_out'):      # head coach barred from the sideline by the League Office: a small dip in every unit
            for u in ('pass_off', 'deep', 'run_off', 'pass_def', 'rush', 'run_def'): setattr(self, u, getattr(self, u) - COACH_OUT_DIP)
        self.timeouts = 3; self.stats = {}; self.score = 0
        self.plays_run = 0
    def st(self, p, k, v=1):
        if not p: return
        d = self.stats.setdefault(p['pid'], {}); d[k] = d.get(k, 0) + v
    def receiver(self):
        pool = [(w, 1.0) for w in self.wrs] + ([(self.te, .55)] if self.te else []) + ([(self.rbs[0], .35)] if self.rbs else [])
        if not pool: return None
        ws = [max(.05, x[1] * (x[0]['attrs'].get('hands', 6) + x[0]['attrs'].get('route', 6)) / 12) for x in pool]
        return self.rnd.choices([x[0] for x in pool], ws)[0]
    def rb(self):
        if not self.rbs: return self.qb
        return self.rbs[0] if len(self.rbs) == 1 or self.rnd.random() < .72 else self.rbs[1]

class Game:
    def __init__(self, S, home, away, year, seed, playoff=False):
        self.rnd = random.Random(seed); self.S = S; self.year = year; self.playoff = playoff
        self.H = Side(S, home, year, self.rnd); self.A = Side(S, away, year, self.rnd)
        self.plays = []; self.injuries = []; self.q = 1; self.clock = Q_LEN; self.ot = False
        self.seed = seed; self.pens = []; self.N = DISC.norms(S) if TRAITS else None
    # ---------------------------------------------------------------- helpers
    def other(self, s): return self.A if s is self.H else self.H
    def log(self, kind, s, text, pts=None):
        self.plays.append(dict(side='H' if s is self.H else 'A', team=s.name, q=self.q if not self.ot else 'OT', t=mmss(self.clock), kind=kind, text=text, score=f"{self.H.score}-{self.A.score}"))
    def burn(self, secs):
        self.clock -= secs
    def injury_check(self, s, p, mult=1.0):
        if not p or p.get('inj'): return
        base = .0018 * (1.35 - p['dur']) * mult
        if self.rnd.random() < base:
            weeks = self.rnd.choices([1, 2, 3, 4, 6, 8, 12, 99], [30, 24, 16, 12, 8, 5, 3, 2])[0]
            if weeks >= 12: kind = self.rnd.choice(['torn ACL', 'broken leg', 'Achilles', 'torn pectoral', 'broken collarbone'])
            elif weeks >= 6: kind = self.rnd.choice(['knee', 'high ankle sprain', 'broken hand', 'shoulder', 'torn ACL', 'broken leg'])
            else: kind = self.rnd.choice(['hamstring', 'ankle sprain', 'knee', 'concussion', 'shoulder', 'groin', 'high ankle sprain', 'calf'])
            p['inj'] = dict(weeks=weeks, kind=kind); self.injuries.append(dict(team=s.name, pid=p['pid'], name=p['name'], pos=p['pos'], weeks=weeks, kind=kind))
            self.log('injury', s, f"{p['name']} ({p['pos']}) leaves with a {kind}" + (' — out for the season' if weeks >= 99 else f', {weeks} wk'))
            # pull from the lineup
            s.__init__(self.S, s.name, self.year, self.rnd) if False else self.replace(s, p)
    def replace(self, s, p):
        s._pc = None
        dc = depth_chart(self.S, s.name)
        g = lambda pos, i: dc[pos][i] if len(dc[pos]) > i else None
        if p['pos'] == 'QB': s.qb = g('QB', 0)
        elif p['pos'] == 'RB': s.rbs = [x for x in dc['RB'][:2]]
        elif p['pos'] == 'WR': s.wrs = dc['WR'][:3]
        elif p['pos'] == 'TE': s.te = g('TE', 0)
        elif p['pos'] == 'K': s.k = g('K', 0)
        elif p['pos'] == 'P': s.p = g('P', 0)
        elif p['pos'] == 'OL': s.ol = dc['OL'][:5]
        elif p['pos'] == 'DL': s.dl = dc['DL'][:4]
        elif p['pos'] == 'LB': s.lb = dc['LB'][:3]
        elif p['pos'] == 'CB': s.cb = dc['CB'][:2]
        elif p['pos'] == 'S': s.s = dc['S'][:2]
    # ---------------------------------------------------------------- kicking
    def fg(self, s, dist):
        k = s.k; acc = k['attrs'].get('accy', 5) if k else 4; leg = k['attrs'].get('leg', 5) if k else 4
        maxd = 44 + 1.9 * leg; p = clamp(.985 - .012 * max(0, dist - 25) * (1.9 - acc / 10) - .035 * max(0, dist - maxd + 6), .02, .99)
        if dist > 61: p = min(p, .08)
        good = self.rnd.random() < p; s.st(k, 'fga'); self.burn(5)
        if good: s.st(k, 'fg'); s.st(k, 'pts', 3); s.score += 3; self.log('fg', s, f"{k['name'] if k else 'emergency kicker'} {dist}-yd field goal GOOD", 3)
        else: self.log('fgmiss', s, f"{k['name'] if k else 'emergency kicker'} {dist}-yd field goal NO GOOD")
        return good
    def xp(self, s):
        k = s.k; acc = k['attrs'].get('accy', 5) if k else 4
        if self.rnd.random() < .91 + acc * .008: s.st(k, 'xp'); s.st(k, 'pts', 1); s.score += 1; return True
        self.log('xpmiss', s, 'extra point missed'); return False
    def two_point(self, s, d):
        p = .47 + .03 * (s.pass_off - d.pass_def)
        if self.rnd.random() < p: s.score += 2; self.log('2pt', s, 'two-point conversion GOOD'); return True
        self.log('2ptfail', s, 'two-point try fails'); return False
    def punt(self, s, spot):
        p = s.p; leg = p['attrs'].get('leg', 5) if p else 4; ctl = p['attrs'].get('ctl', 5) if p else 4
        dist = clamp(self.rnd.gauss(36 + leg * 1.1, 6), 20, 70); s.st(p, 'punts'); s.st(p, 'punt_yds', int(dist))
        new = 100 - (spot + dist)
        if new <= 0: new = 20 if ctl < 7 else (self.rnd.randint(3, 12) if self.rnd.random() < .5 else 20)
        else: new = max(1, int(new - self.rnd.gauss(4, 5)))
        if TACKLES and new < 20: s.st(p, 'in20')
        self.burn(6); return new
    def kickoff(self, s, onside=False):
        if onside:
            self.burn(4)
            if self.rnd.random() < .11: self.log('onside', s, 'ONSIDE KICK recovered by the kicking team!'); return s, 45
            return self.other(s), 58
        self.burn(5); return self.other(s), self.rnd.choices([25, 30, 20, 35, 40], [55, 20, 10, 10, 5])[0]
    # ---------------------------------------------------------------- decisions
    def deficit(self, s): return self.other(s).score - s.score
    def late(self): return (self.q == 4 or self.ot) and self.clock <= 300
    def go_for_it(self, s, dist, spot):
        """4th down: spot = yards from own goal (0-100). Returns 'go' | 'fg' | 'punt'."""
        fgd = 100 - spot + 17; need = self.deficit(s); left = self.clock + (Q_LEN if self.q == 3 else 0); q4 = self.q == 4 or self.ot
        if self.ot and self.ot_state.get('must_score') and fgd <= 60 and dist > 2: return 'fg' if need >= 0 else 'go'
        if q4 and need > 0 and left < 240:
            if need <= 3 and fgd <= 62 and (dist > 4 or left < 40): return 'fg'
            if need > 3 or fgd > 62: return 'go'
            return 'go' if dist <= 4 else 'fg'
        if q4 and need > 8 and left < 600: return 'go' if (fgd > 45 or need > 10) else 'fg'
        if fgd <= 58 and not (dist <= 1 and spot >= 93 and self.rnd.random() < .5): return 'fg'
        if spot >= 60 and dist <= 2: return 'go' if self.rnd.random() < .72 else ('fg' if fgd <= 62 else 'punt')
        if spot >= 50 and dist <= 1 and self.rnd.random() < .55: return 'go'
        if fgd <= 62 and dist > 2: return 'fg' if self.rnd.random() < .6 else 'punt'
        return 'punt'
    def try_two(self, s):
        d = self.deficit(s)  # after the touchdown
        if not (self.q == 4 or self.ot): return False
        if self.ot: return False
        return d in (2, 5, 10, 16, 13) or (d == -1 and self.clock < 300) or (d == 0 and self.clock < 120 and self.rnd.random() < .25)
    def hurry(self, s):
        need = self.deficit(s); return need > 0 and ((self.q == 4 and self.clock <= 240) or (self.q == 2 and self.clock <= 90)) or (self.q in (2, 4) and self.clock <= 45 and need >= 0)
    def milk(self, s): return self.q == 4 and self.deficit(s) < 0 and self.clock <= 300
    def _pbias(self, s, down, dist, goal):
        pass_bias = {'balanced': .58, 'pass-first': .66, 'run-first': .5, 'aggressive': .63, 'conservative': .53}[s.style]
        if down == 3 and dist >= 5: pass_bias = .88
        elif down >= 3 and dist <= 2: pass_bias = .38
        if self.hurry(s): pass_bias = .9
        if self.milk(s): pass_bias = .22
        if goal <= 3: pass_bias = .35
        return pass_bias
    # ---------------------------------------------------------------- a play
    def play(self, s, d, down, dist, spot):
        """Returns (yards, kind, ended_flag) where kind in run/pass/inc/sack/int/fum/td/scramble."""
        goal = 100 - spot
        pass_bias = self._pbias(s, down, dist, goal)
        is_pass = self.rnd.random() < pass_bias
        for side_ in (s, d):
            pool = side_.ol + side_.dl + side_.lb + side_.cb + side_.s + ([side_.qb] if side_ is s and side_.qb else [])
            if pool and self.rnd.random() < .006:
                p_ = self.rnd.choice(pool)
                if self.rnd.random() > p_['dur'] * .55: self.injury_check(side_, p_, 400)
        if is_pass:
            qb = s.qb; edge = s.pass_off - d.pass_def; prs = d.rush - (sum(p['attrs'].get('pblk', 5) for p in s.ol) / max(1, len(s.ol)))
            sack_p = clamp(.08 + .022 * prs - .01 * s.qb_mob / 5, .02, .16)
            if self.rnd.random() < sack_p:
                yds = -self.rnd.randint(4, 11); self.burn(self.rnd.randint(28, 40) if not self.hurry(s) else 12)
                dl = self.rnd.choice(d.dl + d.lb) if d.dl else None; d.st(dl, 'sacks'); s.st(qb, 'sacked')
                if self.rnd.random() < .09: d.st(dl, 'ff'); s.st(qb, 'fum'); self.log('turnover', s, f"{qb['name']} sacked by {dl['name'] if dl else 'the rush'} and FUMBLES, {d.name} recover"); return yds, 'fum', True
                return yds, 'sack', False
            deep = self.rnd.random() < (.2 if goal > 25 else .08) + (.25 if down >= 3 and dist > 8 else 0) + (.4 if self.hurry(s) and self.deficit(s) > 3 else 0)
            cmp_p = clamp(.69 + .024 * edge - (.24 if deep else 0) + (PEN_ADJ['cmp'] if PENALTIES else 0), .25, .88)
            scramble = qb and self.rnd.random() < .04 + .025 * (s.qb_mob - 5)
            if scramble:
                yds = int(clamp(self.rnd.gauss(2 + s.qb_mob * .9, 6), -4, goal)); s.st(qb, 'car'); s.st(qb, 'rush_yds', yds); self.burn(38 if not self.hurry(s) else 14)
                if yds >= goal: s.st(qb, 'rush_td'); return yds, 'td', True
                return yds, 'run', False
            s.st(qb, 'att'); rcv = s.receiver()
            if self.rnd.random() < cmp_p:
                mu = (26 if deep else 9.6) + .6 * edge; sd = 13 if deep else 6.5
                yds = int(clamp(self.rnd.gauss(mu, sd), -3, goal)); yds = max(yds, -3)
                s.st(qb, 'cmp'); s.st(qb, 'pass_yds', yds); s.st(rcv, 'rec'); s.st(rcv, 'rec_yds', yds)
                self.injury_check(s, rcv)
                oob = self.rnd.random() < (.35 if deep else .18)
                self.burn(6 if (oob or self.hurry(s) and self.rnd.random() < .5) else (self.rnd.randint(30, 40) if not self.hurry(s) else 14))
                if yds >= goal: s.st(qb, 'pass_td'); s.st(rcv, 'rec_td'); return yds, 'td', True
                if self.rnd.random() < .012: s.st(rcv, 'fum'); self.log('turnover', s, f"{rcv['name']} FUMBLES after the catch, {d.name} recover"); return yds, 'fum', True
                return yds, 'pass', False
            self.burn(6)
            int_p = clamp(.058 + .01 * (d.ball - 6.5) - .008 * (qb['attrs'].get('acc', 5) - 6.5) + (.03 if deep else 0), .008, .12)
            if self.rnd.random() < int_p:
                db = self.rnd.choice(d.cb + d.s + d.lb) if d.cb else None; s.st(qb, 'ints'); d.st(db, 'int_made')
                ret = int(clamp(self.rnd.gauss(8, 12), 0, spot + 20))
                self.log('turnover', s, f"{qb['name']} INTERCEPTED by {db['name'] if db else 'the defense'}" + (f", returned {ret} yds" if ret > 5 else ''))
                return -ret, 'int', True
            return 0, 'inc', False
        # run
        rb = s.rb(); edge = s.run_off - d.run_def
        mu = 3.05 + .5 * edge + (PEN_ADJ['run'] if PENALTIES else 0); yds = int(clamp(self.rnd.gauss(mu, 3.8) + (self.rnd.expovariate(.11) if self.rnd.random() < .07 else 0), -5, goal))
        s.st(rb, 'car'); s.st(rb, 'rush_yds', yds); self.injury_check(s, rb)
        self.burn(self.rnd.randint(32, 42) if not self.hurry(s) else 15)
        if yds >= goal: s.st(rb, 'rush_td'); return yds, 'td', True
        if self.rnd.random() < .011: s.st(rb, 'fum'); self.log('turnover', s, f"{rb['name']} FUMBLES, {d.name} recover"); return yds, 'fum', True
        return yds, 'run', False
    # ---------------------------------------------------------------- a drive
    def drive(self, s, spot):
        d = self.other(s); down, dist = 1, 10
        while True:
            if self.clock <= 0: return 'clock', spot
            # kneel-downs: leading, opponent cannot stop the clock
            if self.q == 4 and self.deficit(s) < 0 and self.clock <= 40 * (3 - min(3, down - 1)) + 2 and d.timeouts == 0 and self.clock <= 120 and not self.ot:
                self.burn(min(self.clock, 40)); down += 1
                if down > 4: return 'downs', spot
                continue
            if down == 4:
                choice = self.go_for_it(s, dist, spot)
                if choice == 'fg':
                    self.fg(s, 100 - spot + 17); return 'fg', spot
                if choice == 'punt': return 'punt', self.punt(s, spot)
            # Hail Mary / clock
            if (self.q in (2, 4) or self.ot) and self.clock <= 8 and self.deficit(s) > 0 and spot < 65:
                qb = s.qb; s.st(qb, 'att'); self.burn(self.clock)
                if self.rnd.random() < .06 + .01 * (s.deep - 6): rcv = s.receiver(); s.st(qb, 'cmp'); s.st(qb, 'pass_yds', 100 - spot); s.st(qb, 'pass_td'); s.st(rcv, 'rec'); s.st(rcv, 'rec_yds', 100 - spot); s.st(rcv, 'rec_td'); self._td[s.name] = f"HAIL MARY! {qb['name']} to {rcv['name']} for {100 - spot} yards as time expires"; return 'td', 100
                self.log('inc', s, f"{qb['name']}'s Hail Mary falls incomplete"); return 'clock', spot
            yds, kind, ended = self.play(s, d, down, dist, spot)
            if kind == 'pen':      # a flag nullified the snap: move the ball, replay the down (or award a first down) and go again
                spot = clamp(spot + yds, 1, 99)
                if yds >= 0 and (self._pen['af'] or yds >= dist): down, dist = 1, min(10, 100 - spot)
                else: dist = max(1, min(dist - yds, 100 - spot))
                continue
            s.plays_run += 1
            if kind == 'td': return 'td', 100
            if kind in ('int', 'fum'):
                return kind, spot + (yds if kind == 'int' else 0)
            spot += yds; spot = clamp(spot, 1, 99)
            # timeouts: trailing side stops the clock late
            if self.clock <= 180 and self.q in (2, 4) and s.timeouts > 0 and self.deficit(s) > 0 and kind in ('run', 'pass', 'sack') and self.rnd.random() < .8:
                s.timeouts -= 1
            # leading defense uses timeouts to save clock
            if self.clock <= 120 and self.q == 4 and d.timeouts > 0 and self.deficit(d) > 0 and kind in ('run', 'pass') and self.rnd.random() < .85:
                d.timeouts -= 1
            if self.clock <= 0: return 'clock', spot
            if yds >= dist: down, dist = 1, min(10, 100 - spot)
            else: down += 1; dist -= yds
            if down > 4: return 'downs', spot
            if spot >= 100: return 'td', 100
    # ---------------------------------------------------------------- game flow
    def run(self):
        self._last_scorer = {}
        coin = self.rnd.random() < .5; first_kick = self.H if coin else self.A
        self.q = 1; self.clock = Q_LEN
        self.quarter_loop(first_kick, 1, 2)
        self.H.timeouts = self.A.timeouts = 3
        self.quarter_loop(self.other(first_kick), 3, 4)
        if self.H.score == self.A.score: self.overtime()
        return self.result()
    def quarter_loop(self, kicking, q1, q2):
        self.q = q1; self.clock = Q_LEN
        s, spot = self.kickoff(kicking)
        while True:
            nxt = self.drive_wrap(s, spot)
            if nxt is None: return
            s, spot = nxt
    def drive_wrap(self, s, spot):
        """Runs drives, rolling quarter 1→2 / 3→4 by carrying the clock; returns next (side, spot) or None at the half's end."""
        while True:
            res, spot2 = self.drive(s, spot); d = self.other(s)
            if self.clock <= 0 and self.q in (1, 3):
                # quarter break: same possession continues
                self.q += 1; self.clock += Q_LEN
                if res == 'clock': spot = spot2; continue
            if res == 'td':
                s.score += 6; self.log('td', s, self.td_text(s), 6)
                if self.try_two(s): self.two_point(s, d)
                else: self.xp(s)
                if self.clock <= 0 and self.q in (2, 4): return None
                onside = self.q == 4 and self.deficit(s) > 0 and self.clock <= 150 and (self.deficit(s) > 3 or d.timeouts == 0 or self.clock <= 60)
                return self.kickoff(s, onside=onside)
            if res == 'fg':
                if self.clock <= 0 and self.q in (2, 4): return None
                return self.kickoff(s)
            if res == 'punt':
                if self.clock <= 0 and self.q in (2, 4): return None
                return d, spot2
            if res in ('int', 'fum', 'downs'):
                if self.clock <= 0 and self.q in (2, 4): return None
                return d, clamp(100 - spot2, 1, 99)
            if res == 'clock': return None
    def td_text(self, s):
        # the most recent td stat belongs to the last scorer; find who gained a td this drive by diffing is complex: use last-touch bookkeeping
        return self._td.get(s.name, f"{s.name} touchdown")
    # we hook st() to remember the last td scorer
    def result(self):
        return dict(home=self.H.name, away=self.A.name, home_pts=self.H.score, away_pts=self.A.score, ot=self.ot,
                    winner=None if self.H.score == self.A.score else (self.H.name if self.H.score > self.A.score else self.A.name),
                    plays=self.plays, stats={'H': self.H.stats, 'A': self.A.stats}, injuries=self.injuries, drives=getattr(self, 'drives', {'H': 0, 'A': 0}), pens=self.pens)
    def overtime(self):
        self.ot = True; self.ot_state = {}; self.q = 5; self.clock = 600 if not self.playoff else 900
        self.H.timeouts = self.A.timeouts = 2
        first = self.H if self.rnd.random() < .5 else self.A; second = self.other(first)
        self.log('ot', first, f"OVERTIME — {first.name} win the toss and receive")
        possessions = 0; s, spot = self.kickoff(second)
        while True:
            self.ot_state['must_score'] = possessions == 1 and self.deficit(s) > 0
            if possessions >= 2 and self.H.score != self.A.score: break
            res, spot2 = self.drive(s, spot); d = self.other(s)
            possessions += 1
            if res == 'td':
                s.score += 6; self.log('td', s, self.td_text(s), 6)
                diff = s.score - d.score; self.ot_poss = possessions
                if possessions >= 2 and diff > 0: self.plays[-1]['noxp'] = True   # walk-off TD: both teams have had the ball and this one leads, so the game ends on the touchdown — no extra point
                elif possessions >= 2 and diff == 0: self.two_point(s, d) if self.rnd.random() < .5 else self.xp(s)   # answering a TD that missed its XP: the try wins it
                else: self.xp(s)   # first possession (the opponent still gets the ball), or answering a TD+XP: the kick ties it
            if res == 'fg': pass
            if self.H.score != self.A.score and possessions >= 2: break
            if self.clock <= 0:
                if self.playoff: self.clock = 900; continue
                break
            if res in ('td', 'fg'): s, spot = self.kickoff(s)
            elif res == 'punt': s, spot = d, spot2
            elif res in ('int', 'fum', 'downs'): s, spot = d, clamp(100 - spot2, 1, 99)
            elif res == 'clock':
                if self.playoff: self.clock = 900; continue
                break
            if possessions >= 2 and self.H.score != self.A.score: break
        if self.H.score == self.A.score: self.log('tie', self.H, 'Game ends in a tie')

# ---- hook: remember who scored the touchdown so the log can name them
_orig_st = Side.st
def _st(self, p, k, v=1):
    _orig_st(self, p, k, v)
    if TACKLES and p and k == 'sacks': _orig_st(self, p, 'tkl', v)
    if p and k in ('rush_td', 'rec_td'):
        g = self.game if hasattr(self, 'game') else None
        if g is not None:
            if k == 'rec_td': g._td[self.name] = f"{self.qb['name']} {g._last_yds.get(self.name, '')}yd TD pass to {p['name']}".replace(' yd', 'yd')
            else: g._td[self.name] = f"{p['name']} {g._last_yds.get(self.name, '')}yd TD run"
Side.st = _st
_orig_play = Game.play
def _play(self, s, d, down, dist, spot):
    s.game = self; d.game = self
    if not hasattr(self, '_td'): self._td = {}; self._last_yds = {}
    goal = 100 - spot
    self._last_yds[s.name] = goal
    return _orig_play(self, s, d, down, dist, spot)
Game.play = _play
_play_base = Game.play
def _play_tkl(self, s, d, down, dist, spot):
    key = f"tkl|{s.name}|{d.name}|{self.q}|{self.clock}|{spot}|{down}|{dist}|{s.plays_run}"
    yds, kind, ended = _play_base(self, s, d, down, dist, spot)
    if TACKLES and kind in ('run', 'pass'):
        tr = random.Random(key)
        w = {'run': (.20, .45, .15, .20), 'pass': (.05, .30, .35, .30)}[kind]
        cat = tr.choices([d.dl, d.lb, d.cb, d.s], w)[0]
        if not cat: cat = [x for x in (d.lb, d.dl, d.cb, d.s) if x][0] if any((d.lb, d.dl, d.cb, d.s)) else None
        if cat:
            who = tr.choices(cat, [max(1, p_['attrs'].get('tkl', p_['abil'])) for p_ in cat])[0]
            d.st(who, 'tkl')
    return yds, kind, ended
Game.play = _play_tkl
_orig_drive = Game.drive
def _drive(self, s, spot):
    if not hasattr(self, '_td'): self._td = {}; self._last_yds = {}; self.drives = {'H': 0, 'A': 0}
    self.drives['H' if s is self.H else 'A'] += 1
    self._td[s.name] = f"{s.name} touchdown"
    return _orig_drive(self, s, spot)
Game.drive = _drive


# ---------------------------------------------------------------- penalties (Dan, 27 Oct 2026; forward-only)
# Flags are drawn before the snap from a separate random stream keyed on the game seed and the situation, so with PENALTIES off the old
# engine is reproduced exactly. A flag nullifies the snap (no play stats), moves the ball, and the down is replayed or a first is awarded.
# Rates are per scrimmage play for the side that can commit the foul; 'pass-only' fouls apply to pass plays. Who is flagged, and how often a
# whole team is flagged, come from the hidden discipline traits (rfl/discipline.py), normalised so the league-wide rate does not move.
#            key   label                    per-play  yds   presnap pass-only personal  position weights (share of that foul)
OFF_PEN = [('fs', 'false start',           .0155, 5,    True,  False, False, {'OL': .78, 'TE': .10, 'WR': .09, 'RB': .03}),
           ('oh', 'offensive holding',     .0130, 10,   False, False, False, {'OL': .82, 'TE': .10, 'RB': .05, 'WR': .03}),
           ('om', 'illegal formation',     .0065, 5,    True,  False, False, {'OL': .35, 'TE': .25, 'WR': .30, 'QB': .10}),
           ('opf', 'unnecessary roughness', .0020, 15,  False, False, True,  {'OL': .40, 'WR': .20, 'TE': .15, 'RB': .15, 'QB': .10})]
DEF_PEN = [('os', 'offside',               .0098, 5,    True,  False, False, {'DL': .72, 'LB': .28}),
           ('dh', 'defensive holding',     .0080, 5,    False, False, False, {'CB': .55, 'LB': .25, 'S': .20}),
           ('pi', 'pass interference',     .0105, None, False, True,  False, {'CB': .60, 'S': .20, 'LB': .20}),
           ('rp', 'roughing the passer',   .0040, 15,   False, True,  False, {'DL': .70, 'LB': .30}),
           ('dpf', 'unnecessary roughness', .0020, 15,  False, False, True,  {'DL': .30, 'LB': .30, 'S': .25, 'CB': .15})]
AUTO_FIRST = {'dh', 'pi', 'rp', 'dpf'}
PERSONAL_FOULS = ('unnecessary roughness', 'roughing the passer')   # the on-field fouls the League Office draws its conduct cases from

def _on_field(s, side):
    if side == 'o': return {'OL': list(s.ol), 'TE': [s.te] if s.te else [], 'WR': list(s.wrs), 'RB': s.rbs[:1], 'QB': [s.qb] if s.qb else []}
    return {'DL': list(s.dl), 'LB': list(s.lb), 'CB': list(s.cb), 'S': list(s.s)}

def _pen_profile(g, s, side):
    """Per foul type: (rate multiplier for the whole unit/team, [(player, weight)]). Cached on the Side until a lineup change."""
    pc = getattr(s, '_pc', None)
    if pc is None: pc = s._pc = {}
    if side in pc: return pc[side]
    N = g.N; cat = OFF_PEN if side == 'o' else DEF_PEN; unit = _on_field(s, side); out = {}
    cm = 1.0
    if N is not None and TRAITS: cm = math.exp(DISC.BETA_COACH * DISC.z_coach(N, s.coach)) / N['Mcoach']
    for key, label, rate, yds, pre, pass_only, personal, posw in cat:
        rows = []; tm_num = 0.0; tm_den = 0.0
        for pos, w in posw.items():
            ps = [p for p in unit.get(pos, []) if p]
            for p in ps:
                pw = w / len(ps)
                z = 0.0
                if N is not None and TRAITS: z = DISC.z_mix(N, p, .6) if personal else DISC.z_disc(N, p)
                rows.append((p, pw * math.exp(DISC.BETA_SEL * z)))
                tm_num += pw * math.exp(DISC.BETA_TEAM * z); tm_den += pw
        tm = (tm_num / tm_den / (N['Mteam'] if (N is not None and TRAITS) else 1.0)) if tm_den else 1.0
        out[key] = (rate * tm * cm * PEN_SCALE, rows)
    pc[side] = out; return out

def _pen_roll(g, s, d, down, dist, spot):
    """Returns None (no flag) or the dict describing the accepted flag. Offence = s, defence = d."""
    pr = random.Random(f"pen|{g.seed}|{g.q}|{g.clock}|{spot}|{down}|{dist}|{s.plays_run}|{len(g.pens)}")
    goal = 100 - spot
    is_pass = pr.random() < g._pbias(s, down, dist, goal); u = pr.random()
    cand = []
    for side, team, cat in (('o', s, OFF_PEN), ('d', d, DEF_PEN)):
        prof = _pen_profile(g, team, side)
        for key, label, rate, yds, pre, pass_only, personal, posw in cat:
            r = prof[key][0]
            if pass_only and not is_pass: continue
            if key == 'pi' and not is_pass: continue
            cand.append((r, key, label, yds, pre, personal, team, side, prof[key][1]))
    tot = sum(c[0] for c in cand)
    if u >= tot: return None
    acc = 0.0
    for c in cand:
        acc += c[0]
        if u < acc: break
    r, key, label, yds, pre, personal, team, side, rows = c
    if not rows: return None
    p = pr.choices([x[0] for x in rows], [x[1] for x in rows])[0]
    if key == 'om': label = 'delay of game' if p['pos'] == 'QB' else ('illegal formation' if p['pos'] in ('OL', 'TE') else 'illegal shift')
    elif key == 'os' and p['pos'] == 'DL' and pr.random() < .5: label = 'neutral zone infraction'
    elif key == 'dh' and p['pos'] == 'CB' and pr.random() < .3: label = 'illegal contact'
    if side == 'o': y = -min(yds, max(1, spot // 2))
    elif key == 'pi': y = max(1, min(int(max(2, min(48, pr.expovariate(1 / 13) + 2))), goal - 1))
    else: y = max(1, min(yds, max(1, goal // 2)))
    return dict(key=key, label=label, team=team, player=p, yds=y, af=(side == 'd' and key in AUTO_FIRST), pre=pre, burn=(pr.randint(2, 6) if pre else pr.randint(8, 22)))

_play_nopen = Game.play
def _play_pen(self, s, d, down, dist, spot):
    if PENALTIES and self.clock > 0:
        info = _pen_roll(self, s, d, down, dist, spot)
        if info:
            p = info['player']; t = info['team']; self._pen = info; t_snap = mmss(self.clock); self.burn(info['burn'])
            t.st(p, 'pen'); t.st(p, 'pen_yds', abs(info['yds']))
            self.pens.append(dict(side='H' if t is self.H else 'A', team=t.name, q=self.q if not self.ot else 'OT', t=t_snap, type=info['label'], pid=p['pid'], name=p['name'], pos=p['pos'], yds=abs(info['yds']),
                                  down=down, to_go=dist, af=info['af'], against='off' if info['yds'] < 0 else 'def'))
            return info['yds'], 'pen', False
    return _play_nopen(self, s, d, down, dist, spot)
Game.play = _play_pen

def play_game(S, home, away, year, seed, playoff=False):
    g = Game(S, home, away, year, seed, playoff); return g.run()
