"""Detail for Gameview candidates (Dan's standing request, 2042 wk 2).
Usage: python3 gameview_detail.py <week> "Visitor@Host" ...   (uses the last played week's box scores)"""
import sys; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db
SUB.register(E); U=E.U
s=SE.load_state(); db=load_db()
wk=int(sys.argv[1]); rk={t:r for r,t in s['media_poll_current'] if r<=25}
sched=[g for g in s['sched'] if g[0]==wk]; res=list(s['results'])
for arg in sys.argv[2:]:
    a,h=arg.split('@'); g=[g for g in sched if g[1]==h and g[2]==a][0]
    print('='*60); print('%s at %s (%s)'%(a,h,'conference game' if g[3] else 'non-conference'))
    print(' %s vs %s | host state %s'%(U['team_conf'].get(a,'guest'),U['team_conf'].get(h,'guest'),U['geo'][h]['state']))
    ser=sorted([b for b in db.values() if {b['home'],b['away']}=={h,a}],key=lambda b:(b.get('season',0),b.get('week',0)))
    hw=sum(1 for b in ser if (b['home']==h)==(b['home_score']>b['away_score']))
    print(' series since 2025: %s %d-%d %s (%d)'%(h,hw,len(ser)-hw,a,len(ser)))
    for b in ser[-3:]: print('    %s: %s %d, %s %d'%(2025+b.get('season',0),b['home'],b['home_score'],b['away'],b['away_score']))
    for t in (h,a):
        c=E.COACHES[t]; r=s['record'][t]
        print(' -- %s #%s %d-%d | HC %s yr %s | OC %s | DC %s'%(t,rk.get(t,'NR'),r['W'],r['L'],c['HC']['name'],c['HC'].get('tenure'),c['OC']['name'],c['DC']['name']))
        P={p['pid']:p for p in E.ROSTERS[t]}
        for w,gid in res:
            b=db[gid]
            if t not in (b['home'],b['away']): continue
            opp=b['away'] if b['home']==t else b['home']; ts=b['home_score'] if b['home']==t else b['away_score']; os_=b['away_score'] if b['home']==t else b['home_score']
            rows=[(P[pid],x) for pid,x in b['stats'].items() if pid in P]; out=[]
            for p,x in sorted(rows,key=lambda r:-(r[1].get('PassYds',0)+r[1].get('RushYds',0)+r[1].get('RecYds',0)))[:3]:
                bits=[]
                if x.get('PassYds'): bits.append('%d pass/%dTD/%dINT'%(x['PassYds'],x.get('PassTD',0),x.get('INT',0)))
                if x.get('RushYds',0)>=40: bits.append('%d rush/%dTD'%(x['RushYds'],x.get('RushTD',0)))
                if x.get('RecYds',0)>=60: bits.append('%d rec/%dTD'%(x['RecYds'],x.get('RecTD',0)))
                if bits: out.append('%s %s: %s'%(p['name'],p['pos'],', '.join(bits)))
            inj=[(i['name'],i['pos']) for i in b['injuries'] if i['weeks_out']>=8 and i['name'] in {p['name'] for p in P.values()}]
            print('    wk%d %s %d-%d %s%s | %s | out long-term: %s'%(w,'W' if ts>os_ else 'L',ts,os_,'at ' if b['away']==t else 'v ',opp,'; '.join(out),inj))
