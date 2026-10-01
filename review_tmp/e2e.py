"""End-to-end: all witnesses enumerated by (a copy of) cegar944b vs. an independent brute force over all symmetric S."""
import sys, itertools, time
sys.path.insert(0, r"C:\Users\danie\Math\erdos944"); sys.path.insert(0, r"C:\Users\danie\Math\erdos944\review_tmp")
import cegar_all
from pysat.solvers import Cadical153
from search944 import group_by_name

def edges_of(T, n, S):
    E = set()
    for g in range(n):
        for s in S:
            h = T[g][s]
            if h != g: E.add((min(g, h), max(g, h)))
    return sorted(E)

def col3(n, E, skipv=None, skipE=()):
    v = lambda g, c: 3 * g + c + 1
    s = Cadical153(); sk = set(skipE)
    for g in range(n):
        if g != skipv: s.add_clause([v(g, c) for c in range(3)])
    for (a, b) in E:
        if skipv in (a, b) or (a, b) in sk: continue
        for c in range(3): s.add_clause([-v(a, c), -v(b, c)])
    ok = s.solve(); s.delete(); return ok

def brute(G, r, dmin, dmax):
    n = G.n; T = G.table; e = G.e
    # independent atom list: orbits of inversion on non-identity elements
    inv = {g: next(h for h in range(n) if T[g][h] == e) for g in range(n)}
    atoms = sorted({frozenset([g, inv[g]]) for g in range(n) if g != e}, key=min)
    res = set()
    for k in range(1, len(atoms) + 1):
        for combo in itertools.combinations(atoms, k):
            S = sorted(set().union(*combo))
            if not (dmin <= len(S) <= dmax): continue
            E = edges_of(T, n, S)
            if col3(n, E): continue                 # chi <= 3
            if not col3(n, E, skipv=e): continue    # not vertex-critical (vertex-transitive)
            good = True
            for k2 in range(1, r + 1):
                for F in itertools.combinations(E, k2):
                    if col3(n, E, skipE=F): good = False; break
                if not good: break
            if good: res.add(tuple(S))
    return res

def main(spec, r, dmin, dmax):
    G = group_by_name(spec)
    t0 = time.time(); B = brute(G, r, dmin, dmax); tb = time.time() - t0
    out = []
    for split in (True, False):
        t0 = time.time(); W = cegar_all.run(spec, r, dmin, dmax, maxiter=200000, log=None, split=split)
        if W == "maxiter": out.append(f"split={split}: MAXITER"); continue
        Ws = set(S for S, ok in W); allok = all(ok for S, ok in W)
        status = "MATCH" if Ws == B else f"MISMATCH missed={sorted(B - Ws)[:3]} extra={sorted(Ws - B)[:3]}"
        out.append(f"split={split}: {len(Ws)} wit explicit_all_ok={allok} {status} ({time.time()-t0:.0f}s)")
    print(f"{spec} n={G.n} r={r} [{dmin},{dmax}] brute={len(B)} ({tb:.0f}s) | " + " | ".join(out), flush=True)

if __name__ == "__main__":
    for item in sys.argv[1].split(";"):
        spec, r, dmin, dmax = item.split(":")
        try: main(spec, int(r), int(dmin), int(dmax))
        except Exception as ex: print(spec, r, dmin, dmax, "EXCEPTION", repr(ex), flush=True)
