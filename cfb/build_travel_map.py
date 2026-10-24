"""Travel map for a neutral-site playoff round (Dan, 2042): where each team travels from and to,
for the engine's assignment and two alternatives measured on true campus/city positions. Read-only."""
import sys, json, math, itertools, pickle
sys.path.insert(0,'/home/claude/cfb2')
import pbp_engine as E, committee as CM
U=E.U; sc=U['school_coords']
pk=json.load(open('/home/claude/cfb2/state/roiland_map_package.json')); C=pk['cities']
P=pickle.load(open('/home/claude/cfb2/state/playoff_s17.pkl','rb'))
games=P['qf']; seeds=P['seeds']
sd=lambda t: seeds[t] if isinstance(seeds[t],int) else seeds[t].get('seed')
B={b['name']:dict(C['%s, %s'%(b['city'],b['state'])],name=b['name']) for b in CM.BOWLS}
qb=['Lumber Bowl','Copper Bowl','501 Bowl','Redwood Bowl']
d=lambda t,b: math.hypot(sc[t][0]-B[b]['x'],sc[t][1]-B[b]['y'])
def vlabel(t,b):
    bw=[v for v in CM.BOWLS if v['name']==b][0]; return CM.vdist(bw,t)
# engine assignment, recomputed with its own rule (state label positions, seed order, nearest free)
used=set(); eng={}
for h,l in games:
    v=CM.rotation_venue(17,'QF',h,used); eng[h]=v['name']
greedy={}; used=set()
for h,l in games:
    b=min([x for x in qb if x not in used],key=lambda x:d(h,x)); used.add(b); greedy[h]=b
best=None
for perm in itertools.permutations(qb):
    a={g[0]:perm[i] for i,g in enumerate(games)}
    t=sum(d(h,a[h])+d(l,a[h]) for h,l in games)
    if best is None or t<best[0]: best=(t,a)
scen=[('built','As built','Engine rule: nearest free bowl to the higher seed, measured between state label positions.',eng),
      ('true','Nearest to higher seed, true positions','Same seed order and same rule, measured campus to bowl city.',greedy),
      ('min','Least total travel','Every team counted, whichever seed it is.',best[1])]
teams={}
for h,l in games:
    for t in (h,l):
        teams[t]={'x':sc[t][0],'y':sc[t][1],'seed':sd(t),'col':U['team_colors'].get(t,['#444','#999'])[0],'rec':'%d-%d'%(0,0)}
S=SE=None
import season as SE
s=SE.load_state()
for t in teams: teams[t]['rec']='%d-%d'%(s['record'][t]['W'],s['record'][t]['L'])
out=[]
for key,name,desc,a in scen:
    rows=[]
    for h,l in games:
        b=a[h]; rows.append({'hi':h,'lo':l,'bowl':b,'dh':round(d(h,b)),'dl':round(d(l,b))})
    out.append({'key':key,'name':name,'desc':desc,'rows':rows,'total':round(sum(r['dh']+r['dl'] for r in rows))})
# every team to every bowl, for the lookup table
tab={t:{b:round(d(t,b)) for b in qb} for t in teams}
tabl={t:{b:round(vlabel(t,b)) for b in qb} for t in teams if t in [g[0] for g in games]}
tpl=open('/home/claude/cfb2/travel_map_template.html').read()
img=pk['image_png_base64']
html=(tpl.replace('__IMG__',img).replace('__TEAMS__',json.dumps(teams)).replace('__BOWLS__',json.dumps(B))
        .replace('__SCEN__',json.dumps(out)).replace('__TAB__',json.dumps(tab)).replace('__TABL__',json.dumps(tabl)))
open('/home/claude/cfb2/travel_map.html','w').write(html)
print(len(html)//1024,'KB'); [print(o['name'],o['total'],[(r['hi'],r['bowl'],r['dh'],r['dl']) for r in o['rows']]) for o in out]
