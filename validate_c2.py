"""Orbit test at realistic size: all r=1 degree-6 witnesses on the three known witness groups, enumerated without symmetry
breaking (cegar944c with symm=False = version b + blocking clauses), versus with symmetry breaking."""
import sys, time
import cegar944c
from search944 import group_by_name
from auto944 import automorphisms
spec = sys.argv[1]; t0 = time.time()
G = group_by_name(spec); auts, _ = automorphisms(G)
Wall = {tuple(sorted(S)) for S in cegar944c.run(spec, 1, 6, 6, log=None, symm=False, enum_all=True)}
Wsym = [tuple(sorted(S)) for S in cegar944c.run(spec, 1, 6, 6, log=None, symm=True, enum_all=True)]
orbits = {}
for S in Wall: orbits.setdefault(min(tuple(sorted(p[t] for t in S)) for p in auts), set()).add(S)
hits = [sum(1 for S in Wsym if S in o) for o in orbits.values()]
ok = all(S in Wall for S in Wsym) and all(h == 1 for h in hits)
print(f"{'OK' if ok else 'FAIL'} {spec}: |Aut|={len(auts)} all witnesses {len(Wall)} in {len(orbits)} orbits; symmetry-broken search found {len(Wsym)}, hits per orbit {sorted(set(hits))}  {time.time()-t0:.0f}s", flush=True)
