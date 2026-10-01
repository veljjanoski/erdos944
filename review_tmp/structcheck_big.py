import sys, itertools
sys.path.insert(0, r"C:\Users\danie\Math\erdos944\review_tmp")
import structcheck
from structcheck import check, RealCad, cayley
from pysat.card import CardEnc, EncType
def indep_feasible_tot(G, S, r, split):
    n, E = cayley(G, S); e = G.e
    v = lambda g, c: 3 * g + c + 1
    s = RealCad(); top = 3 * n
    for g in range(n):
        if g == e: continue
        s.add_clause([v(g, c) for c in range(3)])
        for c1, c2 in itertools.combinations(range(3), 2): s.add_clause([-v(g, c1), -v(g, c2)])
    for (a, b) in E:
        if e in (a, b): continue
        for c in range(3): s.add_clause([-v(a, c), -v(b, c)])
    if split:
        for c in range(3):
            if len(S) < r + 1: s.delete(); return False
            cnf = CardEnc.atleast(lits=[v(t, c) for t in S], bound=r + 1, top_id=top, encoding=EncType.totalizer)
            top = max(top, cnf.nv)
            for cl in cnf.clauses: s.add_clause(cl)
    ok = s.solve(); s.delete(); return ok
structcheck.indep_feasible = indep_feasible_tot
specs = sys.argv[1].split(",")
for spec in specs:
    for (r, dmin, dmax) in [(0, 1, 60), (1, 6, 6), (2, 9, 12), (2, 6, 14)]:
        for split in (True, False):
            check(spec, r, dmin, dmax, split, nsamp=int(sys.argv[2]) if len(sys.argv) > 2 else 200, seed=hash(spec) % 1000)
