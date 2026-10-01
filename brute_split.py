"""Independent check of the split constraint used by cegar944b (no cardinality encodings, no auxiliary variables).
For every symmetric S with |S| in [dmin, dmax]: enumerate every assignment of colours to the elements of S in which each
colour occurs >= r+1 times (up to fixing the colour of the first element to 0 is NOT done: all assignments), and ask a plain
3-colouring SAT solver whether Cay(Gamma,S) - e has a proper colouring extending it (unit assumptions).
Prints the number of S that admit such a colouring ("split-feasible"); cegar944b can only report NO in 1 iteration if this is 0."""
import sys, itertools, time
from pysat.solvers import Cadical153
from c944 import cayley
from search944 import group_by_name, sym_closure_candidates
spec, r, dmin, dmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
G = group_by_name(spec); atoms = sym_closure_candidates(G); e = G.e; t0 = time.time()
tot = feas = 0; examples = []
for k in range(1, len(atoms) + 1):
    for combo in itertools.combinations(atoms, k):
        d = sum(len(a) for a in combo)
        if d < dmin or d > dmax: continue
        S = sorted(set().union(*combo)); n, E = cayley(G, S); tot += 1
        var = lambda v, c: 3 * v + c + 1
        s = Cadical153()
        for v in range(n):
            if v != e: s.add_clause([var(v, c) for c in range(3)])
        for (u, v) in E:
            if e in (u, v): continue
            for c in range(3): s.add_clause([-var(u, c), -var(v, c)])
        hit = False
        for assign in itertools.product(range(3), repeat=len(S)):
            if min(assign.count(c) for c in range(3)) < r + 1: continue
            if s.solve(assumptions=[var(t, c) for t, c in zip(S, assign)]): hit = True; break
        s.delete()
        if hit:
            feas += 1
            if len(examples) < 2: examples.append(S)
print(f"{spec} r={r} deg[{dmin},{dmax}]: {tot} sets, {feas} split-feasible  {time.time()-t0:.0f}s", examples)
