"""Post-season parity audit (Dan, 2042). Read-only. Compares seasons 13-17 (2038-2042).
Regular season = gids S{n}W..; conference finals and playoffs are separate."""
import sys, re, collections, statistics, json
sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db
SUB.register(E); U=E.U
s=SE.load_state(); db=load_db()
TEAMS=set(U['teams']); TIER={t:U['tiers'][U['team_conf'][t]] for t in TEAMS}
POWER={t for t in TEAMS if TIER[t]=='P6'}
SEAS=[13,14,15,16,17,18,19]
def arch(n,key):
    if n==s['season']: return s.get(key) or {}
    return (s['season_archive'].get(str(n)) or {}).get(key) or {}
def games(n):
    out=[]
    for gid,b in db.items():
        m=re.match(r'S%dW(\d+)_'%n,gid)
        if m: out.append((int(m.group(1)),b))
    return out
def board(n,w):
    """ranking going INTO week w: committee board after w-1 if it existed, else media poll"""
    ch={int(k):v for k,v in arch(n,'committee_history').items()}
    mh={(k if k=='pre' else int(k)):v for k,v in arch(n,'media_history').items()}
    prev=w-1
    lst=ch.get(prev) if prev in ch else (mh.get('pre') if w==0 else mh.get(prev))
    if not lst: return []
    lst=[x[1] if isinstance(x,(list,tuple)) else x for x in lst]
    return lst[:25]
def records(n):
    r=collections.defaultdict(lambda:[0,0])
    for w,b in games(n):
        h,a=b['home'],b['away']; hw=b['home_score']>b['away_score']
        for t,win in ((h,hw),(a,not hw)):
            if t in TEAMS: r[t][0 if win else 1]+=1
    return r
def power_ratings(n,iters=30):
    g=[(b['home'],b['away'],b['home_score']-b['away_score']) for w,b in games(n) if b['home'] in TEAMS and b['away'] in TEAMS]
    em={t:0.0 for t in TEAMS}; HFA=2.5
    for _ in range(iters):
        acc=collections.defaultdict(list)
        for h,a,m in g:
            acc[h].append(m-HFA+em[a]); acc[a].append(-m+HFA+em[h])
        em={t:(statistics.mean(acc[t]) if acc[t] else 0.0) for t in TEAMS}
        mu=statistics.mean(em.values()); em={t:v-mu for t,v in em.items()}
    return em,g
out={}
print("=== 1. TEAMS BY REGULAR-SEASON LOSSES (FBS, weeks 0-14) ===")
print("season | teams | <=1 L | 2 L | <=2 L (power) | <=2 L (non-power) | 0 L | unbeaten power")
for n in SEAS:
    r=records(n); ls={t:v[1] for t,v in r.items()}
    p=[t for t in r if t in POWER]; q=[t for t in r if t not in POWER]
    le2p=sum(1 for t in p if ls[t]<=2); le2q=sum(1 for t in q if ls[t]<=2)
    print("%d | %d | %d | %d | %d/%d | %d/%d | %d | %d"%(2025+n,len(r),sum(1 for t in r if ls[t]<=1),sum(1 for t in r if ls[t]==2),le2p,len(p),le2q,len(q),sum(1 for t in r if ls[t]==0),sum(1 for t in p if ls[t]==0)))
    out.setdefault('le2',{})[n]=(le2p,le2q)
print("\n  exactly-2-loss POWER teams by season:", {2025+n:sum(1 for t,v in records(n).items() if t in POWER and v[1]==2) for n in SEAS})
print("\n=== 2. LOSSES OF THE TOP 25 ===")
print("(a) preseason media top 25: regular-season losses  | (b) final regular-season board (after wk14), losses")
for n in SEAS:
    r=records(n); pre=board(n,0)
    fin=board(n,15)
    def dist(lst):
        c=collections.Counter(r[t][1] for t in lst if t in r); return dict(sorted(c.items())),round(statistics.mean(r[t][1] for t in lst if t in r),2) if lst else None
    print(2025+n,'pre:',dist(pre),'| final board:',dist(fin))
print("\n=== 3. RANKED TEAMS LOSING TO UNRANKED FBS TEAMS, BY WEEK BLOCK ===")
print("season | wks1-7: ranked losses to unranked / ranked games vs unranked | wks8-11 | wks12-14")
blocks=[(1,7),(8,11),(12,14)]
tot={}
for n in SEAS:
    row=[]; 
    for lo,hi in blocks:
        L=G=0
        for w,b in games(n):
            if not lo<=w<=hi: continue
            h,a=b['home'],b['away']
            if h not in TEAMS or a not in TEAMS: continue
            rk=set(board(n,w))
            for t,o in ((h,a),(a,h)):
                if t in rk and o not in rk:
                    G+=1
                    ts=b['home_score'] if t==h else b['away_score']; os_=b['away_score'] if t==h else b['home_score']
                    if ts<os_: L+=1
        row.append((L,G)); tot.setdefault(n,row)
    print(2025+n,'|',' | '.join('%d/%d (%.1f%%)'%(L,G,100*L/max(1,G)) for L,G in row))
print("\n=== 4. FAVOURITE WIN RATE BY RATING GAP (FBS v FBS, season-end power ratings, HFA removed) ===")
bins=[(0,3),(3,7),(7,14),(14,21),(21,99)]
print("season | "+" | ".join("gap %d-%s"%(a,b if b<99 else '+') for a,b in bins)+" | overall fav win%")
for n in SEAS:
    em,g=power_ratings(n); res=collections.defaultdict(lambda:[0,0]); tw=tn=0
    for h,a,m in g:
        gap=(em[h]+2.5)-em[a]
        fav_home=gap>0; fav_won=(m>0)==fav_home
        ag=abs(gap)
        for i,(lo,hi) in enumerate(bins):
            if lo<=ag<hi: res[i][0]+=1; res[i][1]+=fav_won
        tn+=1; tw+=fav_won
    print(2025+n,'|',' | '.join('%.0f%% (n=%d)'%(100*res[i][1]/max(1,res[i][0]),res[i][0]) for i in range(len(bins))),'| %.1f%%'%(100*tw/tn))
print("\n=== 5. SPREAD OF TEAM STRENGTH (std dev of season-end power rating) ===")
for n in SEAS:
    em,g=power_ratings(n); v=sorted(em.values())
    print(2025+n,'sd %.2f | top10 mean %.1f | bottom10 mean %.1f | range %.1f'%(statistics.pstdev(v),statistics.mean(v[-10:]),statistics.mean(v[:10]),v[-1]-v[0]))
print("\n=== 6. GUEST (SUBDIVISION) GAMES: FBS RECORD vs GUESTS ===")
for n in SEAS:
    W=L=0; marg=[]
    for w,b in games(n):
        h,a=b['home'],b['away']
        if (h in TEAMS)!=(a in TEAMS):
            f=h if h in TEAMS else a; fs=b['home_score'] if f==h else b['away_score']; gs=b['away_score'] if f==h else b['home_score']
            W+=fs>gs; L+=fs<gs; marg.append(fs-gs)
    print(2025+n,'FBS %d-%d vs guests | mean margin %+.1f'%(W,L,statistics.mean(marg) if marg else 0))
