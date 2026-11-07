//<engine>
const N=SC.length, NC_=CF.length;
const DAY0=Date.UTC(2021,10,1), NDAYS=126, CONF0=63, NC_END=62, TN_COUNT=30;
const DOW=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'], MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const CONF_ON=false; // conference games are switched off for now
const BLK=new Set([53,54]);
function dparts(d){const t=new Date(DAY0+d*864e5);return{dow:t.getUTCDay(),m:t.getUTCMonth(),dm:t.getUTCDate(),y:t.getUTCFullYear()}}
function dlabel(d){const t=dparts(d);return DOW[t.dow]+' '+MON[t.m]+' '+t.dm}
function dshort(d){const t=dparts(d);return MON[t.m]+' '+t.dm}
const CONFM=CF.map(()=>[]);SC.forEach(s=>CONFM[s.c].push(s.i));
const DIST=SC.map(a=>Float32Array.from(SC,b=>3*Math.hypot(a.x-b.x,a.y-b.y)));
// ---- team quality, fan draw, resume
const QV=SC.map(s=>{const m=/^(\d+)-(\d+)/.exec(s.rec||'');const w=m?+m[1]/((+m[1])+(+m[2])||1):.5;return .5*s.prest+.5*w*100+(s.seed>0?3:0)});
const QMEAN=QV.reduce((a,b)=>a+b,0)/QV.length, QCUT=QV.slice().sort((a,b)=>b-a)[67];
const QRANK=(()=>{const o=QV.map((v,i)=>i).sort((a,b)=>QV[b]-QV[a]),r=new Int16Array(QV.length);o.forEach((i,k)=>r[i]=k+1);return r})();
function winProb(i,o,v){return 1/(1+Math.exp(-((QV[i]-QV[o])+(v==='H'?4:v==='A'?-4:0))/10))}
// what makes a crowd: opponent name, same state, short trip for fans, last year's seed, banners, and the day of the week
function drawParts(h,a,d){const A=SC[a],H=SC[h],D=DIST[h][a],P={};
 P.name=-.25+.5*A.prest/100;
 P.state=H.st===A.st?.30:0;
 P.near=D<=100?.15:D<=250?.08:0;
 P.seed=A.seed>0?(A.seed<=4?.15:A.seed<=8?.10:.05):0;
 P.title=A.ti>0?.05:0;
 P.day=0;if(d!=null&&d>=0){const w=dparts(d).dow;P.day=w===6?.10:(w===5||w===0)?.03:(w===2||w===3)?-.06:0;if(d>=49)P.day-=.12}
 return P}
