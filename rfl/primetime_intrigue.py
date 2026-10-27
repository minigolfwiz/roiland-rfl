import json,collections,re
S=json.load(open('data/state_2042.json')); P=S['players']; SS=json.load(open('data/rfl_2042_season.json'))
h=open('/tmp/claude-0/-home-claude/e38e28a8-ca5b-53b1-aea6-45c802c40f9b/scratchpad/arch43/index.html').read(); i=h.index('const D = ')+10; D,_=json.JSONDecoder().raw_decode(h[i:])
pdata=open('/tmp/pt/data.js').read(); DT=json.JSONDecoder().raw_decode(pdata[len('const DATA = '):])[0]; G=DT['games']; TI=DT['teams']
def nk(t):
    for n in ['Brass Tigers','Sea Lions','T-Rexes','Leatherbacks']:
        if t.endswith(n): return n
    return t.split(' ')[-1]
rec=S['season']['records']; res={t:(r['w'],r['l'],r['t']) for t,r in rec.items()}
wp=lambda t:(res[t][0]+res[t][2]/2)/sum(res[t]); rs=lambda t:f"{res[t][0]}-{res[t][1]}"+(f"-{res[t][2]}" if res[t][2] else '')
order=sorted(res,key=lambda t:-wp(t)); top=order[:8]; bottom=order[-6:]
s42=D['seasons']['2042']; champ=s42['champ']; seeded={t for c in s42['seeds'].values() for t in c}
res41=D['seasons']['2041']['res']
nm=lambda p:p['name']
active={pid:p for pid,p in P.items() if p['status']=='active' and p.get('club')}
stats=S['season']['stats']
def leaders(key,n,pos=None):
    r=[(pid,v.get(key,0)) for pid,v in stats.items() if pid in active and v.get(key,0) and (pos is None or active[pid]['pos'] in pos)]
    return sorted(r,key=lambda x:-x[1])[:n]
L={k:leaders(k,n,pos) for k,n,pos in (('pass_yds',5,None),('rush_yds',5,None),('rec_yds',5,None),('sacks',5,None),('int_made',4,None))}
def lead_in(club,key): return [(active[pid],v) for pid,v in L[key] if active[pid]['club']==club]
# QB set
qb={}
for t,c in S['clubs'].items():
    q=[P[str(x)] for x in c['roster'] if P[str(x)]['pos']=='QB']
    if q: qb[t]=max(q,key=lambda p:p['abil'])
topabil=sorted(qb,key=lambda t:-qb[t]['abil'])[:6]
passl=[active[pid]['club'] for pid,_ in L['pass_yds']]
mvp=s42['aw']['MVP']; qbset=set(topabil)|set(passl[:5])|({mvp['club']} if mvp['pos']=='QB' else set())
for t in list(qbset):
    pl=lead_in(t,'pass_yds')
    if pl: qb[t]=pl[0][0]
def qbline(t):
    p=qb[t]; st=stats.get(str(p['pid']),{})
    return f"{p['name']} ({nk(t)}" + (f", {st['pass_yds']:,} yards and {st['pass_td']} TDs last year" if st.get('pass_yds') else '') + ")"
rookq={t for t,p in qb.items() if p.get('draft') and p['draft']['year']==2043}; rook1={t for t in rookq if qb[t]['draft']['round']==1}
# po history
series=collections.defaultdict(list)
for y,s in D['seasons'].items():
    for g in s['po']: series[frozenset((g['home'],g['away']))].append((int(y),g))
# last-year games
last42={}
for wk in SS['weeks']:
    for g in wk['games']:
        last42.setdefault(frozenset((g['home'],g['away'])),[]).append((wk['week'],g))
STARTQB={t:q['pid'] for t,q in qb.items()}
# movers & former
fmr=collections.defaultdict(list)
for t,c in S['clubs'].items():
    ps=sorted([P[str(x)] for x in c['roster'] if P[str(x)]['pos'] not in('K','P')],key=lambda p:-p['abil'])
    for rk,p in enumerate(ps):
        new=(p.get('contract') or {}).get('signed')==2043 and p.get('contract',{}).get('kind')!='rookie'
        for f,cl,to in p.get('career',[]):
            if cl==t: continue
            ten=to-f+1
            star=(rk<3 or STARTQB.get(t)==p['pid']); 
            if (star and to>=2038 and ten>=4) or (new and star and to>=2041): fmr[(t,cl)].append((p,f,to,new))
