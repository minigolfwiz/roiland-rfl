"""Text record of every draft pick for the pro-league conversation (Dan, 2040 postseason).
Part I: the real drafts (210 picks each) plus the 70 supplementary picks per class that bring them to 280
        (reconstructed from pre-draft roster snapshots for 2037-40; invented for 2036).
Part II: what survives of 2026-34, the shape of the real drafts, survival math, rebuild directions.
Output: state/draft_record_sim_era.txt"""
import sys,pickle,json,collections,statistics; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, committee as CM
s=SE.load_state(); U=E.U; h=s['history']
TC=lambda t: U['team_conf'].get(t,'Subdivision')
TR=lambda t: U['tiers'].get(TC(t),'Guest')
supp=pickle.load(open('/home/claude/cfb2/state/draft_supplementary_s10_s14.pkl','rb'))
back={'draft_s11':'pre_s11_draft','draft_s12':'pre_s13_draft','draft_s13':'pre_s14_draft','draft_s14':'pre_s15_draft'}
cache={}
def roster_map(b):
    if b not in cache:
        R=pickle.load(open('/home/claude/cfb2/state/rosters.pkl.'+b,'rb')); cache[b]={p['pid']:p for t in R.values() for p in t}
    return cache[b]
out=[]; w=out.append
w("ROILAND COLLEGE FOOTBALL -- COMPLETE DRAFT RECORD, SIM ERA (five drafts, 280 players each = 1,400)")
w("Prepared for building a 40-team professional league. Everything below is canon from the sim's own database unless marked INVENTED.")
w("")
w("== CONTEXT ==")
w("- Roiland is a fictional nation of 36 states. Roiland CFB has 152 top-division programmes in 12 conferences: six Power (P6) --")
w("  Power North, Jyras Bay, Great Fourteen, Western Coast, Broad South, Mountain Valley -- and six Lower (L6) -- Vapor Stream, Low Sixteen,")
w("  Brass Belt, East Forest, Evening Star, Southwestern. 217 subdivision ('guest') schools exist below them; a few are drafted each year.")
w("- Season numbering: season N = calendar year 2025+N (season 15 = 2040). The sim's history was reset after the 2035 season (season 10);")
w("  only drafts since then are on record. Each draft is held in the spring after the listed season; the first pick of the 'after 2035' draft")
w("  joined the pros for 2036. The sixth draft (after the 2040 season) has NOT yet been run; it will be the first run natively at 280.")
w("- DRAFT SIZE (Dan's ruling, 2040 postseason): every draft is 280 players, 7 rounds x 40 teams. The college sim drafted 210 (7 x 30) in")
w("  2036-40 as a placeholder, so each of those five classes carries 70 SUPPLEMENTARY picks (overall 211-280) to bring it to 280:")
w("    * 2037, 2038, 2039, 2040: reconstructed from the pre-draft roster snapshots -- the 70 best undrafted players who actually left")
w("      college that spring, ordered by the draft's own grading formula (ability + production, standardised by position) with a small")
w("      seeded jitter. These are real sim players with real colleges and stats.")
w("    * 2036: INVENTED. No roster snapshot survives from before the 2036 draft, so the 70 are new names with colleges weighted by prestige")
w("      and that year's real draft; their ratings are plausible, not recorded. Marked INV in the pid.")
w("  In a 7 x 40 board, overall pick N sits in round ceil(N/40), slot ((N-1) mod 40)+1 -- the original 210 keep their real round/pick labels.")
w("- Eligibility: Sr/RS5 are out of eligibility; Jr/RS4 marked 'early' declared early. (RS = redshirt. A 2037-39 quirk flagged redshirts as")
w("  leaving college, so a few RS appear among the supplementary picks of those years -- they did leave the sim.) Class = college class at draft.")
w("- Positions: QB RB WR TE OL DL LB CB S K P (ATH on a few guest-school picks). Names are gender-mixed by design (women and men play together).")
w("- Rating fields (sim internals, 1-10): abil = overall ability at draft time; pot = ceiling; dur = durability 0-1 (higher = sturdier);")
w("  arch = play-style archetype; attrs = position sub-ratings (e.g. QB acc/arm/mob). prod = final-season production points (schedule-")
w("  adjusted from the 2040 draft on). Sub-ratings/archetype are only recoverable from roster snapshots; 'n/a' where missing.")
w("- Each pick lists college, conference (tier), the college's home state and nickname. A 36-state coordinate map is at the end of Part I.")
w("- Awards since the reset (basis = regular season + conference finals): Ryskamp Trophy (player of the year), DPOY, FOY, Coach of the Year.")
for y,(c,r) in sorted(h['champ'].items()):
    if y>=2035: w("  %d national champion: %s (runner-up %s)"%(y,c,r))
