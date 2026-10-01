"""Search for (4,2)-graphs (4-vertex-critical, no critical edge set of size <= 2) among Cayley graphs.
Usage:
  python search944.py extend            # add 3..4 symmetric elements to the two known (4,1) generating sets
  python search944.py random GROUP D N  # N random symmetric connection sets of size D in GROUP
Necessary condition (Skottova-Steiner Prop. 5.1): degree >= 9.
A candidate passes if col3_with_bad(t=2) is UNSAT (d3 >= 3) and G - e is 3-colourable (vertex-transitive => all v).
"""
import sys, random, itertools, time
from c944 import *

def sym_closure_candidates(G):
    """involutions and one representative of each inverse pair (as frozensets)."""
    inv = [frozenset([g]) for g in range(G.n) if g != G.e and G.inv[g] == g]
    pairs = [frozenset([g, G.inv[g]]) for g in range(G.n) if g < G.inv[g]]
    return inv + pairs

def test(G, S, log=None):
    n, E = cayley(G, S)
    if col3_with_bad(n, E, 2) is not None: return "d3<=2"
    if col3_with_bad(n, E, 0, removed_vertex=G.e) is None: return "d3>=3,not-vc"
    ok, msg = verify_4r_explicit(n, E, 2)
    line = f"FOUND (4,2)-graph? explicit={ok} {msg}  group={G.name} n={n} S={[G.elems[s] for s in S]}"
    print(line, flush=True)
    if log: open(log, "a").write(line + "\n")
    return "FOUND" if ok else "d3>=3,vc?"

def extend():
    for name, G, S in known_graphs():
        atoms = [a for a in sym_closure_candidates(G) if not (a & set(S))]
        print(name, "atoms", len(atoms), flush=True)
        for k in (2, 3, 4):
            stats = {}; t0 = time.time(); cnt = 0
            for combo in itertools.combinations(atoms, k):
                S2 = set(S)
                for a in combo: S2 |= a
                if len(S2) > 12: continue
                r = test(G, sorted(S2), log="found.log"); stats[r] = stats.get(r, 0) + 1; cnt += 1
            print(f"  {name} +{k} atoms: {cnt} sets in {time.time()-t0:.0f}s -> {stats}", flush=True)

def group_by_name(spec):
    """e.g. Z5x|2Z12, S4xZ2, D12, Dic6, A4xZ3, Z3x|2Z4 ..."""
    def one(s):
        if s.startswith("Dic"): return dicyclic(int(s[3:]))
        if s.startswith("D"): return dihedral(int(s[1:]))
        if s.startswith("S"): return sym(int(s[1:]))
        if s.startswith("A"): return alt(int(s[1:]))
        if "x|" in s:
            a, b = s.split("x|"); m = int(a[1:]); t, n = b.split("Z"); return semidirect(m, int(n), int(t))
        return cyclic(int(s[1:]))
    parts = spec.split("x") if "x|" not in spec else [spec]
    if "x|" in spec:
        # allow e.g. Z5x|2Z12xZ2 : split on 'xZ' after the semidirect part
        i = spec.find("x|"); j = spec.find("xZ", i + 2)
        parts = [spec] if j < 0 else [spec[:j], spec[j + 1:]]
    G = one(parts[0])
    for p in parts[1:]: G = direct(G, one(p))
    return G

def random_search(spec, d, N):
    G = group_by_name(spec); atoms = sym_closure_candidates(G)
    print(spec, "order", G.n, "atoms", len(atoms), "degree", d, flush=True)
    stats = {}; t0 = time.time()
    for it in range(N):
        random.shuffle(atoms); S = set()
        for a in atoms:
            if len(S) + len(a) <= d: S |= a
            if len(S) == d: break
        if len(S) != d: continue
        r = test(G, sorted(S), log="found.log"); stats[r] = stats.get(r, 0) + 1
        if (it + 1) % 200 == 0: print(f"  {it+1} tried {time.time()-t0:.0f}s {stats}", flush=True)
    print(spec, d, "final", stats, flush=True)

if __name__ == "__main__":
    if sys.argv[1] == "extend": extend()
    else: random_search(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
