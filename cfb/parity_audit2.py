import sys; sys.path.insert(0,'/home/claude/cfb2')
exec(open('/home/claude/cfb2/parity_audit.py').read().split('out={}')[0])
import math
def fitcurve(n):
    em,g=power_ratings(n); return em
print("=== A. RANKED v UNRANKED, WEEKS 12-14: what the ratings said vs what happened ===")
for n in [15,16,17]:
    em,_=power_ratings(n)
    # logistic fit of home-win on gap over the season (all FBS games) -> expected win prob
    xs=[];ys=[]
    for w,b in games(n):
        h,a=b['home'],b['away']
        if h in TEAMS and a in TEAMS: xs.append((em[h]+2.5)-em[a]); ys.append(1 if b['home_score']>b['away_score'] else 0)
    k=0.0; 
    for _ in range(200):  # one-parameter logistic by gradient on k
        gsum=sum((y-1/(1+math.exp(-k*x)))*x for x,y in zip(xs,ys)); k+=0.0005*gsum/len(xs)*100
    L=exp=G=0; road=roadL=0; rk_gaps=[]; rkrank=[]
    for w,b in games(n):
        if not 12<=w<=14: continue
        h,a=b['home'],b['away']
        if h not in TEAMS or a not in TEAMS: continue
        rk=set(board(n,w))
        for t,o in ((h,a),(a,h)):
            if t in rk and o not in rk:
                G+=1; th=(t==h)
                gap=(em[t]+(2.5 if th else 0))-(em[o]+(0 if th else 2.5))
                p=1/(1+math.exp(-k*gap)); exp+=1-p
                ts=b['home_score'] if th else b['away_score']; os_=b['away_score'] if th else b['home_score']
                lost=ts<os_; L+=lost
                if not th: road+=1; roadL+=lost
                rk_gaps.append(gap)
    order={t:i+1 for i,t in enumerate(sorted(em,key=lambda t:-em[t]))}
    ranked_pr=[order[t] for t in board(n,12)]
    print(2025+n,'ranked lost %d of %d (%.0f%%) | model expected %.1f (%.0f%%) | road games %d, lost %d | mean rating gap in favour of ranked side %+.1f | avg true rating-rank of the wk12 board %.0f'%(L,G,100*L/G,exp,100*exp/G,road,roadL,statistics.mean(rk_gaps),statistics.mean(ranked_pr)))
print("\n=== B. 2042 weeks 12-14: every ranked loss to an unranked team ===")
em,_=power_ratings(17); order={t:i+1 for i,t in enumerate(sorted(em,key=lambda t:-em[t]))}
bd={w:board(17,w) for w in range(0,15)}
for w,b in sorted(games(17),key=lambda x:x[0]):
    if not 12<=w<=14: continue
    h,a=b['home'],b['away']
    if h not in TEAMS or a not in TEAMS: continue
    rk=bd[w]
    for t,o in ((h,a),(a,h)):
        if t in rk and o not in rk:
            ts=b['home_score'] if t==h else b['away_score']; os_=b['away_score'] if t==h else b['home_score']
            if ts<os_: print('wk%d #%d %s (rating rank %d) lost %d-%d %s %s (rating rank %d)%s'%(w,rk.index(t)+1,t,order[t],ts,os_,'at' if t!=h else 'to',o,order[o],' [rivalry]' if b.get('rivalry') else ''))
print("\n=== C. 2-loss power teams 2042 and the <=1 loss teams ===")
r=records(17)
for t,v in sorted(r.items(),key=lambda kv:kv[1][1]):
    if v[1]<=2: print(t,'%d-%d'%tuple(v),'power' if t in POWER else 'non-power',TIER[t])
print("\n=== D. LARGEST UPSETS BY RATING GAP (gap 21+, favourite lost), 2042 ===")
for w,b in sorted(games(17),key=lambda x:x[0]):
    h,a=b['home'],b['away']
    if h in TEAMS and a in TEAMS:
        gap=(em[h]+2.5)-em[a]
        if abs(gap)>=21 and ((b['home_score']>b['away_score'])!=(gap>0)):
            print('wk%d favourite %s (rk %d) lost %d-%d to %s (rk %d), gap %.0f'%(w,h if gap>0 else a,order[h if gap>0 else a],(b['home_score'] if gap>0 else b['away_score']),(b['away_score'] if gap>0 else b['home_score']),a if gap>0 else h,order[a if gap>0 else h],abs(gap)))