for y,a in sorted(h['awards'].items()):
    if y>=2035: w("  %d Ryskamp %s (%s) | DPOY %s (%s) | FOY %s (%s) | CoY %s"%(y,a['ryskamp']['name'],a['ryskamp']['team'],a['dpoy']['name'],a['dpoy']['team'],a['foy']['name'],a['foy']['team'],a['coy']))
w("")
HDR="Ovr Rd Pk  Player                     Pos Cls  College              Conference (tier)      State            Nickname        abil pot  dur  arch              attrs                     prod   early"
def row(p,rp,rd,pk,ovr):
    t=p['team']; g=CM.GEO.get(t,{}); conf=TC(t); tier=TR(t)
    st=g.get('state','(guest school)') if conf!='Subdivision' else '(guest school)'
    nick=g.get('mascot','-') if conf!='Subdivision' else '-'
    attrs=rp.get('attrs') or p.get('attrs'); attrs=' '.join('%s %.1f'%(a,b) for a,b in attrs.items()) if attrs else 'n/a'
    pot=rp.get('pot',p.get('pot')); dur=rp.get('dur',p.get('dur')); arch=rp.get('arch') or p.get('arch') or 'n/a'
    prod=p.get('prod'); 
    return "%3d %2s %2d  %-26s %-3s %-3s  %-20s %-22s %-16s %-15s %4.2f %-4s %-4s %-17s %-25s %5s  %s"%(
        ovr,rd,pk,p['name'],p['pos'],p['cls'],t,"%s (%s)"%(conf if conf!='Subdivision' else 'Subdivision','guest' if conf=='Subdivision' else tier),st,nick,
        p['abil'],('%.2f'%pot) if pot is not None else 'n/a',('%.2f'%dur) if dur is not None else 'n/a',arch,attrs,('%.1f'%prod) if prod is not None else 'n/a','Y' if p.get('early') else '')
