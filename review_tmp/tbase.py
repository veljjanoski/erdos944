"""Compare cegar944b's exact base CNF (captured at first solve) against an independent split-feasibility test."""
import sys, itertools, time; sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
import cegar944b
from pysat.solvers import Cadical153 as Real
from c944 import cayley
from search944 import group_by_name, sym_closure_candidates

class Stop(Exception): pass
class Rec:
    def __init__(self): self.cl=[]
    def add_clause(self, c): self.cl.append(list(c))
    def solve(self, *a, **k):
        global CAPT; CAPT=self.cl; raise Stop()
cegar944b.Cadical153 = Rec

def indep(G, S, r):
    e=G.e; n=G.n; nn,E=cayley(G,S)
    var=lambda v,c: 3*v+c+1
    s=Real()
    for v in range(n):
        if v!=e:
            s.add_clause([var(v,c) for c in range(3)])
            for c1 in range(3):
                for c2 in range(c1+1,3): s.add_clause([-var(v,c1),-var(v,c2)])
    for u,v in E:
        if e in (u,v): continue
        for c in range(3): s.add_clause([-var(u,c),-var(v,c)])
    pats=0
    while s.solve():
        m=set(l for l in s.get_model() if l>0)
        pat=[next(c for c in range(3) if var(t,c) in m) for t in S]
        pats+=1
        if min(pat.count(c) for c in range(3))>=r+1: s.delete(); return True, pats
        s.add_clause([-var(t,c) for t,c in zip(S,pat)])
    s.delete(); return False, pats

def check(spec, r, dmin, dmax):
    G=group_by_name(spec); atoms=sym_closure_candidates(G)
    try: cegar944b.run(spec, r, dmin, dmax)
    except Stop: pass
    cl=CAPT; A=len(atoms)
    sol=Real(bootstrap_with=cl)
    tot=agree=0; nfeas=0; mism=[]
    t0=time.time()
    for k in range(1,A+1):
        for combo in itertools.combinations(range(A),k):
            d=sum(len(atoms[a]) for a in combo)
            if d<dmin or d>dmax: continue
            S=sorted(set().union(*[atoms[a] for a in combo]))
            ass=[(a+1) if a in combo else -(a+1) for a in range(A)]
            got=sol.solve(assumptions=ass)
            want,_=indep(G,S,r)
            tot+=1; nfeas+=want
            if got==want: agree+=1
            else: mism.append((S,got,want))
    print(f"{spec} r={r} [{dmin},{dmax}]: {tot} sets, base-CNF agrees on {agree}, split-feasible {nfeas}, mismatches {mism[:3]} {time.time()-t0:.0f}s", flush=True)

for spec,r,a,b in [("Z13",1,6,6),("Z16",2,9,12),("Z18",2,9,12),("D12",2,9,12),("Z2xZ12",1,6,6),("Z3x|2Z8",1,6,6),("Z7x|6Z2",0,3,6),("Z16",0,3,6),("Z16",1,5,8),("A4xZ2",2,9,10),("Dic6",2,9,10),("S4",2,9,10),("Z20",1,6,8)]:
    check(spec,r,a,b)
