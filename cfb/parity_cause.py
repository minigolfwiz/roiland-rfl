"""Option four: why has the league spread compressed? (2042 audit). Read-only."""
import sys, re, collections, statistics, math
sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db
SUB.register(E); U=E.U
s=SE.load_state(); db=load_db()
TEAMS=set(U['teams']); PRES=U['prestige']
def corr(x,y):
    mx,my=statistics.mean(x),statistics.mean(y)
    sx=math.sqrt(sum((a-mx)**2 for a in x)); sy=math.sqrt(sum((b-my)**2 for b in y))
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/(sx*sy) if sx and sy else 0
def games(n):
    out=[]
    for gid,b in db.items():
        m=re.match(r'S%d(W|P|C)'%n,gid) if n<10 else re.match(r'S%dW'%n if n>=13 else r'S%d'%n,gid)
        if re.match(r'S%dW\d+_'%n,gid) or (n<=12 and re.match(r'S%d[A-Z_]'%n,gid)) : out.append(b)
    return out
def power(n,iters=30):
    g=[(b['home'],b['away'],b['home_score']-b['away_score']) for b in games(n) if b['home'] in TEAMS and b['away'] in TEAMS and 'PO' not in b.get('game_id','') and 'CCG' not in b.get('game_id','')]
    if len(g)<500: return None
    em={t:0.0 for t in TEAMS}
    for _ in range(iters):
        acc=collections.defaultdict(list)
        for h,a,m in g: acc[h].append(m-2.5+em[a]); acc[a].append(-m+2.5+em[h])
        em={t:(statistics.mean(acc[t]) if acc[t] else 0.0) for t in TEAMS}
        mu=statistics.mean(em.values()); em={t:v-mu for t,v in em.items()}
    return em
print("=== 1. SPREAD AND PERSISTENCE OF TEAM STRENGTH, ALL SEASONS WITH FBS GAMES ===")
R={}
for n in range(1,18):
    em=power(n)
    if em: R[n]=em
prev=None
print("season | sd | range | corr with previous season | corr with prestige")
for n in sorted(R):
    v=list(R[n].values()); c=corr([R[n][t] for t in sorted(TEAMS)],[R[n-1][t] for t in sorted(TEAMS)]) if n-1 in R else None
    cp=corr([R[n][t] for t in sorted(TEAMS)],[PRES[t] for t in sorted(TEAMS)])
    print("%d | %.2f | %.1f | %s | %.2f"%(2025+n,statistics.pstdev(v),max(v)-min(v),('%.2f'%c) if c is not None else '-',cp))
import pickle; pickle.dump(R,open('/tmp/R.pkl','wb'))

print("\n=== 2. LONG-RUN: <=2-loss teams, top-10 strength and favourite win % ===")
POWER={t for t in TEAMS if U['tiers'][U['team_conf'][t]]=='P6'}
print("season | teams<=2 L (all) | power <=2 L | top10 mean | fav win% overall")
for n in sorted(R):
    rec=collections.defaultdict(lambda:[0,0])
    gl=[b for b in games(n) if 'PO' not in b.get('game_id','') and 'CCG' not in b.get('game_id','')]
    for b in gl:
        h,a=b['home'],b['away']; hw=b['home_score']>b['away_score']
        for t,w in ((h,hw),(a,not hw)):
            if t in TEAMS: rec[t][0 if w else 1]+=1
    le=sum(1 for t,v in rec.items() if v[1]<=2); lep=sum(1 for t,v in rec.items() if t in POWER and v[1]<=2)
    em=R[n]; fv=fw=0
    for b in gl:
        h,a=b['home'],b['away']
        if h in TEAMS and a in TEAMS:
            gap=(em[h]+2.5)-em[a]
            if abs(gap)>=3: fv+=1; fw+=((b['home_score']>b['away_score'])==(gap>0))
    v=sorted(em.values())
    print("%d | %d | %d | %.1f | %.0f%%"%(2025+n,le,lep,statistics.mean(v[-10:]),100*fw/max(1,fv)))

