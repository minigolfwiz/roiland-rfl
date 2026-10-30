import sys, itertools, collections, json
sys.path.insert(0,'.')
from rfl.engine import *
from rfl import matchups_engine as ME
S=load(f'{ROOT}/data/state_2044.json'); R=S['season']['records']; YEAR=2045; y=YEAR-2041
def key(t): r=R[t]; g=r['w']+r['l']+r.get('t',0); return (-(r['w']+r.get('t',0)/2)/g, -(r['pf']-r['pa']))
nick=lambda t:t.split()[-1] if t!='Billiataho Greats' else 'Greats'
DIVS=ME.DIVS; CONFS=ME.CONFS
roster={(c,d):ME.div(c,d) for c in CONFS for d in DIVS}
rank={}; place={}
for k,T in roster.items():
    o=sorted(T,key=key); rank[k]=o
    for i,t in enumerate(o): place[t]=i+1
divof={t:k for k,T in roster.items() for t in T}
games=[]  # (a,b,kind)
# conference
for c in CONFS:
    pairs=[(a,b) for i,a in enumerate(DIVS) for b in DIVS[i+1:]]
    for p,(d1,d2) in enumerate(pairs):
        A,B=roster[(c,d1)],roster[(c,d2)]; a=(y+p)%5
        for i in range(5): games.append((rank[(c,d1)][i],rank[(c,d2)][i],'same place'))
        base={i:(i+a)%5 for i in range(5)}
        best=None
        for perm in itertools.permutations(range(5)):
            if any(place[A[i]]==place[B[perm[i]]] for i in range(5)): continue
            cost=sum(perm[i]!=base[i] for i in range(5))
            if best is None or cost<best[0]: best=(cost,perm)
        bumped=sum(1 for i in range(5) if place[A[i]]==place[B[base[i]]])
        for i in range(5): games.append((A[i],B[best[1][i]],'rotation'))
# interconference
for r,dr in enumerate(DIVS):
    for m,dm in enumerate(DIVS):
        k=((r+m+y)%4)+1
        for p in range(5): games.append((rank[('Regal',dr)][p],rank[('Majestic',dm)][(p+k)%5],'interconf'))
assert len(games)==40*10//2*1+0 or True
opp=collections.defaultdict(list)
for a,b,kd in games: opp[a].append((kd,b)); opp[b].append((kd,a))
assert all(len(v)==10 for v in opp.values()), collections.Counter(len(v) for v in opp.values())
assert all(len({b for _,b in v})==10 for v in opp.values())
assert all(not any(divof[b]==divof[a] for _,b in opp[a]) for a in opp)
ordn={1:'1st',2:'2nd',3:'3rd',4:'4th',5:'5th'}
rec=lambda t:f"{R[t]['w']}-{R[t]['l']}"+(f"-{R[t]['t']}" if R[t].get('t') else '')
# old rotation for comparison
old=collections.defaultdict(list)
for g in ME.games_for(YEAR):
    if g['kind']!='division': old[g['host']].append(g['visitor']); old[g['visitor']].append(g['host'])
wp=lambda t:(R[t]['w']+R[t].get('t',0)/2)/(R[t]['w']+R[t]['l']+R[t].get('t',0))
sos=lambda L:sum(wp(x) for x in L)/len(L)
out=[]
for c in CONFS:
    for d in DIVS:
        out.append(f"## {c} {d}")
        for t in rank[(c,d)]:
            out.append(f"### {t} ({ordn[place[t]]}, {rec(t)})")
            for kd in ('same place','rotation','interconf'):
                out.append(f"- {kd}: "+', '.join(f"{nick(b)} ({ordn[place[b]]} in {divof[b][0][:3]} {divof[b][1]}, {rec(b)})" for k2,b in opp[t] if k2==kd))
            out.append(f"- Non-division opponents' avg win pct: new {sos([b for _,b in opp[t]]):.3f} vs old rotation {sos(old[t]):.3f}")
open('out/nfl_style_2045_example.md','w').write('\n'.join(out))
import statistics
new=[sos([b for _,b in opp[t]]) for t in opp]; oldv=[sos(old[t]) for t in opp]
print('spread (stdev of opp win pct) new',round(statistics.pstdev(new),3),'old',round(statistics.pstdev(oldv),3))
by=collections.defaultdict(lambda:[[],[]])
for t in opp: by[place[t]][0].append(sos([b for _,b in opp[t]])); by[place[t]][1].append(sos(old[t]))
for p in sorted(by): print(ordn[p],'new',round(sum(by[p][0])/8,3),'old',round(sum(by[p][1])/8,3))
for t in ('Port Logan Commodores','Billiataho Greats'):
    print('\n'.join(l for l in out[out.index(next(x for x in out if x.startswith('### '+t))):][:5]))