for n in range(10,15):
    k='draft_s%d'%n; picks=s[k]['picks']; yr=2025+n; sp=supp[k]['picks']
    rm=roster_map(back[k]) if k in back else {}
    allp=picks+sp
    by=collections.Counter(p['pos'] for p in allp)
    w("="*110)
    w("%d DRAFT (held spring %d, after the %d season) -- 280 players: 210 drafted by the college sim + 70 supplementary (%s)"%(yr+1,yr+1,yr,'INVENTED' if k=='draft_s10' else 'reconstructed'))
    w("early entrants %d | positions: %s"%(sum(1 for p in allp if p.get('early')),", ".join("%s %d"%(a,b) for a,b in sorted(by.items(),key=lambda x:-x[1]))))
    w("-"*110); w(HDR)
    for p in picks: w(row(p,rm.get(p['pid'],{}),p['round'],p['pick'],p['overall']))
    w("--- supplementary picks 211-280 (%s) ---"%supp[k]['source'])
    for p in sp:
        ovr=p['overall']; w(row(p,{},(ovr-1)//40+1,(ovr-1)%40+1,ovr))
    w("")
w("="*110)
w("STATES OF ROILAND (36) with map coordinates (x, y; arbitrary units, used for travel distance) and the top-division schools in each:")
bystate={}
for t in U['teams']: bystate.setdefault(CM.GEO[t]['state'],[]).append(t)
for st in sorted(U['state_coords']):
    x,y=U['state_coords'][st]; w("  %-16s (%6.1f, %6.1f)  %s"%(st,x,y,', '.join(sorted(bystate.get(st,[]))) or '(no top-division programme)'))
w("")
w("NAMED CITIES already canon (for pro franchise placement): bowl sites -- "+'; '.join('%s: %s, %s'%(b,c[0],c[1]) for b,c in U['bowls'].items()))
w("conference title-game sites -- "+'; '.join('%s: %s, %s'%(b,c[0],c[1]) for b,c in U['ccg_sites'].items()))
w("national championship sites -- "+'; '.join('%d %s, %s'%(y,c[0],c[1]) for y,c in sorted(U['champ_sites'].items())))
w("")
w("TEAM DIRECTORY (college): "+'; '.join('%s = %s (%s, %s)'%(t,CM.GEO[t]['full_name'],U['team_conf'][t],CM.GEO[t]['state']) for t in sorted(U['teams'])))
# ---------------- PART II ----------------
w(""); w("="*110)
w("PART II -- THE LOST DRAFTS (2027-2035) AND THE PRE-SIM-ERA VETERAN POOL")
w("="*110)
w("Seasons 2026-2034 (sim seasons 1-9) were played, and nine drafts followed them (springs 2027-2035), but the 2035 container reset")
w("destroyed every roster and box score from before the 2035 offseason. No pick, name or college from those nine drafts survives.")
w("What DOES survive for those years is below. Use it to rebuild the nine classes, at 280 each, with NEW NAMES in a new conversation.")
w("")
w("-- What is known, season by season (2026-2034) --")
for y in range(2026,2035):
    c,r=h['champ'][y]; site=U['champ_sites'].get(y)
    semis=[t for t,b in h['book'].items() if y in b.get('semis',[])]
    apps=[t for t,b in h['book'].items() if y in b.get('playoff_app',[]) and t not in (c,r) and t not in semis]
    a=h['awards'].get(y)
    line="  %d: champion %s, runner-up %s, title game at %s, %s"%(y,c,r,site[0],site[1])
    if semis: line+="; semifinalists %s"%', '.join(semis)
    if apps: line+="; other known playoff teams %s"%', '.join(apps)
    w(line)
    if a:
        g=lambda k: a[k]['name']+' ('+a[k]['team']+')' if isinstance(a.get(k),dict) else str(a.get(k))
        w("        awards: POY %s | DPOY %s | FOY %s | CoY %s"%(g('ryskamp'),g('dpoy'),g('foy'),g('coy')))
        if a.get('finalists'):
            w("        finalists: "+'; '.join('%s: %s'%(k,', '.join('%s (%s)'%(x['name'],x['team']) for x in v)) for k,v in a['finalists'].items()))
w("  (2028-2034 award winners are not recorded. The 2026-27 award winners and finalists named above ARE canon and must appear in the")
w("   rebuilt drafts in the class their college year implies -- e.g. Bozena Krupka, QB, Kaji Daun, Jr in 2027 -> the 2028 or 2029 draft.)")
w("")
w("-- Per-programme record in the lost window (2026-2034) and designed prestige (0-100, the strength baseline the universe was built on) --")
w("   Weight each school's share of the rebuilt picks by prestige plus that window's titles / runner-ups / semis / playoff appearances.")
rows=[]
for t in U['teams']:
    b=h['book'].get(t,{}); f=lambda k: [y for y in b.get(k,[]) if 2026<=y<=2034]
    rows.append((t,TC(t),TR(t),U['prestige_designed'].get(t,0),f('titles'),f('runnerup'),f('semis'),f('playoff_app')))
rows.sort(key=lambda r:-r[3])
for t,c,tier,pr,ti,ru,se,ap in rows:
    w("  %-20s %-16s %s  prestige %5.1f  titles %-14s runner-up %-14s semis %-14s playoff apps %s"%(t,c,tier,pr,ti or '-',ru or '-',se or '-',ap or '-'))
w("")
w("-- Shape of the five REAL drafts (2036-2040; the 210 college-sim picks only), to copy when rebuilding --")
allp=[p for n in range(10,15) for p in s['draft_s%d'%n]['picks']]
tier=collections.Counter(TR(p['team']) for p in allp)
w("  tier share of picks: "+', '.join('%s %.0f%%'%(k,100*v/len(allp)) for k,v in tier.items()))
conf=collections.Counter(TC(p['team']) for p in allp)
w("  picks per conference per draft (avg): "+', '.join('%s %.1f'%(k,v/5) for k,v in sorted(conf.items(),key=lambda x:-x[1])))
r1=collections.Counter(TR(p['team']) for p in allp if p['round']==1)
w("  round-one tier share: "+', '.join('%s %d of %d'%(k,v,sum(r1.values())) for k,v in r1.items()))
pos=collections.Counter(p['pos'] for p in allp)
w("  position share: "+', '.join('%s %.1f%%'%(k,100*v/len(allp)) for k,v in sorted(pos.items(),key=lambda x:-x[1])))
cls=collections.Counter(p['cls'] for p in allp)
w("  class share: "+', '.join('%s %.1f%%'%(k,100*v/len(allp)) for k,v in sorted(cls.items(),key=lambda x:-x[1])))
w("  ability (abil) by round, mean / min-max:")
for rd in range(1,8):
    a=[p['abil'] for p in allp if p['round']==rd]; w("     round %d: %.2f  (%.2f-%.2f)"%(rd,statistics.mean(a),min(a),max(a)))
a=[p['abil'] for k in supp for p in supp[k]['picks'] if k!='draft_s10']
w("     supplementary 211-280 (reconstructed 2037-40): %.2f  (%.2f-%.2f)"%(statistics.mean(a),min(a),max(a)))
team=collections.Counter(p['team'] for p in allp)
w("  most-drafted programmes 2036-40: "+', '.join('%s %d'%(t,n) for t,n in team.most_common(15)))
w("  programmes with zero picks in five drafts: %d of 152"%sum(1 for t in U['teams'] if team[t]==0))
w("")
w("-- How many pre-sim-era draftees would still be playing in 2041 --")
w("  Rule of thumb from real pro football (share of a drafted class still on a roster entering its n-th season):")
surv={1:.85,2:.72,3:.58,4:.47,5:.38,6:.30,7:.23,8:.17,9:.12,10:.08,11:.05,12:.03,13:.02,14:.01,15:.005}
w("     "+', '.join('yr%d %.1f%%'%(k,v*100) for k,v in surv.items()))
w("  Applied to the nine lost classes at 280 picks each (2041 is their n-th pro season):")
tot=0
for y in range(2027,2036):
    n=2041-y+1; sv=surv.get(n,0); tot+=round(280*sv)
    w("     %d draft: %2dth pro season in 2041 -> %4.1f%% survive = %3d of 280"%(y,n,sv*100,round(280*sv)))
w("     TOTAL pre-sim-era veterans to invent for 2041: ~%d."%tot)
simtot=sum(round(280*surv[2041-y+1]) for y in range(2036,2041))
w("     For scale: the five recorded classes (280 each) contribute ~%d survivors. A 40-team league at 53 players is 2,120 roster spots,"%simtot)
w("     so the balance (~%d) are undrafted free agents and pre-2027 veterans, inventable with no college-sim constraint."%(2120-simtot-tot))
w("")
w("-- DIRECTIONS TO MYSELF FOR THE NEW CONVERSATION (rebuild the lost drafts + the veteran pool) --")
for line in [
"1. Do this in the PRO-LEAGUE conversation and write its output to that league's own files. Write nothing back into the college sim",
"   (cfb2): the college sim's canon starts at the 2036 draft and must not be contradicted. The pro league owns 2027-2035.",
"2. Build nine classes, 2027-2035, one draft each, 7 rounds x 40 teams = 280 picks. Dan's standing rule: every draft is 280 players.",
"3. Allocate picks to colleges by weight = designed prestige (above) plus bonuses for that window's titles / runner-ups / semis / playoff",
"   appearances, and match the real-draft shape: tier share, conference averages, round-one tier split, position share, class share, and",
"   the abil-by-round ranges printed above (rounds 6-7 and the supplementary band for picks 211-280). Every one of the 152 programmes",
"   should get at least a few picks over nine years; a few guest (subdivision) picks per class are fine -- the real drafts had 2-9 each.",
"4. Names: invent new ones in the Roiland style -- gender-mixed, mixed global origins, one given name and one surname -- and never reuse",
"   a name from Part I. The only names that MUST appear are the 2026-27 award winners and finalists above, in the class their college",
"   year implies (Fr in 2027 -> 2030 or 2031 draft; So -> 2029/30; Jr -> 2028/29; Sr -> 2028).",
"5. Give every player: pid in a new range (9xxxxxx, never colliding with college pids), name, pos, class at draft, college, conference,",
"   state, abil at draft (1-10, inside the round ranges), pot, dur (0.3-0.9), arch, and a birth year (seniors ~22 at draft, early 20-21).",
"6. Apply the survival table to decide who is still active in 2041, oldest classes thinnest. Survival is not random: survivors skew to",
"   higher abil/pot and higher dur, and QB/K/P last longer. Give survivors pro careers (teams, seasons, a peak at 27-29 and decline after",
"   30). Record retired players too, briefly, so the league has a history.",
"7. Fill the remaining spots (53 x 40) with undrafted free agents and pre-2027 veterans invented from scratch, aged 23-36.",
"8. The college sim's 2041 draft (after the 2040 season) has not been run; draft.py is now set to 7 x 40 = 280, so it will be the first",
"   class drafted natively at the pro league's size. Take it from the college sim when that offseason is played.",
"9. Keep the two universes aligned only on: team names, nicknames and states (directory in Part I), the season-year mapping, the position",
"   set, the gender-mixed naming convention and the 36-state map. Everything else about the pro league is new canon."]:
    w(line)
open('/home/claude/cfb2/state/draft_record_sim_era.txt','w').write('\n'.join(out)+'\n')
print(len(out),'lines', sum(len(l) for l in out)//1024,'KB')
