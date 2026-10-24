import sys; sys.path.insert(0,'/home/claude/cfb2')
exec(open('/home/claude/cfb2/parity_audit.py').read().split('out={}')[0])
import math
print("=== E. RIVALRY vs NON-RIVALRY: favourite win % (season-end ratings, FBS v FBS) ===")
for n in SEAS:
    em,_=power_ratings(n); R=[0,0]; N=[0,0]; Rg=[]; Ng=[]
    for w,b in games(n):
        h,a=b['home'],b['away']
        if h in TEAMS and a in TEAMS:
            gap=(em[h]+2.5)-em[a]
            if abs(gap)<7: continue
            fav_won=(b['home_score']>b['away_score'])==(gap>0)
            (R if b.get('rivalry') else N)[0]+=1; (R if b.get('rivalry') else N)[1]+=fav_won
    print(2025+n,'gap>=7: rivalry fav wins %d/%d (%.0f%%) | other %d/%d (%.0f%%)'%(R[1],R[0],100*R[1]/max(1,R[0]),N[1],N[0],100*N[1]/max(1,N[0])))
print("\n=== F. WEEK 14 vs OTHER WEEKS: favourite win % at gap>=7 ===")
for n in SEAS:
    em,_=power_ratings(n); A=[0,0]; B=[0,0]
    for w,b in games(n):
        h,a=b['home'],b['away']
        if h in TEAMS and a in TEAMS:
            gap=(em[h]+2.5)-em[a]
            if abs(gap)<7: continue
            fw=(b['home_score']>b['away_score'])==(gap>0)
            t=A if w==14 else B; t[0]+=1; t[1]+=fw
    print(2025+n,'wk14 %d/%d (%.0f%%) | wk0-13 %d/%d (%.0f%%)'%(A[1],A[0],100*A[1]/max(1,A[0]),B[1],B[0],100*B[1]/max(1,B[0])))
print("\n=== G. WEEK 14: how many games were rivalry games, by season ===")
for n in SEAS:
    g=[b for w,b in games(n) if w==14 and b['home'] in TEAMS and b['away'] in TEAMS]
    print(2025+n,'wk14 FBS games',len(g),'rivalry',sum(1 for b in g if b.get('rivalry')))
print("\n=== H. 2042 weeks 12-14 ranked-vs-unranked upsets: share that were rivalry games ===")
for n in [15,16,17]:
    L=Lr=G=Gr=0
    for w,b in games(n):
        if not 12<=w<=14: continue
        h,a=b['home'],b['away']
        if h not in TEAMS or a not in TEAMS: continue
        rk=set(board(n,w))
        for t,o in ((h,a),(a,h)):
            if t in rk and o not in rk:
                G+=1; Gr+=bool(b.get('rivalry'))
                ts=b['home_score'] if t==h else b['away_score']; os_=b['away_score'] if t==h else b['home_score']
                if ts<os_: L+=1; Lr+=bool(b.get('rivalry'))
    print(2025+n,'ranked-v-unranked games %d (rivalry %d); ranked losses %d (rivalry %d) | loss%% rivalry %.0f%% vs other %.0f%%'%(G,Gr,L,Lr,100*Lr/max(1,Gr),100*(L-Lr)/max(1,G-Gr)))
