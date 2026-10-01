import sys, random, time; sys.path.insert(0, r"C:\Users\danie\Math\erdos944"); sys.path.insert(0, r"C:\Users\danie\Math\erdos944\review_tmp")
import tbase
from tbase import *
random.seed(7)
def sample(spec, r, dmin, dmax, N):
    G=group_by_name(spec); atoms=sym_closure_candidates(G); A=len(atoms)
    try: cegar944b.run(spec, r, dmin, dmax)
    except Stop: pass
    sol=Real(bootstrap_with=tbase.CAPT)
    tot=agree=nf=0; mism=[]; t0=time.time()
    while tot<N:
        order=list(range(A)); random.shuffle(order); combo=[]; d=0; target=random.randint(dmin,dmax)
        for a in order:
            if d+len(atoms[a])<=target: combo.append(a); d+=len(atoms[a])
        if d<dmin: continue
        S=sorted(set().union(*[atoms[a] for a in combo]))
        got=sol.solve(assumptions=[(a+1) if a in combo else -(a+1) for a in range(A)])
        want,_=indep(G,S,r); tot+=1; nf+=want; agree+=(got==want)
        if got!=want: mism.append(S)
    print(f"{spec} r={r} [{dmin},{dmax}] random {tot}: agree {agree}, split-feasible {nf}, mism {mism[:2]} {time.time()-t0:.0f}s", flush=True)
sample("A5",2,9,12,300)
sample("S4xZ2",2,9,12,300)
sample("Z5x|2Z12",2,9,12,300)
sample("S4xZ2",1,6,8,300)
