"""Mobile-friendly playoff round preview page. Usage: python3 playoff_preview_page.py [r1|r2|...] -> playoff_preview.html"""
import sys, json, collections
sys.path.insert(0,'/home/claude/cfb2')
import playoff_preview as PV
from ccg_preview import series
s,db,E,U,seed,erank=PV.s,PV.db,PV.E,PV.U,PV.seed,PV.erank
rnd=sys.argv[1] if len(sys.argv)>1 else 'r1'
LABEL={'r1':'First round','r2':'Quarterfinals','r3':'Semifinals','r4':'National Championship'}
def team(t):
    r=s['record'][t]; c=E.COACHES[t]
    g=PV.season_games(t); pf=pa=0; line=[]
    for w,gid,b in g:
        h=b['home']==t; ts=b['home_score'] if h else b['away_score']; os_=b['away_score'] if h else b['home_score']; opp=b['away'] if h else b['home']
        pf+=ts; pa+=os_; line.append((ts>os_,ts,os_,opp))
    n=max(1,len(g))
    losses=['%d-%d %s'%(a,b,o) for w,a,b,o in line if not w]
    wins=sorted([(erank.get(o,999),'%d-%d %s'%(a,b,o)) for w,a,b,o in line if w])[:3]
    pl,agg=PV.leaders(t)
    def best(key,k=1): return sorted(agg.items(),key=lambda kv:-kv[1].get(key,0))[:k]
    stars=[]
    for pid,x in best('PassYds'):
        p=pl[pid]; stars.append(['Pass',p['name'],p['pos'],'%d yds, %d TD, %d INT'%(x['PassYds'],x['PassTD'],x['INT'])])
    for pid,x in best('RushYds'):
        p=pl[pid]; stars.append(['Rush',p['name'],p['pos'],'%d yds, %d TD'%(x['RushYds'],x['RushTD'])])
    for pid,x in best('RecYds',2):
        p=pl[pid]; stars.append(['Rec',p['name'],p['pos'],'%d yds, %d TD'%(x['RecYds'],x.get('RecTD',0))])
    return {'name':t,'seed':seed.get(t),'rec':'%d-%d'%(r['W'],r['L']),'conf':U['team_conf'].get(t),
      'hc':c['HC']['name'],'ten':c['HC'].get('tenure'),'oc':c['OC']['name'],'dc':c['DC']['name'],
      'ppg':round(pf/n,1),'papg':round(pa/n,1),'losses':losses,'wins':[w for _,w in wins],'stars':stars}
VEN={}
if rnd in ('qf','sf'):
    import committee as CM
    used=set(PV.P.get('venues_used') or [])
    for h,l in PV.P[rnd]:
        v=CM.rotation_venue(s['season'],rnd.upper(),h,used,l); used.add(v['city'])
        VEN[h]='%s, %s, %s'%(v['name'],v['city'],v['state'])
if rnd=='final':
    import committee as CM
    v=CM.champ_venue(s['season']); VEN[PV.P['final'][0]]='%s (%s), %s'%(v.get('name') or 'Championship',v['city'],v['state'])
def game(h,a):
    rk={x:r for r,x in s.get('committee_poll_current',[])}
    w,last=series(db,h,a); n=sum(w.values())
    if n:
        b=last[2]; ws=b['home'] if b['home_score']>b['away_score'] else b['away']
        ser='%d meetings, %s %d-%d %s. Last: %s won %d-%d (%d)'%(n,h,w[h],w[a],a,ws,max(b['home_score'],b['away_score']),min(b['home_score'],b['away_score']),2025+last[0][0])
        if n==1: ser='1 meeting: %s won %d-%d (%d)'%(ws,max(b['home_score'],b['away_score']),min(b['home_score'],b['away_score']),2025+last[0][0])
    else: ser='First meeting'
    return {'home':team(h),'away':team(a),'venue':VEN.get(h,'%s campus (%s)'%(h,U['geo'][h]['state'])),'series':ser,
            'ranks':{h:rk.get(h),a:rk.get(a)}}
if rnd=='r2' and 'r2' not in PV.P:
    import playoff as PL
    pairs=PL._pair_host(PV.P,PV.P['byes'],[r['winner'] for r in PV.P['r1_results']])
elif rnd=='final': pairs=[PV.P['final']]
else: pairs=PV.P[rnd]
data={'year':2025+s['season'],'round':LABEL.get(rnd,rnd),'games':[game(h,a) for h,a in pairs]}
tpl=open('playoff_preview_template.html').read()
open('playoff_preview.html','w').write(tpl.replace('__DATA__',json.dumps(data,separators=(',',':'))))
print(len(data['games']),'games')
