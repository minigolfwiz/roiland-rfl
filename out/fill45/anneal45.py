"""Standalone version of rfl_fill_anneal.py for 2044. Usage: python3 -I anneal44.py seed seconds fixw out.json"""
import json, sys, random, collections, math, time
seed=int(sys.argv[1]); budget=float(sys.argv[2]); FIXW=float(sys.argv[3]); OUT=sys.argv[4]
G=json.load(open('games2045.json')); hand=json.load(open('handoff2045.json'))
fixed={r['id']:r['week'] for r in hand['prime']}; fixed.update({r['id']:r['week'] for r in hand['pins']})
W=list(range(1,21)); rnd=random.Random(seed); teams=sorted({g['host'] for g in G}); NG=len(G)
host=[g['host'] for g in G]; vis=[g['visitor'] for g in G]; isdiv=[g['kind']=='division' for g in G]
fixw=[fixed.get(g['id']) for g in G]
def opp(i,t): return vis[i] if host[i]==t else host[i]
def stage1():
    for attempt in range(1,2000):
        r=random.Random(seed*1000+attempt)
        week=[fixw[i] for i in range(NG)]; slot={t:[None]*21 for t in teams}; ok=True
        for i,w in enumerate(week):
            if w is not None:
                for t in (host[i],vis[i]):
                    if slot[t][w] is not None: ok=False
                    slot[t][w]=i
        if not ok: print('fixed games collide'); return None,None
        left=[i for i in range(NG) if week[i] is None]
        def free(i): return [w for w in W if slot[host[i]][w] is None and slot[vis[i]][w] is None]
        stuck=False
        while left:
            i=min(left,key=lambda k:(len(free(k)),r.random())); f=free(i)
            if not f: stuck=True; break
            per=collections.Counter(w for w in week if w is not None)
            w=min(f,key=lambda w:per[w]+r.random()*.8); week[i]=w; slot[host[i]][w]=i; slot[vis[i]][w]=i; left.remove(i)
        if not stuck: return week,slot
    return None,None
week,slot=stage1()
if week is None: print('stage 1 failed'); sys.exit(1)
def team_cost(t):
    sl=slot[t]; c=0; byes=[w for w in W if sl[w] is None]
    if len(byes)!=2: c+=5*abs(len(byes)-2)
    else:
        b1,b2=byes
        if not (4<=b1<=11): c+=2
        if not (12<=b2<=18): c+=2
        if b2-b1<4: c+=2
    run=0; last=None; prev=None
    for w in W:
        i=sl[w]
        if i is None: continue
        s=host[i]==t
        if s==last: run+=1
        else: run=1; last=s
        if run>2: c+=2
        if prev is not None and isdiv[i] and isdiv[prev] and sl[w-1]==prev and opp(i,t)==opp(prev,t): c+=2
        prev=i
    return c
def fixpen(i): return FIXW if fixw[i] is not None and week[i]!=fixw[i] else 0
tc={t:team_cost(t) for t in teams}; cost=sum(tc.values())+sum(fixpen(i) for i in range(NG))
def chain(t,w1,w2):
    S=set(); st=[t]
    while st:
        x=st.pop()
        if x in S: continue
        S.add(x)
        for w in (w1,w2):
            i=slot[x][w]
            if i is not None:
                o=opp(i,x)
                if o not in S: st.append(o)
    return S
def apply_partial(S,w1,w2):
    games=set()
    for x in S:
        for w in (w1,w2):
            i=slot[x][w]
            if i is not None: games.add(i)
    for i in games:
        for t in (host[i],vis[i]): slot[t][week[i]]=None
    for i in games: week[i]=w2 if week[i]==w1 else w1
    for i in games:
        for t in (host[i],vis[i]): slot[t][week[i]]=i
    return games
T=.8; t0=time.time(); best=(cost,list(week)); it=0
while time.time()-t0<budget and best[0]>0:
    it+=1
    if rnd.random()<.15: w1,w2=rnd.sample(W,2); S=set(teams)
    else:
        t=rnd.choice(teams); w1,w2=rnd.sample(W,2)
        if slot[t][w1] is None and slot[t][w2] is None: continue
        S=chain(t,w1,w2)
        if len(S)>14: continue
    games={slot[x][w] for x in S for w in (w1,w2) if slot[x][w] is not None}
    before=sum(tc[x] for x in S)+sum(fixpen(i) for i in games); apply_partial(S,w1,w2)
    after={x:team_cost(x) for x in S}; d=sum(after.values())+sum(fixpen(i) for i in games)-before
    if d<=0 or rnd.random()<math.exp(-d/T):
        tc.update(after); cost+=d
        if cost<best[0]: best=(cost,list(week))
    else: apply_partial(S,w1,w2)
    if it%20000==0:
        T=max(.06,T*.95); cost=sum(tc.values())+sum(fixpen(i) for i in range(NG))
        if it%600000==0 and cost>0: T=.5
cost,week=best
slot={t:[None]*21 for t in teams}
for i,w in enumerate(week): slot[host[i]][w]=i; slot[vis[i]][w]=i
tc={t:team_cost(t) for t in teams}
moved=[(G[i]['id'],fixw[i],week[i]) for i in range(NG) if fixw[i] is not None and week[i]!=fixw[i]]
viol={t:v for t,v in tc.items() if v}
print('seed',seed,'cost',cost,'violations',len(viol),'moved',len(moved),flush=True)
json.dump(dict(seed=seed,cost=cost,viol=viol,moved=moved,weeks={g['id']:week[i] for i,g in enumerate(G)}),open(OUT,'w'))
