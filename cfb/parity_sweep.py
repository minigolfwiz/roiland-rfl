"""Parity sweep (2042 audit): replay the 2042 regular-season slate on the current rosters
under different NOISE_SCALE / RIVALRY_GAP settings, many reps each, and score the things
Dan cares about. Nothing is persisted: rosters are never written back, results never stored.
Usage: python3 parity_sweep.py <noise> <rivalry_gap> <reps> <out.json>"""
import sys, json, collections, statistics, random
sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, subdivision as SUB
from games_db import load_db
SUB.register(E); U=E.U
noise, riv, reps, out = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
E.NOISE_SCALE=noise; E.RIVALRY_GAP=riv
s=SE.load_state(); db=load_db()
TEAMS=set(U['teams']); tal={t:SE._talent(t) for t in TEAMS}
slate=[(w,db[g]) for w,g in s['results']]
order=sorted(TEAMS,key=lambda t:-tal[t]); top5=order[:5]; top10=set(order[:10]); top15=order[:15]
bins=[(0.15,0.3),(0.3,0.6),(0.6,1.0),(1.0,9)]
agg={'pts':0,'n':0,'one':0,'fw':collections.Counter(),'fn':collections.Counter(),'gm':[],'riv_fw':0,'riv_fn':0,'riv_oth_fw':0,'riv_oth_fn':0,
     'und':[], 'le2':[], 'top5L':[], 'top15L':[], 'top10w':[0,0], 'rank_up':[0,0], 'wk14fw':[0,0]}
for r in range(reps):
    rec=collections.defaultdict(lambda:[0,0])
    for i,(w,b) in enumerate(slate):
        h,a=b['home'],b['away']
        box,_=E.simulate_game(h,a,31000000+r*10000+i,site='home',rivalry=b['rivalry'],keep_pbp=False)
        hs,as_=box['home_score'],box['away_score']
        agg['pts']+=hs+as_; agg['n']+=2; agg['one']+= abs(hs-as_)<=8
        hin,ain=h in TEAMS,a in TEAMS
        if hin and ain:
            gap=tal[h]-tal[a]; ag=abs(gap)
            for j,(lo,hi) in enumerate(bins):
                if lo<=ag<hi:
                    agg['fn'][j]+=1; agg['fw'][j]+= ((hs>as_)==(gap>0))
            if ag>=0.3:
                key='riv' if b['rivalry'] else 'riv_oth'
                agg[key+'_fn' if key=='riv' else 'riv_oth_fn']+=1
                agg[key+'_fw' if key=='riv' else 'riv_oth_fw']+= ((hs>as_)==(gap>0))
            if w==14 and ag>=0.3: agg['wk14fw'][0]+=1; agg['wk14fw'][1]+=((hs>as_)==(gap>0))
        elif hin!=ain:
            f=h if hin else a; agg['gm'].append((hs-as_) if f==h else (as_-hs))
        for t,win in ((h,hs>as_),(a,as_>hs)):
            if t in TEAMS: rec[t][0 if win else 1]+=1
    agg['und'].append(sum(1 for t in rec if rec[t][1]==0)); agg['le2'].append(sum(1 for t in rec if rec[t][1]<=2))
    agg['top5L'].append(statistics.mean(rec[t][1] for t in top5)); agg['top15L'].append(statistics.mean(rec[t][1] for t in top15))
    agg['top10w'][0]+=sum(rec[t][0] for t in top10); agg['top10w'][1]+=sum(rec[t][0]+rec[t][1] for t in top10)
res={'noise':noise,'riv':riv,'reps':reps,'pts_per_team':agg['pts']/agg['n'],'one_score':agg['one']/(agg['n']/2),
     'fav_win':{str(bins[j]):[agg['fw'][j],agg['fn'][j]] for j in range(4)},
     'riv':[agg['riv_fw'],agg['riv_fn']],'nonriv':[agg['riv_oth_fw'],agg['riv_oth_fn']],'wk14':agg['wk14fw'],
     'guest_margin':statistics.mean(agg['gm']),'undefeated':statistics.mean(agg['und']),'le2':statistics.mean(agg['le2']),
     'top5_losses':statistics.mean(agg['top5L']),'top15_losses':statistics.mean(agg['top15L']),'top10_win':agg['top10w'][0]/agg['top10w'][1]}
json.dump(res,open(out,'w'),indent=1); print(json.dumps(res))