cb={c['name']:c for c in D['coaches']}; gb={g['name']:g for g in D['gms']}
stf=collections.defaultdict(list)
for t,c in S['clubs'].items():
    for kind,nmx,db in (('HC',c['coach']['name'],cb),('GM',c['gm']['name'],gb)):
        pe=db.get(nmx)
        if not pe: continue
        for st in pe['stints']:
            if st['club']!=t and st['end'] is not None and st['role'] in('HC','GM') and st['end']-st['start']>=2: stf[(t,st['club'])].append((kind,nmx,st))
# trades
trd=collections.defaultdict(list)
for line in S['offseason']['trades']:
    m=re.match(r'(.+?) trade (.+?) \((\w+), [\d.]+\) to (.+?) for (.+)',line)
    if m: trd[frozenset((m.group(1),m.group(4)))].append((m.group(1),m.group(2),m.group(3),m.group(4),m.group(5)))
# draft
d43=sorted([p for p in P.values() if p.get('draft') and p['draft']['year']==2043],key=lambda p:p['draft']['pick'])
top5={p['draft']['club']:p for p in d43[:5]}
cls=collections.defaultdict(list)
for p in d43:
    if p['draft']['pick']<=40: cls[(p['college'])].append(p)
# awards
aw=s42['aw']; awc=collections.defaultdict(list)
for k,v in aw.items():
    if k in('Offensive Player of the Year','Mega Bowl MVP'): continue
    awc[v['club']].append((k,v['name']))
# rise/fall, droughts
chg={t:(res[t][0]-res41[t][0]) for t in res if t in res41}
lastpo={}
for y,s in D['seasons'].items():
    for c in s['seeds'].values():
        for t in c: lastpo[t]=int(y)
pdr={t:2042-lastpo.get(t,0) for t in res}
pw=collections.Counter()
for y,s in D['seasons'].items():
    for g in s['po']: pw[g['winner']]+=1
titles={t:len(a['titles']) for t,a in D['allt'].items()}
ppg={t:rec[t]['pf']/18 for t in rec}; papg={t:rec[t]['pa']/18 for t in rec}
topO=sorted(ppg,key=lambda t:-ppg[t])[:3]; topD=sorted(papg,key=lambda t:papg[t])[:3]
hct={}
for t,c in S['clubs'].items():
    pe=cb.get(c['coach']['name']); hct[t]=(pe['name'],len(pe['titles'])) if pe else (c['coach']['name'],0)