function drawMult(h,a,d){const P=drawParts(h,a,d);return Math.max(.5,1+P.name+P.state+P.near+P.seed+P.title+P.day)}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function shuf(a,r){for(let i=a.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
const TIERS=['Hurting','Tight','Middling','Comfortable','Flush'];
const STY={
 host:{n:'Buy-game host',d:'Hosts most of its non-conference games and pays smaller schools to visit.',home:.85,tw:.15},
 earn:{n:'Road for pay',d:'Takes road buy games at bigger schools to bring money home.',home:.2,tw:.6},
 chase:{n:'Tournament chaser',d:'Wants a spot in an early-season tournament and plays an even home and road mix.',home:.5,tw:1},
 near:{n:'Close to home',d:'Keeps non-conference trips short and plays nearby schools.',home:.5,tw:.7},
 swap:{n:'Home-and-home',d:'Trades home dates with schools of similar standing.',home:.5,tw:.8},
 sos:{n:'Schedule strengthener',d:'Looks for strong opponents to help its résumé.',home:.4,tw:.9}
};
const GATE=[.20,.30,.45,.65,.90], NEED=[3.9,4.0,5.2,7.4,10.2], STIP=.25, TRV=.05;
function hash(i){return ((i+1)*2654435761>>>0)%100}
function defStyle(t,i){const h=hash(i);
 if(t===4)return h<60?'host':'sos';
 if(t===3)return h<35?'swap':h<65?'sos':'chase';
 if(t===2)return h<40?'chase':h<75?'near':'swap';
 if(t===1)return h<45?'near':h<85?'earn':'chase';
 return h<80?'earn':'near'}
let S=null; // state
const X={}; // derived index
function newState(){return{v:1,tl:0,g:[],tn:Array.from({length:TN_COUNT},()=>({n:'',na:0,site:-1,sp:0,d:-1,dp:0,t:Array(8).fill(-1),tp:Array(8).fill(0)})),ov:{},cf:{},seed:1}}
function score(i){const s=SC[i],o=S.ov[i]||{};const al=o.alum!=null?o.alum:s.alum;return .4*s.prest+.3*(al-1)/4*100+.2*s.cl+5*(o.bud||0)}
function tierOf(i){const v=score(i);return v<CUTS[0]?0:v<CUTS[1]?1:v<CUTS[2]?2:v<CUTS[3]?3:4}
function styleOf(i){const o=S.ov[i];return(o&&o.style)||defStyle(tierOf(i),i)}
function refresh(){
 X.busy=SC.map(()=>new Set());X.by=SC.map(()=>[]);X.inT=new Int8Array(N).fill(-1);X.nc=new Int16Array(N);X.cc=new Int16Array(N);X.load=new Int16Array(NDAYS+8);
 X.tier=Int8Array.from(SC,(_,i)=>tierOf(i));X.sty=SC.map((_,i)=>styleOf(i));
 X.pairs=new Set();
 for(const g of S.g){X.busy[g.h].add(g.d);X.busy[g.a].add(g.d);X.by[g.h].push(g);X.by[g.a].push(g);X.load[g.d]++;
  if(g.t==='C'){X.cc[g.h]++;X.cc[g.a]++}else{X.nc[g.h]++;X.nc[g.a]++}
  X.pairs.add(g.h<g.a?g.h*1000+g.a:g.a*1000+g.h)}
 S.tn.forEach((T,k)=>T.t.forEach(i=>{if(i>=0){X.inT[i]=k;X.nc[i]+=0;if(T.d>=0)for(let q=0;q<3;q++){X.busy[i].add(T.d+q)}}}));
 S.tn.forEach(T=>{if(T.d>=0)for(let q=0;q<3;q++)X.load[T.d+q]+=T.t.filter(i=>i>=0).length/2})
}
function ncTotal(i){return X.nc[i]+(X.inT[i]>=0?3:0)}
function entries(i){
 const out=[];for(const g of X.by[i])out.push({d:g.d,opp:g.h===i?g.a:g.h,v:g.h===i?'H':'A',t:g.t,g});
 const k=X.inT[i];if(k>=0){const T=S.tn[k];if(T.d>=0){const p=T.t.indexOf(i),q=T.t[p^1];
  out.push({d:T.d,opp:q,v:'N',t:'T',k,r:1},{d:T.d+1,opp:-1,v:'N',t:'T',k,r:2},{d:T.d+2,opp:-1,v:'N',t:'T',k,r:3})}}
 return out.sort((a,b)=>a.d-b.d)}
function isBuy(h,a){return X.tier[h]-X.tier[a]>=2}
// guarantee the host pays the guest: grows with the budget gap, the miles travelled and the guest's drawing power
function feeParts(h,a){return{base:.15+.08*(X.tier[h]-X.tier[a]),trav:.0003*DIST[h][a],draw:.004*SC[a].prest}}
function fee(h,a){const p=feeParts(h,a);return p.base+p.trav+p.draw}
function money(i){
 const E=entries(i),t=X.tier[i];let gate=0,feeIn=0,feeOut=0,trav=0,stip=0;
 for(const e of E){
  if(e.t==='T'){if(e.r===1){stip+=STIP;const T=S.tn[e.k];if(T.site>=0){const c=CITY[T.site];trav-=TRV*3*Math.hypot(SC[i].x-c[2],SC[i].y-c[3])/100}}continue}
  if(e.v==='H'){gate+=GATE[t]*drawMult(i,e.opp,e.d);if(e.t==='N'&&isBuy(i,e.opp))feeOut+=fee(i,e.opp)}
  else{if(e.t==='N'&&isBuy(e.opp,i))feeIn+=fee(e.opp,i);else trav-=TRV*DIST[i][e.opp]/100}}
 if(!CONF_ON){gate+=9*GATE[t];trav-=9*TRV*2.5}
 const tot=gate+feeIn-feeOut+trav+stip;
 return{gate,feeIn,feeOut,trav,stip,tot,need:NEED[t]}}
function sosOf(i){const q=[];for(const e of entries(i)){if(e.t==='T'){if(e.r===1){const T=S.tn[e.k],f=T.t.filter(x=>x>=0&&x!==i);if(f.length){const a=f.reduce((s,x)=>s+QV[x],0)/f.length;q.push(a,a,a)}}}else if(e.opp>=0)q.push(QV[e.opp])}
 return{n:q.length,avg:q.length?q.reduce((a,b)=>a+b,0)/q.length:0}}
function outlookOf(r){return r>=QCUT+6?3:r>=QCUT-4?2:r>=QCUT-14?1:0}
const OUTL=['Outside the field','Longshot','On the bubble','Safely in'];
function resumeOf(i){const s=sosOf(i);if(s.n<6)return null;return{sos:s.avg,r:QV[i]+1.2*(s.avg-QMEAN),o:outlookOf(QV[i]+1.2*(s.avg-QMEAN)),base:outlookOf(QV[i])}}
// ---- checks
function issues(i){
 const out=[],E=entries(i),nm=n=>SC[n].n;
 if(CONF_ON&&X.cc[i]!==18)out.push({s:X.cc[i]>18?'x':'l',m:`Conference games: ${X.cc[i]} of 18`});
 const nt=ncTotal(i);if(nt!==12)out.push({s:nt>12?'x':'l',m:`Non-conference games: ${nt} of 12`});
 if(nt===12){const m=money(i);if(m.tot<m.need-.3)out.push({s:'l',m:`Budget short by $${(m.need-m.tot).toFixed(2)}M`});const R=resumeOf(i);if(R&&R.o<R.base)out.push({s:'l',m:`Soft schedule: tournament outlook slips to “${OUTL[R.o].toLowerCase()}”`})}
 const k=X.inT[i];if(k>=0&&S.tn[k].d<0)out.push({s:'l',m:'Tournament date not set'});
 const seen=new Map();E.forEach(e=>{seen.set(e.d,(seen.get(e.d)||0)+1)});
 for(const[d,c]of seen)if(c>1)out.push({s:'x',m:`Two games on ${dlabel(d)}`});
 E.forEach(e=>{if(BLK.has(e.d))out.push({s:'x',m:`Game on ${dlabel(e.d)} (holiday)`})});
 const tg=E.map((e,ix)=>e.t==='T'?ix:-1).filter(x=>x>=0);
 if(tg.length&&tg[tg.length-1]>=12)out.push({s:'x',m:'Tournament runs past the first 12 games'});
 const cs=CONF_ON?E.filter(e=>e.t==='C'):[];let run=0,last='',bad=0;for(const e of cs){if(e.v===last)run++;else{run=1;last=e.v}if(run===4)bad++}
 if(bad)out.push({s:'x',m:`Conference home/away streak longer than 3 (${bad}×)`});
 const ncOpp=new Map();E.forEach(e=>{if(e.t==='N'){ncOpp.set(e.opp,(ncOpp.get(e.opp)||0)+1);if(SC[e.opp].c===SC[i].c)out.push({s:'x',m:`Non-conference game vs conference mate ${nm(e.opp)}`})}});
 E.forEach(e=>{if(e.t==='N'&&e.opp>=0&&k>=0&&X.inT[e.opp]===k)out.push({s:'x',m:`Plays ${nm(e.opp)} in a game and in the same tournament`})});
 for(const[o,c]of ncOpp)if(c>1)out.push({s:'l',m:`Plays ${nm(o)} ${c} times outside the conference`});
 const cOpp=new Map();E.forEach(e=>{if(CONF_ON&&e.t==='C'){cOpp.set(e.opp,(cOpp.get(e.opp)||0)+1)}});
 for(const[o,c]of cOpp)if(c>2)out.push({s:'x',m:`Plays ${nm(o)} ${c} times in conference`});
 let b2=0;for(let q=1;q<E.length;q++)if(E[q].d-E[q-1].d===1&&!(E[q].t==='T'&&E[q-1].t==='T'&&E[q].k===E[q-1].k))b2++;
 if(b2>2)out.push({s:'l',m:`${b2} back-to-back days`});
 return out}
function tnIssues(k){const T=S.tn[k],out=[],f=T.t.filter(i=>i>=0);
 if(f.length<8)out.push({s:'l',m:`${f.length} of 8 teams`});if(T.d<0)out.push({s:'l',m:'No date'});if(T.site<0)out.push({s:'l',m:'No host city'});
 const cc={};f.forEach(i=>cc[SC[i].c]=(cc[SC[i].c]||0)+1);for(const c in cc)if(cc[c]>2)out.push({s:'l',m:`${cc[c]} teams from ${CF[c].name}`});
 for(const i of f)for(const g of X.by[i])if(g.t==='N'){const o=g.h===i?g.a:g.h;if(o>i&&f.includes(o))out.push({s:'x',m:`${SC[i].n} and ${SC[o].n} already have a game`})}
 if(T.d>=0)for(const i of f)for(const d of[T.d,T.d+1,T.d+2])if(X.by[i].some(g=>g.d===d)){out.push({s:'x',m:`${SC[i].n} already has a game that weekend`});break}
 return out}
function progress(){let have=0;if(!CONF_ON){for(let i=0;i<N;i++)have+=Math.min(12,ncTotal(i));return have/(N*12)}for(let i=0;i<N;i++)have+=Math.min(18,X.cc[i])+Math.min(12,ncTotal(i));return have/(N*30)}
// ---- conference schedules
const CP=[[1,5],[2,5],[3,6],[1,4],[2,6],[3,5],[0,5]];
function confPlan(ci,seed){
 const mem=CONFM[ci],n=mem.length,r=mulberry32(seed*7919+ci*104729+13),base=n-1,D=Math.max(0,Math.min(base,18-base));
 let best=null;
 for(let t=0;t<250;t++){
  const p=shuf(mem.slice(),r),q=p.slice(1),m=q.length,R=[];
  for(let k=0;k<m;k++){const pr=[[p[0],q[k]]];for(let j=1;j<n/2;j++)pr.push([q[(k+j)%m],q[(k-j+m)%m]]);R.push(pr)}
  const cost=R.map(pr=>pr.reduce((s,[a,b])=>s+DIST[a][b],0)),ord=cost.map((c,i)=>i).sort((a,b)=>cost[a]-cost[b]);
  const dbl=ord.slice(0,D),tot=dbl.reduce((s,i)=>s+cost[i],0);
  if(!best||tot<best.tot)best={R,dbl,tot}}
 const items=[];for(let k=0;k<base;k++)items.push(k);best.dbl.forEach(k=>items.push(k));
 while(items.length<18)items.push(items[items.length%base]);
 let seq=null;
 for(let t=0;t<400;t++){const s=shuf(items.slice(),r);const last={};let ok=true;s.forEach((x,i)=>{if(x in last&&i-last[x]<4)ok=false;last[x]=i});seq=s;if(ok)break}
 const gm=[],seen=new Map();
 seq.forEach((x,pos)=>best.R[x].forEach(([a,b])=>{const key=a<b?a+'_'+b:b+'_'+a;const sec=seen.has(key);if(!sec)seen.set(key,seen.size);gm.push({pos,a,b,k:seen.get(key),sec})}));
 const tg={};gm.forEach((g,ix)=>{(tg[g.a]=tg[g.a]||[]).push(ix);(tg[g.b]=tg[g.b]||[]).push(ix)});
 const keyTeams=[];gm.forEach(g=>{if(!g.sec)keyTeams[g.k]=[g.a,g.b]});
 function homeOf(g,bits){const f=bits[g.k]?g.a:g.b,o=bits[g.k]?g.b:g.a;return g.sec?o:f}
 function tc(t,bits){let run=0,last=-1,pen=0,h=0;for(const ix of tg[t]){const g=gm[ix],H=homeOf(g,bits)===t?1:0;h+=H;if(H===last)run++;else{run=1;last=H}if(run>3)pen+=60;else if(run===3)pen+=1}return pen+Math.abs(h-9)*4}
 let bestBits=null,bestCost=1e9;
 for(let att=0;att<6&&bestCost>=60;att++){
  const bits=Uint8Array.from({length:seen.size},()=>r()<.5?1:0);
  let cur=0;for(const t of mem)cur+=tc(t,bits);
  for(let it=0;it<5000;it++){const T=1.8*(1-it/5000)+.05,k=Math.floor(r()*seen.size),[a,b]=keyTeams[k];
   const before=tc(a,bits)+tc(b,bits);bits[k]^=1;const after=tc(a,bits)+tc(b,bits),dl=after-before;
   if(dl<=0||r()<Math.exp(-dl/T))cur+=dl;else bits[k]^=1}
  if(cur<bestCost){bestCost=cur;bestBits=bits.slice()}}
 return{gm,bits:bestBits,homeOf,cost:bestCost,doubles:best.dbl.length}}
function dayOfRound(ci,pos){return CONF0+7*(pos>>1)+CP[ci%CP.length][pos&1]}
function placeConf(ci,seed){
 const pl=confPlan(ci,seed),byPos={};pl.gm.forEach(g=>(byPos[g.pos]=byPos[g.pos]||[]).push(g));
 let made=0;
 for(let pos=0;pos<18;pos++){const gs=byPos[pos];if(!gs)continue;let day=-1;const t0=dayOfRound(ci,pos);
  for(const off of[0,1,-1,2,-2,3,-3,4,-4]){const d=t0+off;if(d<CONF0||d>=NDAYS||BLK.has(d))continue;
   if(gs.every(g=>!X.busy[g.a].has(d)&&!X.busy[g.b].has(d))){day=d;break}}
  if(day<0)continue;
  for(const g of gs){const h=pl.homeOf(g,pl.bits),a=h===g.a?g.b:g.a;S.g.push({d:day,h,a,t:'C',p:0});X.busy[h].add(day);X.busy[a].add(day);made++}}
 return made}
// ---- tournaments
const SUF=['Classic','Invitational','Showcase','Shootout','Challenge','Tip-Off','Hardwood Classic','Festival','Tournament','Cup'];
const WINS=[23,18,25,32,11,39,4,46,50],WCAP=[4,4,4,4,3,3,3,3,2];
function kmeans(pts,k,r){let c=shuf(pts.slice(),r).slice(0,k).map(p=>[p[0],p[1]]);
 for(let it=0;it<25;it++){const sum=c.map(()=>[0,0,0]);for(const p of pts){let b=0,bd=1e9;c.forEach((q,j)=>{const d=(p[0]-q[0])**2+(p[1]-q[1])**2;if(d<bd){bd=d;b=j}});sum[b][0]+=p[0];sum[b][1]+=p[1];sum[b][2]++}
  c=c.map((q,j)=>sum[j][2]?[sum[j][0]/sum[j][2],sum[j][1]/sum[j][2]]:q)}return c}
function autoTournaments(seed){
 const r=mulberry32(seed*131+5);
 // sites
 const unsited=S.tn.map((T,k)=>T.site<0?k:-1).filter(k=>k>=0);
 if(unsited.length){const used=new Set(S.tn.map(T=>T.site).filter(s=>s>=0));
  const cs=kmeans(SC.map(s=>[s.x,s.y]),unsited.length,r);
  cs.forEach((c,j)=>{let b=-1,bd=1e9;CITY.forEach((q,ix)=>{if(used.has(ix))return;const d=(q[2]-c[0])**2+(q[3]-c[1])**2;if(d<bd){bd=d;b=ix}});if(b>=0){used.add(b);S.tn[unsited[j]].site=b}else S.tn[unsited[j]].site=Math.floor(r()*CITY.length)})}
 // teams
 const pool=[];for(let i=0;i<N;i++)if(X.inT[i]<0)pool.push(i);
 const slots=S.tn.map(T=>T.t.filter(i=>i<0).length);
 const confCnt=S.tn.map(T=>{const o={};T.t.forEach(i=>{if(i>=0)o[SC[i].c]=(o[SC[i].c]||0)+1});return o});
 const pairs=[];
 for(const i of pool){const mult=1/(STY[X.sty[i]].tw+.05);
  S.tn.forEach((T,k)=>{if(!slots[k]||T.site<0)return;const c=CITY[T.site];const d=3*Math.hypot(SC[i].x-c[2],SC[i].y-c[3]);pairs.push([d*mult*(1+.15*r()),i,k])})}
 pairs.sort((a,b)=>a[0]-b[0]);const taken=new Set();
 for(const relax of[0,1]){for(const[,i,k]of pairs){if(taken.has(i)||!slots[k])continue;const c=SC[i].c;if(!relax&&(confCnt[k][c]||0)>=2)continue;
   const T=S.tn[k],p=T.t.indexOf(-1);T.t[p]=i;T.tp[p]=0;slots[k]--;confCnt[k][c]=(confCnt[k][c]||0)+1;taken.add(i)}}
 // dates
 const wuse=WINS.map(()=>0),todo=S.tn.map((T,k)=>T.d<0?k:-1).filter(k=>k>=0);
 S.tn.forEach(T=>{if(T.d>=0){const w=WINS.indexOf(T.d);if(w>=0)wuse[w]++}});
 const avg=k=>{const f=S.tn[k].t.filter(i=>i>=0);return f.length?f.reduce((s,i)=>s+SC[i].prest,0)/f.length:0};
 todo.sort((a,b)=>avg(b)-avg(a));
 for(const k of todo){const T=S.tn[k],f=T.t.filter(i=>i>=0);let done=false;
  for(let w=0;w<WINS.length&&!done;w++){if(wuse[w]>=WCAP[w])continue;const d=WINS[w];
   if(f.every(i=>[d,d+1,d+2].every(x=>!X.by[i].some(g=>g.d===x)))){T.d=d;wuse[w]++;done=true}}
  if(!done){for(let w=0;w<WINS.length&&!done;w++){const d=WINS[w];if(f.every(i=>[d,d+1,d+2].every(x=>!X.by[i].some(g=>g.d===x)))){T.d=d;done=true}}}}
 // names
 const names=new Set(S.tn.map(T=>T.n).filter(Boolean));let si=0;
 S.tn.forEach((T,k)=>{if(!T.n&&T.site>=0){let nm;let tries=0;do{nm=CITY[T.site][0]+' '+SUF[(si++ +k)%SUF.length];tries++}while(names.has(nm)&&tries<20);names.add(nm);T.n=nm;T.na=1}})
}
// ---- non-conference games
function fillNoncon(seed){
 const r=mulberry32(seed*31+7);
 const need=new Int16Array(N),hT=new Int16Array(N);
 for(let i=0;i<N;i++){need[i]=Math.max(0,12-ncTotal(i));hT[i]=Math.round(need[i]*STY[X.sty[i]].home)}
 const flex=i=>['near','swap','chase','sos'].includes(X.sty[i]);
 let tH=0,tR=0;for(let i=0;i<N;i++){tH+=hT[i];tR+=need[i]-hT[i]}
 const ord=shuf([...Array(N).keys()],r);
 let guard=0;while(tH!==tR&&guard++<5000){
  if(tH>tR){const i=ord[guard%N];if(hT[i]>0&&(flex(i)||guard>2000)){hT[i]--;tH--;tR++}}
  else{const i=ord[guard%N];if(need[i]-hT[i]>0&&(flex(i)||guard>2000)){hT[i]++;tH++;tR--}}}
 const hL=Int16Array.from(hT),rL=Int16Array.from(need.map((n,i)=>n-hT[i]));
 const played=new Set(X.pairs),newG=[];
 const key=(a,b)=>a<b?a*1000+b:b*1000+a;
 S.tn.forEach(T=>{const f=T.t.filter(i=>i>=0);for(const a of f)for(const b of f)if(a<b)played.add(key(a,b))}); // tournament mates never meet again
 const prest=SC.map(s=>s.prest),tier=X.tier;
 function sc(a,b){ // a home, b road
  const d=DIST[a][b],sa=X.sty[a],sb=X.sty[b],g=tier[a]-tier[b];let s=r()*1.2;
  s-=(sa==='near'||sb==='near')?d/45:d/380;
  if(sa==='host'||sb==='earn'){s+=g>=2?3.5:g>=0?.5:-2}
  if(sa==='sos')s+=prest[b]/35;if(sb==='sos')s+=prest[a]/35;
  if(sa==='swap'||sb==='swap')s-=Math.abs(g)*1.4;
  if(sa==='chase'||sb==='chase'||sa==='near'||sb==='near')s-=Math.abs(g)*.5;
  if(g>=2&&!(sa==='host'||sb==='earn'))s-=1;
  if(g<=-2)s-=2.5;
  return s}
 let progress=true;
 while(progress){progress=false;
  for(const a of shuf([...Array(N).keys()],r)){if(hL[a]<=0)continue;
   let best=-1,bs=-1e9;
   for(let b=0;b<N;b++){if(rL[b]<=0||b===a||SC[b].c===SC[a].c||played.has(key(a,b)))continue;const s=sc(a,b);if(s>bs){bs=s;best=b}}
   if(best<0)continue;hL[a]--;rL[best]--;played.add(key(a,best));newG.push({h:a,a:best});progress=true}}
 // repair leftovers by swapping
 for(let pass=0;pass<4000;pass++){
  const A=[],B=[];for(let i=0;i<N;i++){if(hL[i]>0)A.push(i);if(rL[i]>0)B.push(i)}
  if(!A.length&&!B.length)break;
  if(A.length&&B.length){let ok=false;for(const a of A){for(const b of B){if(a!==b&&SC[a].c!==SC[b].c&&!played.has(key(a,b))){hL[a]--;rL[b]--;played.add(key(a,b));newG.push({h:a,a:b});ok=true;break}}if(ok)break}if(ok)continue}
  const ix=Math.floor(r()*newG.length),g=newG[ix];if(!g)break;
  if(A.length){const a=A[Math.floor(r()*A.length)];const x=g.h,y=g.a; // a home vs y, and x needs another road... x had home stub: x home stub now free -> becomes leftover home. net: a's stub used, x's freed
   if(a!==y&&SC[a].c!==SC[y].c&&!played.has(key(a,y))){played.delete(key(x,y));played.add(key(a,y));g.h=a;hL[a]--;hL[x]++}}
  else{const b=B[Math.floor(r()*B.length)];const x=g.h,y=g.a;
   if(b!==x&&SC[b].c!==SC[x].c&&!played.has(key(x,b))){played.delete(key(x,y));played.add(key(x,b));g.a=b;rL[b]--;rL[y]++}}}
 // days
 const days=[];for(let d=0;d<=NC_END;d++)if(!BLK.has(d)&&d!==24)days.push(d);
 const load=Int16Array.from(X.load),dn=0;
 let placed=0;
 for(const g of shuf(newG,r)){
  let bd=-1,bs=1e9;
  for(const d of days){if(X.busy[g.h].has(d)||X.busy[g.a].has(d))continue;let s=load[d]*.6+r()*2.2;
   for(const t of[g.h,g.a]){if(X.busy[t].has(d-1)||X.busy[t].has(d+1))s+=7;if(X.busy[t].has(d-2)||X.busy[t].has(d+2))s+=1.6}
   if(s<bs){bs=s;bd=d}}
  if(bd<0)continue;g.d=bd;g.t='N';g.p=0;{const sa=X.sty[g.h],sb=X.sty[g.a];g.r=((sa==='swap'||sb==='swap')&&Math.abs(X.tier[g.h]-X.tier[g.a])<=1)?1:0}S.g.push(g);X.busy[g.h].add(bd);X.busy[g.a].add(bd);load[bd]++;X.by[g.h].push(g);X.by[g.a].push(g);X.nc[g.h]++;X.nc[g.a]++;placed++}
 return placed}
// seed every full tournament by last year's strength, with noise so first rounds stay interesting
function reseedTn(seed){let n=0;const ORD=[0,7,3,4,2,5,1,6]; // seeds 1v8, 4v5, 3v6, 2v7
 S.tn.forEach((T,k)=>{const f=T.t.map((i,p)=>({i,p:T.tp[p]})).filter(x=>x.i>=0);if(f.length<8)return;
  const r=mulberry32(seed*131+k*7+3);let pick=null;
  for(let a=0;a<120&&!pick;a++){const o=f.map(x=>({x,v:QV[x.i]+(r()+r()+r()-1.5)*8})).sort((p,q)=>q.v-p.v).map(z=>z.x);
   const slots=Array(8);ORD.forEach((si,rank)=>{slots[si]=o[rank]});
   let ok=true;for(let q=0;q<8;q+=2)if(SC[slots[q].i].c===SC[slots[q+1].i].c)ok=false;
   if(ok||a===119)pick=slots}
  T.t=pick.map(x=>x.i);T.tp=pick.map(x=>x.p);n++});
 return n}
function clearAuto(){
 S.g=S.g.filter(g=>g.p);
 if(!S.tl)S.tn.forEach(T=>{T.t.forEach((i,p)=>{if(i>=0&&!T.tp[p]){T.t[p]=-1}});if(!T.dp)T.d=-1;if(!T.sp){T.site=-1;if(T.na){T.n='';T.na=0}}});
 }
function completeAll(){
 const seed=S.seed;refresh();
 for(let ci=0;CONF_ON&&ci<NC_;ci++){if(!S.g.some(g=>g.t==='C'&&SC[g.h].c===ci)){placeConf(ci,seed+(S.cf[ci]?S.cf[ci].s||0:0))}}
 refresh();if(!S.tl){autoTournaments(seed);refresh()}fillNoncon(seed);refresh()}
function reroll(){S.seed=(S.seed||1)+1;clearAuto();refresh();completeAll()}
//</engine>
