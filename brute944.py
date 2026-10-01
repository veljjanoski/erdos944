"""Brute-force cross-check of cegar944 negatives: enumerate all symmetric S with |S| in [dmin,dmax] on a small group
and test (4,r) directly with c944 (defect via col3_with_bad, vertex-criticality via G - e)."""
import sys, itertools, time
from c944 import *
from search944 import group_by_name, sym_closure_candidates
spec, r, dmin, dmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
G = group_by_name(spec); atoms = sym_closure_candidates(G); t0 = time.time()
cnt = 0; vc = 0; found = []
for k in range(1, len(atoms) + 1):
    for combo in itertools.combinations(atoms, k):
        d = sum(len(a) for a in combo)
        if d < dmin or d > dmax: continue
        S = sorted(set().union(*combo)); n, E = cayley(G, S); cnt += 1
        if col3_with_bad(n, E, 0, removed_vertex=G.e) is None: continue
        vc += 1
        if col3_with_bad(n, E, r) is None: found.append(S)
print(f"{spec} order {G.n}: {cnt} sets, {vc} with G-e 3-colourable, {len(found)} (4,{r})-graphs  {time.time()-t0:.0f}s", found[:3])
