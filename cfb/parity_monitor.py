"""Standing parity check (Dan, 2042 audit). Run at weeks 8 and 14 and after the season:
    python3 parity_monitor.py            # current season, through the last played week
    python3 parity_monitor.py 16         # a finished season
Reports the numbers the 2042 audit used: elite records (undefeated, <=2-loss teams, top-5 mean
losses, top-10 win %), favourite win rate by rating gap, and how often a ranked team lost to an
unranked FBS team against what the ratings expected. Read-only."""
import sys, re, math, collections, statistics
sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db
SUB.register(E); U=E.U
s=SE.load_state(); db=load_db()
n=int(sys.argv[1]) if len(sys.argv)>1 else s['season']
TEAMS=set(U['teams']); POWER={t for t in TEAMS if U['tiers'][U['team_conf'][t]]=='P6'}
games=[(int(m.group(1)),b) for gid,b in db.items() for m in [re.match(r'S%dW(\d+)_'%n,gid)] if m]
last=max(w for w,_ in games)
def arch(key):
    return (s.get(key) if n==s['season'] else (s['season_archive'].get(str(n)) or {}).get(key)) or {}
def board(w):
    ch={int(k):v for k,v in arch('committee_history').items()}; mh={(k if k=='pre' else int(k)):v for k,v in arch('media_history').items()}
    lst=ch.get(w-1) if (w-1) in ch else (mh.get('pre') if w==0 else mh.get(w-1))
    return [x[1] if isinstance(x,(list,tuple)) else x for x in (lst or [])][:25]
fbs=[(w,b) for w,b in games if b['home'] in TEAMS and b['away'] in TEAMS]
em={t:0.0 for t in TEAMS}
for _ in range(30):
    acc=collections.defaultdict(list)
    for w,b in fbs:
        m=b['home_score']-b['away_score']; acc[b['home']].append(m-2.5+em[b['away']]); acc[b['away']].append(-m+2.5+em[b['home']])
    em={t:(statistics.mean(acc[t]) if acc[t] else 0.0) for t in TEAMS}; mu=statistics.mean(em.values()); em={t:v-mu for t,v in em.items()}
rec=collections.defaultdict(lambda:[0,0])
for w,b in games:
    hw=b['home_score']>b['away_score']
    for t,win in ((b['home'],hw),(b['away'],not hw)):
        if t in TEAMS: rec[t][0 if win else 1]+=1
order=sorted(TEAMS,key=lambda t:-em[t]); top10=set(order[:10])
t10=[rec[t] for t in order[:10]]
print('PARITY MONITOR  %d  through week %d  (%d FBS games)'%(2025+n,last,len(fbs)))
print(' elite records: undefeated %d | <=2 losses %d (power %d) | top-5 mean losses %.2f | top-15 %.2f | top-10 win %% %.1f'%(
    sum(1 for t in rec if rec[t][1]==0), sum(1 for t in rec if rec[t][1]<=2), sum(1 for t in rec if t in POWER and rec[t][1]<=2),
    statistics.mean(rec[t][1] for t in order[:5]), statistics.mean(rec[t][1] for t in order[:15]),
    100*sum(r[0] for r in t10)/max(1,sum(sum(r) for r in t10))))
print('   reference 2038-42 (full season): undefeated 0-1 | <=2 losses 7-16 | top-5 mean losses 1.6-3.4 | top-10 win % 74-83')
bins=[(0,3),(3,7),(7,14),(14,21),(21,99)]; res=collections.defaultdict(lambda:[0,0]); tw=tn=0
for w,b in fbs:
    gap=(em[b['home']]+2.5)-em[b['away']]; fw=(b['home_score']>b['away_score'])==(gap>0)
    for i,(lo,hi) in enumerate(bins):
        if lo<=abs(gap)<hi: res[i][0]+=1; res[i][1]+=fw
print(' favourite win % by gap: '+' | '.join('%d-%s %.0f%% (n=%d)'%(lo,hi if hi<99 else '+',100*res[i][1]/max(1,res[i][0]),res[i][0]) for i,(lo,hi) in enumerate(bins)))
print('   reference 2038-42: 0-3 51-55 | 3-7 57-69 | 7-14 73-80 | 14-21 87-93 | 21+ 92-98')
xs=[(em[b['home']]+2.5-em[b['away']], b['home_score']>b['away_score']) for w,b in fbs]
k=0.0
for _ in range(300): k+=0.05*sum((y-1/(1+math.exp(-k*x)))*x for x,y in xs)/max(1,len(xs))
for lo,hi in ((1,7),(8,11),(12,14)):
    if last<lo: continue
    L=G=0; ex=0.0
    for w,b in fbs:
        if not lo<=w<=min(hi,last): continue
        rk=set(board(w))
        for t,o in ((b['home'],b['away']),(b['away'],b['home'])):
            if t in rk and o not in rk:
                th=t==b['home']; gap=(em[t]+(2.5 if th else 0))-(em[o]+(0 if th else 2.5))
                G+=1; ex+=1-1/(1+math.exp(-k*gap))
                ts=b['home_score'] if th else b['away_score']; os_=b['away_score'] if th else b['home_score']; L+=ts<os_
    if G: print(' weeks %d-%d: ranked lost %d of %d to unranked (%.0f%%) | ratings expected %.1f (%.0f%%)%s'%(lo,min(hi,last),L,G,100*L/G,ex,100*ex/G,'   <-- well above expectation' if L-ex>2*math.sqrt(max(ex*(1-ex/G),0.1)) else ''))
print('   reference 2040-42, weeks 12-14: 33%, 33%, 50% (ratings expected 26-33%)')