print("\n=== 3. OFFSEASON MECHANISMS (classes after seasons 10-16) ===")
tl=sorted(TEAMS)
top25p=set(sorted(TEAMS,key=lambda t:-PRES[t])[:25])
print("--- recruiting: class strength vs prestige, and where the stars go ---")
print("class | corr(class avg ability, prestige) | corr(class avg ability, last season's strength) | share of 5-star signees to top-25 prestige | share of 4-5 star | avg class size top25p vs rest")
for n in range(10,17):
    rc=s.get('recruiting_s%d'%n)
    if not rc: continue
    sg=rc['signed']; avg={}; five=four5=tot5=tot45=0; sz_t=[];sz_r=[]
    for t in tl:
        L=sg.get(t,[]); avg[t]=statistics.mean([r['abil'] for r in L]) if L else 0
        (sz_t if t in top25p else sz_r).append(len(L))
        for r in L:
            if r['stars']>=5: tot5+=1; five+= t in top25p
            if r['stars']>=4: tot45+=1; four5+= t in top25p
    c1=corr([avg[t] for t in tl],[PRES[t] for t in tl])
    c2=corr([avg[t] for t in tl],[R[n][t] for t in tl]) if n in R else float('nan')
    print("%d | %.2f | %.2f | %d/%d (%.0f%%) | %.0f%% | %.1f vs %.1f"%(2025+n+1,c1,c2,five,tot5,100*five/max(1,tot5),100*four5/max(1,tot45),statistics.mean(sz_t),statistics.mean(sz_r)))
print("--- draft: picks taken from each team ---")
print("draft after | picks | share from top-25 by last-season strength | corr(picks, last-season strength)")
for n in range(10,17):
    d=s.get('draft_s%d'%n)
    if not d: continue
    pk=d['picks']; c=collections.Counter(p['team'] for p in pk)
    if n not in R: continue
    top25=set(sorted(TEAMS,key=lambda t:-R[n][t])[:25])
    print("%d | %d | %.0f%% | %.2f"%(2025+n,len(pk),100*sum(v for t,v in c.items() if t in top25)/len(pk),corr([c.get(t,0) for t in tl],[R[n][t] for t in tl])))
print("--- development: average yearly progress by team vs strength ---")
for n in range(10,17):
    dv=s.get('development_s%d'%n)
    if not dv or n not in R: continue
    tm=dv['team_means']
    print("%d | mean %.3f | corr(team progress, strength that season) %.2f | corr(team progress, prestige) %.2f | sd of team means %.3f"%(2025+n,dv['mean'],corr([tm.get(t,0) for t in tl],[R[n][t] for t in tl]),corr([tm.get(t,0) for t in tl],[PRES[t] for t in tl]),statistics.pstdev([tm.get(t,0) for t in tl])))
print("--- portal: net flow of value toward strong teams ---")
for n in range(10,17):
    pt=s.get('portal_s%d'%n)
    if not pt or n not in R: continue
    net=collections.Counter()
    for tr in pt['transfers']:
        net[tr['to']]+=tr['value']; net[tr['from']]-=tr['value']
    print("%d | transfers %d | corr(net value, strength) %.2f | corr(net value, prestige) %.2f"%(2025+n,len(pt['transfers']),corr([net.get(t,0) for t in tl],[R[n][t] for t in tl]),corr([net.get(t,0) for t in tl],[PRES[t] for t in tl])))

print("\n=== 4. ELITE RECORDS vs the 2038 restart's projection (top-5 mean losses 1.08, top-15 1.88, top-10 roster wins 70.8%, undefeated 0.83/season) ===")
print("season | undefeated FBS | top-5 by strength: mean L | top-15 mean L | top-10 win% vs FBS")
for n in range(13,18):
    gl=[b for b in games(n) if 'PO' not in b.get('game_id','') and 'CCG' not in b.get('game_id','')]
    rec=collections.defaultdict(lambda:[0,0]); fw=fg=0
    em=R[n]; top10=set(sorted(TEAMS,key=lambda t:-em[t])[:10])
    for b in gl:
        h,a=b['home'],b['away']; hw=b['home_score']>b['away_score']
        for t,w in ((h,hw),(a,not hw)):
            if t in TEAMS: rec[t][0 if w else 1]+=1
            if t in top10: fg+=1; fw+=w
    order=sorted(TEAMS,key=lambda t:-em[t])
    t5=statistics.mean(rec[t][1] for t in order[:5]); t15=statistics.mean(rec[t][1] for t in order[:15])
    print("%d | %d | %.2f | %.2f | %.1f%%"%(2025+n,sum(1 for t in rec if rec[t][1]==0),t5,t15,100*fw/fg))
print("\n=== 5. DOES TALENT STILL FOLLOW PRESTIGE? (rosters now, after the 2042 season) ===")
tal={t:SE._talent(t) for t in tl}
print("corr(roster talent, prestige) now: %.3f  (2038 restart regenerated at 0.951)"%corr([tal[t] for t in tl],[PRES[t] for t in tl]))
v=list(tal.values()); print("roster talent sd %.3f range %.2f"%(statistics.pstdev(v),max(v)-min(v)))
print("corr(2042 season strength, roster talent now) %.2f ; (2042 strength, prestige) %.2f"%(corr([R[17][t] for t in tl],[tal[t] for t in tl]),corr([R[17][t] for t in tl],[PRES[t] for t in tl])))