out={}
for g in G:
    a,b=g['host'],g['visitor']; k=frozenset((a,b)); R=[]
    def add(w,t,s): R.append((w,t,s))
    # 1 playoff meetings & finals
    sr=series.get(k,[])
    if sr:
        wins=collections.Counter(x[1]['winner'] for x in sr); mb=[x for x in sr if x[1]['stage']=='Mega Bowl']
        recent=[x for x in sr if x[0]>=2041]
        if recent:
            y,x=recent[-1]; w=x['winner']; l=x['away'] if w==x['home'] else x['home']; ws,ls=max(x['home_pts'],x['away_pts']),min(x['home_pts'],x['away_pts'])
            add(1,'rematch',f"{'Mega Bowl' if x['stage']=='Mega Bowl' else 'Playoff'} rematch: the {nk(w)} beat the {nk(l)} {ws}–{ls} in the {y} {x['stage'].lower() if x['stage']!='Mega Bowl' else 'Mega Bowl'}.")
        if len(sr)>=6 or mb:
            ld=wins.most_common(); s1=f"the {nk(ld[0][0])} lead the playoff series {ld[0][1]}–{ld[1][1] if len(ld)>1 else 0}" if len(ld)==1 or ld[0][1]!=ld[1][1] else f"the playoff series is tied {ld[0][1]}–{ld[1][1]}"
            extra=f" and met in the Mega Bowl in {mb[-1][0]}" if mb else ''
            if not recent or len(sr)>=6: add(3,'series',f"Postseason history: {len(sr)} playoff meetings, {s1}{extra} (last in {sr[-1][0]}).")
    # 2 last year
    if k in last42:
        for wkn,x in last42[k][:1]:
            hp,ap=x['score']; w=x['home'] if hp>ap else x['away']; l=x['away'] if w==x['home'] else x['home']; ws,ls=max(hp,ap),min(hp,ap)
            if False: pass
            elif False: add(2,'last',f"Last year's meeting (week {wkn}) was a thriller: the {nk(w)} edged the {nk(l)} {ws}–{ls}.")
            elif ws-ls>=35: add(2,'last',f"Revenge spot: the {nk(w)} beat the {nk(l)} {ws}–{ls} last year (week {wkn}).")
            elif wp(w)+.3<wp(l): add(2,'last',f"Last year's upset (week {wkn}): the {nk(w)} ({rs(w)}) beat the better {nk(l)} ({rs(l)}) {ws}–{ls}.")
    # 3 champions
    pair41={D['seasons']['2041']['champ'],champ}
    if k==frozenset(pair41): add(1,'champs',f"Back-to-back champions meet: {nk(D['seasons']['2041']['champ'])} (2041) and {nk(champ)} (2042). The {nk('Diamond City Hope')} are {rs('Diamond City Hope')} since winning it all.")
    # 4 top teams
    if a in top and b in top: add(2,'top',f"Two of last year's best: the {nk(b)} ({rs(b)}) and the {nk(a)} ({rs(a)}) both finished top eight.")
    # 5 qb
    if a in qbset and b in qbset: add(1,'qb',f"Quarterback duel: {qbline(b)} vs {qbline(a)}.")
    elif (a in rook1 and b in qbset) or (b in rook1 and a in qbset):
        r=a if a in rook1 else b; v=b if r==a else a
        add(1,'qb',f"Rookie test: No. {qb[r]['draft']['pick']} pick {qb[r]['name']} ({nk(r)}) against {qbline(v)}.")
    elif a in rookq and b in rookq: add(2,'qb',f"Two rookie quarterbacks meet: {qb[b]['name']} ({nk(b)}, No. {qb[b]['draft']['pick']}) and {qb[a]['name']} ({nk(a)}, No. {qb[a]['draft']['pick']}).")
    # 6 stat leaders
    for (cx,cy) in ((a,b),(b,a)):
        pl=lead_in(cx,'pass_yds'); sk=lead_in(cy,'sacks')
        if pl and sk: add(2,'lead',f"Passer vs pass rusher: {nm(pl[0][0])} ({nk(cx)}) threw for {pl[0][1]:,} yards last year; {nm(sk[0][0])} ({nk(cy)}) had {sk[0][1]} sacks.")
        rc=lead_in(cx,'rec_yds'); ib=lead_in(cy,'int_made')
        if rc and ib: add(2,'lead',f"Top target vs ball hawk: {nm(rc[0][0])} ({nk(cx)}, {rc[0][1]:,} receiving yards) against {nm(ib[0][0])} ({nk(cy)}, {ib[0][1]} interceptions).")
        ru=lead_in(cx,'rush_yds'); pp=lead_in(cy,'pass_yds')
        if ru and pp: add(2,'lead',f"Ground vs air: rushing star {nm(ru[0][0])} ({nk(cx)}, {ru[0][1]:,} yards) meets passing star {nm(pp[0][0])} ({nk(cy)}).")
    # 7 offense/defense
    for (cx,cy) in ((a,b),(b,a)):
        if cx in topO and cy in topD: add(2,'unit',f"Unstoppable force: the {nk(cx)} averaged {ppg[cx]:.1f} points last year; the {nk(cy)} allowed just {papg[cy]:.1f}.")
    # 8 awards
    ca,cbb=awc.get(a,[]),awc.get(b,[])
    if ca and cbb: add(2,'award',f"Award winners collide: {nk(a)} ({', '.join(f'{n} – {x}' for x,n in ca)}) vs {nk(b)} ({', '.join(f'{n} – {x}' for x,n in cbb)}).")
    # 9 draft
    if a in top5 and b in top5: add(1,'draft',f"Top-five picks meet: No. {top5[b]['draft']['pick']} {top5[b]['name']} ({nk(b)}) and No. {top5[a]['draft']['pick']} {top5[a]['name']} ({nk(a)}).")
    for col,ps in cls.items():
        pa=[p for p in ps if p['draft']['club']==a]; pb=[p for p in ps if p['draft']['club']==b]
        if pa and pb: add(3,'class',f"College teammates, now rivals: {pb[0]['name']} ({nk(b)}) and {pa[0]['name']} ({nk(a)}) both came out of {col} in this year's draft.")
    # 10 former/movers/trades
    for x,y in ((a,b),(b,a)):
        pl=fmr.get((x,y),[])
        if pl:
            p,f0,to,new=pl[0]; more=f" (plus {len(pl)-1} more ex-{nk(y)})" if len(pl)>1 else ''
            add(1 if new else 2,'former',f"{p['name']} ({p['pos']}) {'joined the '+nk(x)+' this year and ' if new else ''}faces former club the {nk(y)} ({f0}–{to}){more}.")
        for kind,nmx,st in stf.get((x,y),[])[:1]:
            role={'HC':'head coach','GM':'general manager'}.get(st['role'],st['role'])
            add(2,'staff',f"{nk(x)} {'head coach' if kind=='HC' else 'general manager'} {nmx} faces the {nk(y)}, whom they led as {role} {st['start']}–{st['end']}.")
    for (s1,pn,pos,s2,pk) in trd.get(k,[]): add(2,'trade',f"Offseason trade partners: the {nk(s1)} sent {pn} ({pos}) to the {nk(s2)} for a {pk.replace('a 2043 ','')} pick.")
    # 11 geography
    if TI[a]['city']==TI[b]['city']: add(1,'derby',f"Same-city derby: both clubs play in {TI[a]['city']}.")
    elif TI[a]['state']==TI[b]['state']: add(3,'derby',f"In-state rivals: both clubs call {TI[a]['state']} home.")
    # 12 trajectories
    if a in bottom and b in bottom: add(2,'cellar',f"Cellar clash: last year's {rs(a)} {nk(a)} and {rs(b)} {nk(b)} — two of the league's six worst records.")
    ra,rb=chg.get(a,0),chg.get(b,0)
    for u,d in ((a,b),(b,a)):
        if chg.get(u,0)>=6 and chg.get(d,0)<=-6: add(3,'swing',f"Rise vs fall: the {nk(u)} jumped {chg[u]} wins to {rs(u)}; the {nk(d)} dropped {-chg[d]} to {rs(d)}.")
    if pdr[a]>=5 and pdr[b]>=5: add(2,'drought',f"Two clubs starved for January football: playoff droughts of {pdr[a]} years ({nk(a)}) and {pdr[b]} ({nk(b)}).")
    if pw[a]==0 and pw[b]==0: add(1,'drought',f"Neither the {nk(a)} nor the {nk(b)} has ever won a playoff game.")
    # 13 coaches
    if hct[a][1]>=2 and hct[b][1]>=2: add(2,'coach',f"Decorated sidelines: {hct[b][0]} ({nk(b)}, {hct[b][1]} titles) vs {hct[a][0]} ({nk(a)}, {hct[a][1]} titles).")
    if R:
        R.sort(key=lambda r:r[0]); out[g['id']]=[[r[1],r[2]] for r in R[:3]]
json.dump(out,open('/tmp/pt/intrigue.json','w'),ensure_ascii=False)
c=collections.Counter(r[0] for v in out.values() for r in v); print(len(out),c)
seen=set()
for gid,v in out.items():
    for r in v:
        if r[0] not in seen: seen.add(r[0]); print(r[0],'|',r[1])
