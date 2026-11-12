import gzip,pickle,json,random,colorsys,math
S='/tmp/claude-0/-home-claude/a8ff99bb-ab82-56bb-a24f-2fc85e5c5875/scratchpad/'
u=pickle.load(gzip.open('/home/claude/roiland-rfl/cfb/state/universe.pkl.gz'));tc=u['team_colors']
names=[r[0] for r in json.load(open(S+'sg/data.json'))['schools']]
def norm(k):
    if k=='S Antiragal State':return 'South Antiragal St'
    if k.endswith(' St') and k!='South Antiragal St':return k[:-3]+' State'
    return k
fb={norm(k):v for k,v in tc.items()}
assert all(k in names for k in fb),[k for k in fb if k not in names]
# colour math
def hex2rgb(h):h=h.lstrip('#');return tuple(int(h[i:i+2],16)/255 for i in(0,2,4))
def rgb2hex(r,g,b):return '#%02x%02x%02x'%tuple(round(max(0,min(1,x))*255) for x in(r,g,b))
def lin(c):return c/12.92 if c<=.04045 else((c+.055)/1.055)**2.4
from functools import lru_cache
@lru_cache(None)
def lab(h):
    r,g,b=[lin(x) for x in hex2rgb(h)]
    X=(.4124*r+.3576*g+.1805*b)/.95047;Y=.2126*r+.7152*g+.0722*b;Z=(.0193*r+.1192*g+.9505*b)/1.08883
    f=lambda t:t**(1/3) if t>.008856 else 7.787*t+16/116
    return(116*f(Y)-16,500*(f(X)-f(Y)),200*(f(Y)-f(Z)))
def dE(a,b):return math.dist(lab(a),lab(b))
def lum(h):r,g,b=[lin(x) for x in hex2rgb(h)];return .2126*r+.7152*g+.0722*b
def contrast(a,b):x,y=sorted([lum(a),lum(b)],reverse=True);return(x+.05)/(y+.05)
def hsl(h,s,l):r,g,b=colorsys.hls_to_rgb((h%360)/360,l,s);return rgb2hex(r,g,b)
def hue(hx):r,g,b=hex2rgb(hx);return colorsys.rgb_to_hls(r,g,b)[0]*360
def pd(a,b):return min(dE(a[0],b[0])+dE(a[1],b[1]),dE(a[0],b[1])+dE(a[1],b[0]))
# naming
HN=[(15,'red'),(40,'orange'),(65,'gold'),(95,'lime'),(150,'green'),(185,'teal'),(205,'cyan'),(255,'blue'),(285,'indigo'),(315,'violet'),(345,'magenta'),(361,'red')]
def cname(hx):
    r,g,b=hex2rgb(hx);h,l,s=colorsys.rgb_to_hls(r,g,b);h*=360
    if l>.93:return 'white'
    if l<.1:return 'black'
    if s<.12:return 'silver' if l>.65 else 'charcoal' if l<.35 else 'grey'
    base=next(n for t,n in HN if h<t)
    if base=='orange' and l<.38:base='brown'
    if base=='gold' and l>.8:base='cream'
    if base=='red' and l>.7:base='pink'
    pre='deep ' if l<.28 else 'dark ' if l<.4 else 'light ' if l>.72 else 'bright ' if s>.8 and .45<l<.65 else ''
    if base in('cream','white','black','brown') and pre in('deep ','dark '):pre='dark ' if base=='brown' else ''
    return pre+base
# schemes: returns (primary,secondary,label)
def make(rng):
    sch=rng.choices(['complementary','analogous','split','triadic','neutral','mono','tetrad'],[18,22,14,10,18,10,8])[0]
    h=rng.uniform(0,360);s=rng.uniform(.5,.9);l=rng.uniform(.22,.5)
    p=hsl(h,s,l)
    if sch=='complementary':sec=hsl(h+180+rng.uniform(-12,12),rng.uniform(.55,.95),rng.uniform(.5,.7))
    elif sch=='analogous':d=rng.choice([-1,1])*rng.uniform(28,50);sec=hsl(h+d,rng.uniform(.5,.9),rng.uniform(.55,.78))
    elif sch=='split':d=rng.choice([-1,1])*rng.uniform(140,160);sec=hsl(h+d,rng.uniform(.55,.9),rng.uniform(.5,.72))
    elif sch=='triadic':d=rng.choice([-1,1])*120+rng.uniform(-8,8);sec=hsl(h+d,rng.uniform(.5,.85),rng.uniform(.5,.72))
    elif sch=='tetrad':d=rng.choice([-1,1])*90+rng.uniform(-8,8);sec=hsl(h+d,rng.uniform(.5,.85),rng.uniform(.5,.72))
    elif sch=='mono':sec=hsl(h+rng.uniform(-8,8),rng.uniform(.3,.7),rng.uniform(.78,.9))
    else:
        sec=rng.choice([hsl(h,.12,.93),hsl(h+rng.uniform(-15,15),.1,.8),hsl(40,.35,.9),hsl(h,.3,.12),'#ffffff'])
        if rng.random()<.5:p,sec=sec,p
        if rng.random()<.5:  # dark-neutral primary with a bright accent
            p=hsl(h,.1,.14);sec=hsl(h+rng.uniform(-20,20),rng.uniform(.65,.9),rng.uniform(.5,.62))
    return p,sec,sch
rng=random.Random(2122)
placed=[tuple(v) for v in fb.values()]
out={}
for n,v in fb.items():out[n]={'primary':v[0],'secondary':v[1],'source':'college football'}
todo=sorted([n for n in names if n not in fb])
rng.shuffle(todo)
for n in todo:
    best=None
    for _ in range(120):
        p,s,sc=make(rng)
        if contrast(p,s)<3.0:continue
        if dE(p,s)<30:continue
        sc_=min(pd((p,s),q) for q in placed)
        if best is None or sc_>best[0]:best=(sc_,p,s,sc)
    sc_,p,s,sch=best;placed.append((p,s))
    out[n]={'primary':p,'secondary':s,'source':'new','scheme':sch}
for n,v in out.items():v['names']=[cname(v['primary']),cname(v['secondary'])]
json.dump(out,open('team_colors.json','w'),indent=0,sort_keys=True)
ds=sorted(pd(a,b) for i,a in enumerate(placed) for b in placed[:i])
new=[v for v in out.values() if v['source']=='new']
from collections import Counter
print(len(out),'new',len(new),Counter(v['scheme'] for v in new))
print('closest pair distances',[round(x,1) for x in ds[:8]])
print('contrast min new',round(min(contrast(v['primary'],v['secondary']) for v in new),2))
print(Counter(v['primary'] for v in out.values()).most_common(3))
