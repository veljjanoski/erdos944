"""Independent confirmation of 1-iteration NO results of cegar944b: no symmetric S with |S| in [dmin,dmax] admits a proper
3-colouring of Cay(G,S) - e using every colour on >= r+1 elements of S.  Own edge construction, totalizer encoding."""
import sys, itertools, time
sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
from search944 import group_by_name
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def run(spec, r, dmin, dmax):
    G = group_by_name(spec); T = G.table; n = G.n; e = G.e; t0 = time.time()
    inv = {g: next(h for h in range(n) if T[g][h] == e) for g in range(n)}
    invs = [frozenset([g]) for g in range(n) if g != e and inv[g] == g]
    pairs = sorted({frozenset([g, inv[g]]) for g in range(n) if g != e and inv[g] != g}, key=min)
    tot = feas = 0; ex = None
    v = lambda g, c: 3 * g + c + 1
    for np_ in range(0, len(pairs) + 1):
        for ni in range(0, len(invs) + 1):
            d = 2 * np_ + ni
            if not (dmin <= d <= dmax): continue
            for P in itertools.combinations(pairs, np_):
                for I in itertools.combinations(invs, ni):
                    S = sorted(set().union(*P, *I)); tot += 1
                    s = Cadical153(); top = 3 * n
                    for g in range(n):
                        if g != e: s.add_clause([v(g, c) for c in range(3)])
                    for g in range(n):
                        if g == e: continue
                        for t in S:
                            h = T[g][t]
                            if h == e: continue
                            for c in range(3): s.add_clause([-v(g, c), -v(h, c)])
                    for c in range(3):
                        cnf = CardEnc.atleast(lits=[v(t, c) for t in S], bound=r + 1, top_id=top, encoding=EncType.totalizer)
                        top = max(top, cnf.nv); s.append_formula(cnf.clauses)
                    if s.solve():
                        feas += 1; ex = ex or S
                    s.delete()
    print(f"{spec} n={n} r={r} [{dmin},{dmax}]: {tot} S checked, {feas} split-feasible {time.time()-t0:.0f}s ex={ex}", flush=True)
for item in sys.argv[1].split(";"):
    a = item.split(":"); run(a[0], int(a[1]), int(a[2]), int(a[3]))
