"""Closure test (exact): is a given (4,1)-graph G1 contained in some (4,2)-graph?

Facts used (all elementary):
 (i)  If H is 4-vertex-critical and G1 is a 4-chromatic subgraph of H, then V(G1) = V(H) (else H - v contains G1 for some v
      outside G1, so chi(H - v) = 4).  So only supergraphs H = G1 + F on the same vertex set, F a set of non-edges, matter.
 (ii) H = G1 + F is vertex-critical iff for every vertex u there is a proper 3-colouring c_u of G1 - u that is also proper on
      the edges of F not containing u.  (chi(H) = 4 then holds automatically: chi(H) >= chi(G1) = 4 and chi(H - u) <= 3.)
 (iii) d3(G1) = 2 (G1 is a (4,1)-graph whose defect is exactly 2), so d3(H) >= 3 iff every 3-colouring phi of V with exactly
      2 monochromatic edges of G1 makes at least one edge of F monochromatic.
Given the choices c = (c_u), the largest allowed F is C(c) = {non-edges xy : c_u(x) != c_u(y) for all u not in {x, y}},
and adding edges only helps (iii).  Hence: G1 lies in a (4,2)-graph  <=>  there is a choice c of colourings, c_u a proper
3-colouring of G1 - u, such that C(c) hits every defect-2 colouring of G1.  Colourings matter only up to renaming colours.
This is decided by one SAT instance (variables sel[u,i] = "c_u is colouring i", p[x,y] = "xy in C(c)").
For a Cayley graph the proper colourings of G1 - u are the left translates of those of G1 - e.

Usage: python closure944.py GROUP r0 deg      e.g.  python closure944.py S4xZ2 1 6
  (enumerates the (4,r0)-witness orbits of that degree with the validated cegar944c and tests each of them)
"""
import sys, time, itertools
from pysat.solvers import Cadical153, Glucose4
from pysat.card import CardEnc, EncType
from c944 import cayley, col3_with_bad, defect3, vertex_critical, verify_4r_explicit
from search944 import group_by_name
import cegar944c

PERMS = list(itertools.permutations(range(3)))

