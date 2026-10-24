"""Show one matchup under the old (blind) model and the new (scouting) model."""
import sys, collections, re; sys.path.insert(0,'/home/claude/cfb2')
import season as SE, pbp_engine as E, scouting as SC, subdivision as SUB
SUB.register(E)

def splits(pbp):
    run=pas=0; ry=py=0
    for p in pbp:
        if not isinstance(p,dict): continue
        d=p.get('desc',''); m=re.search(r'for (-?\d+)$',d)
        if ' rush for ' in d or ' keeper for ' in d:
            run+=1; ry+=int(m.group(1)) if m else 0
        elif 'complete to' in d:
            pas+=1; py+=int(m.group(1)) if m else 0
        elif 'Pass incomplete' in d: pas+=1
        elif d.startswith('SACK'):
            pas+=1
            mm=re.search(r'for (-?\d+)',d); py+=int(mm.group(1)) if mm else 0
    return run,pas,ry,py

def arm(label, home, away, seed, scouting_on):
    SC.ENABLE.update({"shift":scouting_on,"quick":scouting_on,"commit":scouting_on})
    E.CAL_COMP_BASE = 0.030 if scouting_on else 0.055
    box,pbp = E.simulate_game(home,away,seed,site="home",keep_pbp=True)
    return box, splits([p for p in pbp if isinstance(p,dict)])

def show(home, away, seed, note):
    print("="*78); print("%s   —   %s at %s   (seed %d)"%(note,away,home,seed)); print("="*78)
    # the reads the new model makes
    SC.ENABLE.update({"shift":True,"quick":True,"commit":True}); E.CAL_COMP_BASE=0.030
    import random
    rng=random.Random(seed)
    H=E.TeamGame(home,rng); A=E.TeamGame(away,rng)
    offs={home:E.COACHES[home]['off_scheme'],away:E.COACHES[away]['off_scheme']}
    defs={home:E.COACHES[home]['def_scheme'],away:E.COACHES[away]['def_scheme']}
    sH,sA,iH,iA = SC.build(H,A,offs,defs,E.U['OFF_SCHEMES'],E.U['DEF_SCHEMES'])
    for nm,ident,sc,tg in ((home,iH,sH,H),(away,iA,sA,A)):
        print("  %-20s %-17s / %-17s"%(nm,ident.off_scheme,ident.def_scheme))
        print("      built to            : %s (pass lean %+.2f)"%(
            "throw" if ident.pass_lean>0.05 else ("run" if ident.pass_lean<-0.05 else "balanced"),ident.pass_lean))
        print("      its defence         : front %.2f  coverage %.2f  -> %s"%(
            ident.front,ident.cover,
            "soft against the RUN" if ident.soft_vs_run>0.08 else ("soft against the PASS" if ident.soft_vs_run<-0.08 else "balanced")))
        print("      OC %.1f / DC %.1f    : attack edge %+.2f, read edge %+.2f"%(
            tg.oc_skill,tg.dc_skill,sc.off_edge,sc.def_edge))
        print("      game plan           : pass shift %+.3f%s | defence commits %+.2f (%s)"%(
            sc.plan_pass_shift," (quick game vs blitz)" if sc.quick_game else "",
            sc.commit,"toward the pass" if sc.commit>0.1 else ("toward the run" if sc.commit<-0.1 else "balanced")))
    print()
    for label,on in (("OLD  (blind)",False),("NEW  (scouting)",True)):
        box,(r,p,ry,py)=arm(label,home,away,seed,on)
        tot=r+p
        print("  %-16s %s %2d - %2d %s   | %s ran %d (%.1f/c) threw %d (%.1f/a)  pass rate %.0f%%"%(
            label,home,box['home_score'],box['away_score'],away,
            "both", r,ry/max(1,r),p,py/max(1,p),100*p/max(1,tot)))
    print()

if __name__=="__main__":
    show("Ranroman State","Ciarralotta",4242001,"MISMATCH: champion vs 1-11")
    show("Orlot","Kaji Daun",4242002,"EVEN: two good teams")
