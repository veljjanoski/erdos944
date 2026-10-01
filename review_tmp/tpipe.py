import sys, itertools, time, io, contextlib; sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
import cegar944b
from c944 import cayley, col3_with_bad
from search944 import group_by_name, sym_closure_candidates
def brute(G, r, d):
    atoms=sym_closure_candidates(G); cnt=0
    for k in range(1,len(atoms)+1):
        for combo in itertools.combinations(atoms,k):
            if sum(len(a) for a in combo)!=d: continue
            S=sorted(set().union(*combo)); n,E=cayley(G,S)
            if col3_with_bad(n,E,0,removed_vertex=G.e) is None: continue
            if col3_with_bad(n,E,r) is None: cnt+=1
    return cnt
res=[]; t0=time.time()
for spec in ["Z7","Z8","Z10","Z11","Z13","Z14","Z16","Z17","Z19","D5","D7","D8","A4","Dic3","Z7x|2Z3","Z2xZ8","Z3xZ6","Z5x|2Z4"]:
    G=group_by_name(spec)
    for r in (0,1):
        for d in range(3,9):
            if d>G.n-1: continue
            b=brute(G,r,d)
            buf=io.StringIO()
            with contextlib.redirect_stdout(buf): out=cegar944b.run(spec,r,d,d)
            cv = "NO" if out is None else ("MAXITER" if out=="maxiter" else "WIT")
            ok = (cv=="NO")==(b==0) and cv!="MAXITER"
            res.append((spec,r,d,b,cv,ok))
            if not ok: print("DISAGREE", spec, r, d, "brute", b, "cegar", cv, buf.getvalue()[-300:], flush=True)
print("cases", len(res), "positives", sum(1 for x in res if x[3]>0), "disagreements", sum(1 for x in res if not x[5]), f"{time.time()-t0:.0f}s")
print([x[:5] for x in res if x[3]>0][:40])