def all_colourings(n, edges, removed_vertex=None, max_bad=0, cap=200000):
    """All 3-colourings (list of tuples, -1 at the removed vertex) with at most max_bad monochromatic edges, one per
    class under renaming of colours (each found colouring is blocked together with its 6 renamings)."""
    var = lambda v, c: 3 * v + c + 1
    s = Cadical153(); top = 3 * n; bad = []
    V = [v for v in range(n) if v != removed_vertex]
    for v in V:
        s.add_clause([var(v, c) for c in range(3)])
        for c1 in range(3):
            for c2 in range(c1 + 1, 3): s.add_clause([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        if removed_vertex in (u, v): continue
        if max_bad == 0:
            for c in range(3): s.add_clause([-var(u, c), -var(v, c)])
        else:
            top += 1; bad.append(top)
            for c in range(3): s.add_clause([-var(u, c), -var(v, c), top])
    if max_bad > 0:
        cnf = CardEnc.atmost(lits=bad, bound=max_bad, top_id=top, encoding=EncType.seqcounter)
        for cl in cnf.clauses: s.add_clause(cl)
    out = []
    while s.solve():
        m = set(l for l in s.get_model() if l > 0)
        col = [-1] * n
        for v in V: col[v] = next(c for c in range(3) if var(v, c) in m)
        out.append(tuple(col))
        for p in PERMS: s.add_clause([-var(v, p[col[v]]) for v in V])
        if len(out) >= cap: s.delete(); raise RuntimeError(f"more than {cap} colourings; aborting (no verdict)")
    s.delete(); return out

def count_plain(n, edges, max_bad):
    """Second count: all colourings with at most max_bad monochromatic edges, NOT modulo renaming (each blocked alone)."""
    var = lambda v, c: 3 * v + c + 1
    s = Glucose4(); top = 3 * n; bad = []
    for v in range(n):
        s.add_clause([var(v, c) for c in range(3)])
        for c1 in range(3):
            for c2 in range(c1 + 1, 3): s.add_clause([-var(v, c1), -var(v, c2)])
    for (u, v) in edges:
        top += 1; bad.append(top)
        for c in range(3): s.add_clause([-var(u, c), -var(v, c), top])
    cnf = CardEnc.atmost(lits=bad, bound=max_bad, top_id=top, encoding=EncType.totalizer)
    for cl in cnf.clauses: s.add_clause(cl)
    k = 0
    while s.solve():
        m = set(l for l in s.get_model() if l > 0); k += 1
        s.add_clause([-var(v, c) for v in range(n) for c in range(3) if var(v, c) in m])
    s.delete(); return k

def closure_test(G, S, label, solver_names=("cadical", "glucose")):
    t0 = time.time()
    n, E = cayley(G, S); Eset = set(E)
    d = defect3(n, E, cap=4); vc = vertex_critical(n, E, vertices=[G.e])
    print(f"[{label}] n={n} m={len(E)} deg={len(S)} d3={d} G-e 3-colourable={vc}", flush=True)
    assert d == 2 and vc, "input must be a (4,1)-graph with defect exactly 2"
    base = all_colourings(n, E, removed_vertex=G.e)                      # proper colourings of G1 - e mod renaming
    D2 = all_colourings(n, E, max_bad=2)                                  # colourings with <= 2 (hence exactly 2) mono edges
    assert all(sum(1 for (u, v) in E if c[u] == c[v]) == 2 for c in D2)
    print(f"[{label}] proper colourings of G1-e mod renaming: {len(base)}; defect-2 colourings mod renaming: {len(D2)}  [{time.time()-t0:.0f}s]", flush=True)
    # independent second count (other solver, other cardinality encoding, no renaming symmetry): every class has 6 members
    # because a colouring with <= 2 bad edges of a 4-chromatic graph (or a proper colouring of G1 - e, which has chromatic number 3) uses 3 colours
    E_minus_e = [(u, v) for (u, v) in E if G.e not in (u, v)]
    c2 = count_plain(n, E, 2); c0 = count_plain(n, E_minus_e, 0)      # c0 counts the free colour of e too (factor 3)
    print(f"[{label}] check: plain counts {c2} = 6 x {len(D2)}? {c2 == 6 * len(D2)};  {c0} = 18 x {len(base)}? {c0 == 18 * len(base)}  [{time.time()-t0:.0f}s]", flush=True)
    assert c2 == 6 * len(D2) and c0 == 18 * len(base), "colouring counts disagree"
    # left translates: c_u(g) = c_e(u^-1 g)
    inv = G.inv; T = G.table
    cols = {u: [tuple(c[T[inv[u]][g]] for g in range(n)) for c in base] for u in range(n)}
    for u in range(n): assert all(cu[u] == -1 for cu in cols[u])
    K = len(base)
    nonedges = [(x, y) for x in range(n) for y in range(x + 1, n) if (x, y) not in Eset]
    sel = lambda u, i: u * K + i + 1
    pv = {xy: n * K + j + 1 for j, xy in enumerate(nonedges)}
    clauses = []
    for u in range(n):
        clauses.append([sel(u, i) for i in range(K)])
        for i in range(K):
            for j in range(i + 1, K): clauses.append([-sel(u, i), -sel(u, j)])
    for (x, y) in nonedges:
        for u in range(n):
            if u in (x, y): continue
            for i, c in enumerate(cols[u]):
                if c[x] == c[y]: clauses.append([-pv[(x, y)], -sel(u, i)])
    for phi in D2:
        clauses.append([pv[(x, y)] for (x, y) in nonedges if phi[x] == phi[y]])
    print(f"[{label}] SAT instance: {n*K + len(nonedges)} variables, {len(clauses)} clauses  [{time.time()-t0:.0f}s]", flush=True)
    verdicts = []
    for name in solver_names:
        s = Cadical153() if name == "cadical" else Glucose4()
        for cl in clauses: s.add_clause(cl)
        ok = s.solve(); model = set(l for l in s.get_model() if l > 0) if ok else None; s.delete()
        verdicts.append(ok); print(f"[{label}] {name}: {'SAT (candidate supergraph)' if ok else 'UNSAT'}  [{time.time()-t0:.0f}s]", flush=True)
        if ok:
            F = [xy for xy in nonedges if pv[xy] in model]
            H = sorted(set(E) | set(F))
            print(f"[{label}] candidate H: {len(F)} added edges; checking (4,2) directly ...", flush=True)
            res = verify_4r_explicit(n, H, 2)
            print(f"[{label}] explicit (4,2) check of H: {res}", flush=True)
    assert len(set(verdicts)) == 1, "solvers disagree"
    msg = (f"[{label}] RESULT: no (4,2)-graph contains this graph (exact)" if not verdicts[0]
           else f"[{label}] RESULT: SAT - see candidate check above")
    print(msg, flush=True)
    return verdicts[0], len(base), len(D2)

if __name__ == "__main__":
    spec, r0, deg = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    G = group_by_name(spec)
    W = cegar944c.run(spec, r0, deg, deg, log=None, symm=True, enum_all=True)
    if not isinstance(W, list): sys.exit(f"{spec}: witness enumeration incomplete ({W}); no verdict")
    print(f"{spec}: {len(W)} witness orbit(s) of (4,{r0})-Cayley graphs at degree {deg}", flush=True)
    for k, S in enumerate(W):
        print(f"{spec} orbit {k}: S = {[G.elems[t] for t in S]}", flush=True)
        closure_test(G, S, f"{spec}#{k}")
