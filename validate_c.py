"""Validation of cegar944c symmetry breaking (orbit test).

For each (group, r, dmin, dmax): W_b = all symmetric S with |S| in range such that Cay(G,S) is a (4,r)-graph, by brute force
(G - e 3-colourable and no 3-colouring with <= r monochromatic edges; vertex-transitivity => one vertex suffices; chi = 4 then
follows from d3 >= 1 and G - e 3-colourable).  W_c = all witnesses cegar944c enumerates (blocking clauses).
Checks: W_c subset of W_b, and every Aut-orbit of W_b contains exactly one element of W_c.
"""
import sys, itertools, time
from multiprocessing import Pool
from c944 import cayley, col3_with_bad
from search944 import group_by_name, sym_closure_candidates
from auto944 import automorphisms
import cegar944c

def brute(G, atoms, r, dmin, dmax):
    W = set()
    for k in range(1, len(atoms) + 1):
        for combo in itertools.combinations(atoms, k):
            d = sum(len(a) for a in combo)
            if d < dmin or d > dmax: continue
            S = tuple(sorted(set().union(*combo))); n, E = cayley(G, S)
            if col3_with_bad(n, E, 0, removed_vertex=G.e) is None: continue
            if col3_with_bad(n, E, r) is None: W.add(S)
    return W

def case(args):
    spec, r, dmin, dmax = args
    t0 = time.time()
    G = group_by_name(spec); atoms = sym_closure_candidates(G)
    Wb = brute(G, atoms, r, dmin, dmax)
    Wc = [tuple(sorted(S)) for S in (cegar944c.run(spec, r, dmin, dmax, log=None, enum_all=True) or [])]
    auts, _ = automorphisms(G)
    orbits = {}
    for S in Wb:
        key = min(tuple(sorted(p[t] for t in S)) for p in auts)
        orbits.setdefault(key, set()).add(S)
    bad = [S for S in Wc if S not in Wb]
    per_orbit = [sum(1 for S in Wc if S in orb) for orb in orbits.values()]
    ok = not bad and all(c == 1 for c in per_orbit) and len(Wc) == len(set(Wc))
    return (f"{'OK  ' if ok else 'FAIL'} {spec:10s} r={r} deg[{dmin},{dmax}] |Aut|={len(auts):4d} brute witnesses {len(Wb):4d} "
            f"in {len(orbits):3d} orbits, cegar944c found {len(Wc):3d}, not-real {len(bad)}, orbits hit {sum(1 for c in per_orbit if c)}"
            f"/{len(orbits)} (max per orbit {max(per_orbit) if per_orbit else 0})  {time.time()-t0:.0f}s")

if __name__ == "__main__":
    small = ['Z8', 'Z9', 'Z10', 'Z11', 'Z12', 'Z13', 'Z14', 'Z15', 'Z16', 'Z18', 'Z20', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10',
             'A4', 'Dic2', 'Dic3', 'Dic4', 'Dic5', 'Z2xZ4', 'Z2xZ6', 'Z3xZ3', 'Z2xZ2xZ2', 'Z4xZ4', 'Z2xZ8', 'Z2xZ2xZ4', 'Z5x|2Z4',
             'Z7x|2Z3', 'Z3xZ6', 'Z2xZ10']
    mid = ['S4', 'D12', 'Dic6', 'A4xZ2', 'Z2xZ12', 'Z3x|2Z8', 'Z24', 'Z21', 'Z22']
    cases = [(g, 0, 3, 6) for g in small] + [(g, 1, 6, 8) for g in small] + [(g, 0, 3, 5) for g in mid] + [(g, 1, 6, 6) for g in mid]
    with Pool(14) as pool:
        for line in pool.imap_unordered(case, cases):
            print(line, flush=True)
