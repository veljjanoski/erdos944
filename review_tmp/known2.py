import sys
sys.path.insert(0, r"C:\Users\danie\Math\erdos944"); sys.path.insert(0, r"C:\Users\danie\Math\erdos944\review_tmp")
import structcheck  # installs recording solver into cegar944b
from structcheck import Rec, RealCad
import cegar944b
from c944 import known_graphs
from search944 import group_by_name, sym_closure_candidates
specs = {"Kitamura48": "S4xZ2", "Chan60": "Z5x|2Z12"}
for name, G0, S0 in known_graphs():
    spec = specs[name]
    for split in (True, False):
        Rec.inst.clear()
        res = cegar944b.run(spec, 1, 6, 6, maxiter=5000, log=None, split=split)
        R = Rec.inst[-1]
        G = group_by_name(spec); atoms = sym_closure_candidates(G); A = len(atoms)
        assert G.table == G0.table
        chosen = [a for a, at in enumerate(atoms) if at <= set(S0)]
        assert sorted(set().union(*[atoms[a] for a in chosen])) == sorted(S0)
        s = RealCad(bootstrap_with=R.clauses)
        ok = s.solve(assumptions=[a + 1 if a in chosen else -(a + 1) for a in range(A)])
        print(name, "split" if split else "nosplit", "iterations", len(R.solves), "found", res if res is None else [G.elems[t] for t in res],
              "| known S still feasible under ALL recorded clauses:", ok, flush=True)
        s.delete()
