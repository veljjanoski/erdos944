import sys
sys.path.insert(0, r"C:\Users\danie\Math\erdos944"); sys.path.insert(0, r"C:\Users\danie\Math\erdos944\review_tmp")
import structcheck
from structcheck import Rec
import cegar944b
from pysat.card import CardEnc as RealCE
from search944 import group_by_name, sym_closure_candidates
log = []
class CE:
    @staticmethod
    def atleast(lits, bound, top_id, encoding):
        c = RealCE.atleast(lits=lits, bound=bound, top_id=top_id, encoding=encoding); log.append(("atleast", list(lits), top_id, c)); return c
    @staticmethod
    def atmost(lits, bound, top_id, encoding):
        c = RealCE.atmost(lits=lits, bound=bound, top_id=top_id, encoding=encoding); log.append(("atmost", list(lits), top_id, c)); return c
cegar944b.CardEnc = CE
for spec, r, dmin, dmax, it in [("A5", 2, 9, 12, 8), ("S4xZ2", 1, 6, 6, 30), ("Z5x|2Z12", 2, 9, 12, 10)]:
    log.clear(); Rec.inst.clear()
    cegar944b.run(spec, r, dmin, dmax, maxiter=it, log=None, split=True)
    R = Rec.inst[-1]
    G = group_by_name(spec); A = len(sym_closure_candidates(G)); n = G.n
    used = set(range(1, A + 3 * n + 1))  # x and y
    # z variables: literals in 2-clauses [-z, x] beyond A+3n
    zs = set(-cl[0] for cl in R.clauses if len(cl) == 2 and cl[0] < 0 and -cl[0] > A + 3 * n and 0 < cl[1] <= A)
    problems = []
    if zs & used: problems.append("z overlaps x/y")
    used |= zs
    for kind, lits, top, c in log:
        lv = set(abs(l) for l in lits)
        if not lv <= used: problems.append(f"{kind}: input lits not previously defined")
        aux = set(abs(l) for cl in c.clauses for l in cl) - lv
        if aux & used: problems.append(f"{kind}: aux vars collide with earlier vars: {sorted(aux & used)[:5]}")
        if aux and min(aux) <= top: problems.append(f"{kind}: aux <= top_id")
        used |= aux
    allv = set(abs(l) for cl in R.clauses for l in cl)
    if not allv <= used: problems.append(f"unaccounted vars {sorted(allv - used)[:5]}")
    print(spec, f"A={A} n={n} z={len(zs)} cardencs={len(log)} vars={len(allv)} problems={problems}", flush=True)
