"""Full previews for a playoff round (Dan: 'full previews like usual'). Read-only.
Usage: python3 playoff_preview.py   -> first-round games from state/playoff_s17.pkl"""
import sys, pickle, collections; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB, committee as CM
from games_db import load_db
SUB.register(E); U=E.U
s=SE.load_state(); db=load_db()
P=pickle.load(open('state/playoff_s%d.pkl'%s['season'],'rb'))
ranked,scores,eff=CM.committee_rank(s,db)
erank={t:i+1 for i,t in enumerate(sorted(U['teams'],key=lambda x:-eff[x]))}
games=P['r1'] if 'r1' in P else None
seed={}
sd=P['seeds']
for k,v in sd.items():
    if isinstance(k,int): seed[v if isinstance(v,str) else v.get('team')]=k
    else: seed[k]=v if isinstance(v,int) else v.get('seed')
def season_games(t):
    out=[]
    for w,gid in s['results']:
        b=db[gid]
        if t in (b['home'],b['away']): out.append((w,gid,b))
    for gid,b in db.items():
        if (str(gid).startswith('S%dCCG'%s['season']) or str(gid).startswith('S%dPO_'%s['season'])) and t in (b['home'],b['away']): out.append((15,gid,b))
    return sorted(out,key=lambda x:x[0])
def leaders(t):
    pl={p['pid']:p for p in E.ROSTERS[t]}; agg=collections.defaultdict(lambda:collections.Counter())
    for w,gid,b in season_games(t):
        for pid,x in b['stats'].items():
            if pid in pl:
                for k,v in x.items():
                    if isinstance(v,(int,float)): agg[pid][k]+=v
    return pl,agg
def show(t):
    r=s['record'][t]; c=E.COACHES[t]
    print('  -- %s (%s) %d-%d | rating rank %d | HC %s yr %s | OC %s | DC %s'%(t,'seed %s'%seed.get(t,'?'),r['W'],r['L'],erank[t],c['HC']['name'],c['HC'].get('tenure'),c['OC']['name'],c['DC']['name']))
    g=season_games(t); pf=pa=0; line=[]
    for w,gid,b in g:
        h=b['home']==t; ts=b['home_score'] if h else b['away_score']; os_=b['away_score'] if h else b['home_score']; opp=b['away'] if h else b['home']
        pf+=ts; pa+=os_
        line.append('%s %d-%d %s'%('W' if ts>os_ else 'L',ts,os_,opp))
    po=[l for l in line if False]
    n=max(1,len(g)); print('     scoring %.1f-%.1f per game'%(pf/n,pa/n))
    losses=[l for l in line if l.startswith('L')]
    print('     losses: '+('; '.join(losses) if losses else 'none'))
    top=sorted([l for l in line if l.startswith('W')],key=lambda l:-erank.get(l.split(' ',2)[2],999)*-1)
    wins=[(erank.get(l.split(' ',2)[2],999),l) for l in line if l.startswith('W')]
    wins.sort(); print('     best wins: '+'; '.join(l for _,l in wins[:3]))
    pl,agg=leaders(t)
    def best(key,n=1):
        return sorted(agg.items(),key=lambda kv:-kv[1].get(key,0))[:n]
    for key,lab in (('PassYds','pass'),('RushYds','rush'),('RecYds','rec')):
        for pid,x in best(key,1 if key!='RecYds' else 2):
            p=pl[pid]
            if key=='PassYds': d='%d yds, %d TD, %d INT'%(x['PassYds'],x['PassTD'],x['INT'])
            elif key=='RushYds': d='%d yds, %d TD'%(x['RushYds'],x['RushTD'])
            else: d='%d yds, %d TD'%(x['RecYds'],x.get('RecTD',0))
            print('     %s %s %s (%s): %s'%(lab,p['name'],p['pos'],p.get('cls','?'),d))
    inj=[]
    for p in E.ROSTERS[t]:
        if p.get('injury') or p.get('inj'): inj.append(p['name'])
    if inj: print('     injured: '+', '.join(inj[:6]))
def preview(a,h):
    print('='*70); print('(%s) %s at (%s) %s'%(seed.get(a),a,seed.get(h),h))
    rk={x:r for r,x in s.get('committee_poll_current',[])}; print('  committee board wk14: %s / %s'%(rk.get(a,'NR'),rk.get(h,'NR')))
    print('  %s / %s | host state %s'%(U['team_conf'].get(a),U['team_conf'].get(h),U['geo'][h]['state']))
    from ccg_preview import series
    w,last=series(db,h,a); n=sum(w.values())
    if n:
        b=last[2]; ws=b['home'] if b['home_score']>b['away_score'] else b['away']
        print('  series: %d meetings, %s %d-%d %s; last: %s won %d-%d (%s)'%(n,h,w[h],w[a],a,ws,max(b['home_score'],b['away_score']),min(b['home_score'],b['away_score']),2025+last[0][0]))
    else: print('  series: first meeting')
    show(h); show(a)
if __name__=='__main__':
    import playoff as PL
    rnd=sys.argv[1] if len(sys.argv)>1 else 'r1'
    if rnd=='r2' and 'r2' not in P:
        pairs=PL._pair_host(P,P['byes'],[r['winner'] for r in P['r1_results']])
    else: pairs=P[rnd]
    for h,a in pairs: preview(a,h)
