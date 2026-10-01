"""Validation of cegar944s (version s).

mode 'lane' GROUP r d:  all witness orbits at degree d from the validated cegar944c (enum_all, symmetry breaking on: exactly
   one member per Aut-orbit), their stabilisers computed directly; then cegar944s with enum_all for EVERY prime-order class
   (cuts off).  PASS iff the set of Aut-orbits found by the lane equals the set of orbits with a nontrivial stabiliser, and
   the lane with sigma = id finds exactly the same orbits as cegar944c.
mode 'same' GROUP r dmin dmax:  cegar944s with sigma = id (colsym and cuts on) must give the same verdict (witness / NO) as
   cegar944c; prints both times.
"""
import sys, time
import cegar944c, cegar944s
from search944 import group_by_name
from auto944 import automorphisms

def canon(S, auts): return min(tuple(sorted(f[t] for t in S)) for f in auts)

def lane(spec, r, d, cubes=False):
    t0 = time.time(); G = group_by_name(spec); auts, _ = automorphisms(G)
    Wc = cegar944c.run(spec, r, d, d, log=None, symm=True, enum_all=True)
    orbits = {canon(S, auts) for S in Wc}
    assert len(orbits) == len(Wc), "cegar944c returned two members of one orbit"
    ident = tuple(range(G.n))
    nontriv = {canon(S, auts) for S in Wc if any(tuple(f) != ident and sorted(f[t] for t in S) == sorted(S) for f in auts)}
    classes, _ = cegar944s.prime_classes(G, cegar944s.aut_data(G), max(d, 2))
    found = set(); per = []
    for k in range(len(classes)):
        Wk = cegar944s.run(spec, r, d, d, str(k), cuts=False, enum_all=True, record=False, cubes=cubes, progress=False)
        ck = {canon(S, auts) for S in Wk}; found |= ck; per.append(len(ck))
    Wid = cegar944s.run(spec, r, d, d, 'id', cuts=False, enum_all=True, record=False)
    same_id = {canon(S, auts) for S in Wid} == orbits and len(Wid) == len(orbits)
    ok = found == nontriv and same_id
    print(f"{'PASS' if ok else 'FAIL'} lane{' (cubes)' if cubes else ''} {spec} r={r} d={d}: orbits {len(orbits)}, with nontrivial stabiliser {len(nontriv)}, "
          f"found by sigma-lane {len(found)} (per class {per}); sigma=id finds all orbits exactly once: {same_id}  [{time.time()-t0:.0f}s]", flush=True)
    return ok

def same(spec, r, dmin, dmax):
    t0 = time.time(); a = cegar944c.run(spec, r, dmin, dmax, log=None); t1 = time.time()
    b = cegar944s.run(spec, r, dmin, dmax, 'id', cuts=True, record=False); t2 = time.time()
    ok = (a is None) == (b is None)
    print(f"{'PASS' if ok else 'FAIL'} same {spec} r={r} d=[{dmin},{dmax}]: c {'NO' if a is None else 'WITNESS'} {t1-t0:.0f}s, "
          f"s(id) {'NO' if b is None else 'WITNESS'} {t2-t1:.0f}s", flush=True)
    return ok

def cmp(spec, r, d, k):
    """same lane (sigma class k) without and with cubes: verdicts must agree."""
    t0 = time.time(); a = cegar944s.run(spec, r, d, d, k, cuts=False, record=False); t1 = time.time()
    b = cegar944s.run(spec, r, d, d, k, cuts=False, record=False, cubes=True, progress=False); t2 = time.time()
    ok = (a is None) == (b is None)
    print(f"{'PASS' if ok else 'FAIL'} cmp {spec} r={r} d={d} sigma={k}: plain {'NO' if a is None else 'WITNESS'} {t1-t0:.0f}s, "
          f"cubes {'NO' if b is None else 'WITNESS'} {t2-t1:.0f}s", flush=True)
    return ok

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "lane": ok = lane(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif mode == "lanec": ok = lane(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), cubes=True)
    elif mode == "cmp": ok = cmp(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else: ok = same(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    sys.exit(0 if ok else 1)
