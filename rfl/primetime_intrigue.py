import json,sys,collections
S=json.load(open('data/state_2042.json')); P=S['players']
h=open('/tmp/claude-0/-home-claude/e38e28a8-ca5b-53b1-aea6-45c802c40f9b/scratchpad/arch43/index.html').read(); i=h.index('const D = ')+10; D,_=json.JSONDecoder().raw_decode(h[i:])
pdata=open('/tmp/pt/data.js').read(); G=json.JSONDecoder().raw_decode(pdata[len('const DATA = '):])[0]['games']
BR=json.load(open('/tmp/pt/brand.json')) if False else None
nick=lambda t:t.split(' ')[-1] if t not in('Brass Tigers',) else t
def nk(t):
    for n in ['Brass Tigers','Sea Lions','T-Rexes','Leatherbacks']:
        if t.endswith(n): return n
    return t.split(' ')[-1]
s42=D['seasons']['2042']; res=s42['res']
wp=lambda t:(res[t][0]+res[t][2]/2)/sum(res[t]); rs=lambda t:f"{res[t][0]}-{res[t][1]}"+(f"-{res[t][2]}" if res[t][2] else '')
top=sorted(res,key=lambda t:-wp(t))[:8]; champ=s42['champ']
titles={t:len(a['titles']) for t,a in D['allt'].items()}
seeded={t for c in s42['seeds'].values() for t in c}
# QBs
qb={}
for t,c in S['clubs'].items():
    q=[P[str(x)] for x in c['roster'] if P[str(x)]['pos']=='QB']
    if q: qb[t]=max(q,key=lambda p:p['abil'])
rank=sorted(qb,key=lambda t:-qb[t]['abil']); topq=set(rank[:8])
rook1={t for t,p in qb.items() if p.get('draft') and p['draft']['year']==2043 and p['draft']['round']==1}
rookq={t for t,p in qb.items() if p.get('draft') and p['draft']['year']==2043}
# former clubs
fmr=collections.defaultdict(list)  # (current club, old club) -> [players]
for t,c in S['clubs'].items():
    ps=sorted([P[str(x)] for x in c['roster'] if P[str(x)]['pos'] not in('K','P')],key=lambda p:-p['abil'])[:6]
    for p in ps:
        for f,cl,to in p.get('career',[]):
            if cl!=t and to>=2038 and (to-f+1)>=4: fmr[(t,cl)].append((p,f,to))
# coaches
cb={c['name']:c for c in D['coaches']}; gb={g['name']:g for g in D['gms']}
stf=collections.defaultdict(list)
for t,c in S['clubs'].items():
    for kind,nm,db in (('HC',c['coach']['name'],cb),('GM',c['gm']['name'],gb)):
        pe=db.get(nm)
        if not pe: continue
        for st in pe['stints']:
            if st['club']!=t and st['role'] in('HC','GM') and st['end'] is not None: stf[(t,st['club'])].append((kind,nm,st))
# playoffs
po=collections.defaultdict(list)
for g in s42['po']:
    po[frozenset((g['home'],g['away']))].append(g)
out={}
for g in G:
    a,b=g['host'],g['visitor']; R=[]
    k=frozenset((a,b))
    if k in po:
        for x in po[k]:
            w=x['winner'];l=x['away'] if w==x['home'] else x['home']; ws=max(x['home_pts'],x['away_pts']); ls=min(x['home_pts'],x['away_pts'])
            if x['stage']=='Mega Bowl': R.append(('rematch',f"Mega Bowl rematch: the {nk(w)} beat the {nk(l)} {ws}–{ls} for the 2042 title."))
            else: R.append(('rematch',f"2042 playoff rematch: the {nk(w)} eliminated the {nk(l)} {ws}–{ls} ({x['stage'].lower()})."))
    if a in top and b in top and not any(r[0]=='rematch' for r in R):
        R.append(('top',f"Two of last year's best: the {nk(b)} ({rs(b)}) and the {nk(a)} ({rs(a)}) were both top-eight in the standings."))
    elif champ in (a,b) and not any(r[0]=='rematch' for r in R):
        o=b if a==champ else a
        R.append(('champ',f"The defending champion {nk(champ)} ({rs(champ)} in 2042) take on the {nk(o)} ({rs(o)})."))
    if a in topq and b in topq: R.append(('qb',f"Quarterback duel: {qb[b]['name']} ({nk(b)}) vs {qb[a]['name']} ({nk(a)}), two of the league's top passers."))
    elif (a in rook1 and b in topq) or (b in rook1 and a in topq):
        r=a if a in rook1 else b; v=b if r==a else a
        R.append(('qb',f"Rookie test: No. {qb[r]['draft']['pick']} pick {qb[r]['name']} ({nk(r)}) against one of the league's top quarterbacks, {qb[v]['name']} ({nk(v)})."))
    elif a in rookq and b in rookq: R.append(('qb',f"Rookie quarterbacks {qb[b]['name']} ({nk(b)}) and {qb[a]['name']} ({nk(a)}) meet."))
    for x,y in ((a,b),(b,a)):
        pl=fmr.get((x,y),[])
        if pl:
            p,f0,to=pl[0]; more=f" (and {len(pl)-1} more)" if len(pl)>1 else ''
            R.append(('former',f"{p['name']} ({p['pos']}) faces his old club: with the {nk(y)} {f0}–{to}, now with the {nk(x)}{more}.".replace('his old club','a former club') ))
        for kind,nm,st in stf.get((x,y),[])[:1]:
            R.append(('staff',f"{nk(x)} {'head coach' if kind=='HC' else 'general manager'} {nm} returns to face the {nk(y)}, whom he {'coached' if kind=='HC' else 'ran the front office for'} {st['start']}–{st['end']}."))
    if titles.get(a,0)==0 and titles.get(b,0)==0:
        R.append(('drought',f"Title-less clash: neither the {nk(a)} nor the {nk(b)} has ever won a Mega Bowl."))
    if g['kind']=='division' and a in seeded and b in seeded and not any(r[0] in('rematch','top') for r in R):
        R.append(('div',f"Division rivals who both reached the 2042 playoffs."))
    if R: out[g['id']]=R
json.dump({k:[list(r) for r in v] for k,v in out.items()},open('/tmp/pt/intrigue.json','w'),ensure_ascii=False)
c=collections.Counter(r[0] for v in out.values() for r in v); print(len(out),c)
for k,v in list(out.items())[:0]: pass
import itertools
for t in('rematch','top','qb','former','staff','drought'):
    for k,v in out.items():
        for r in v:
            if r[0]==t: print(t,k,G[int(k[1:])]['visitor'],'at',G[int(k[1:])]['host'],'|',r[1]); break
        else: continue
        break
print(rank, [ (t,qb[t]['name']) for t in rank[:8]])
