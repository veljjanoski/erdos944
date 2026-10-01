"""Known (4,1)-graphs: (a) split soundness directly (no proper colouring of G-e with some colour on <= r elements of S);
(b) the cegar944b base CNF (r=1, degree 6) admits the known S; (c) the known S satisfy every cut added in a full r=1 run."""
import sys, itertools
sys.path.insert(0, r"C:\Users\danie\Math\erdos944"); sys.path.insert(0, r"C:\Users\danie\Math\erdos944\review_tmp")
from c944 import known_graphs, cayley, col3_with_bad
from pysat.solvers import Cadical153 as RealCad
import cegar944b, search944
for name, G, S in known_graphs():
    n, E = cayley(G, S); e = G.e
    v = lambda g, c: 3 * g + c + 1
    bad = 0
    for c in range(3):
        for T in itertools.combinations(S, 5):   # colour c appears on at most 1 element of S  <=>  some 5 elements avoid c
            s = RealCad()
            for g in range(n):
                if g != e: s.add_clause([v(g, cc) for cc in range(3)])
            for (a, b) in E:
                if e in (a, b): continue
                for cc in range(3): s.add_clause([-v(a, cc), -v(b, cc)])
            for t in T: s.add_clause([-v(t, c)])
            if s.solve(): bad += 1
            s.delete()
    print(name, "split-violating colourings of G-e:", bad, "| d3<=1 colouring exists:", col3_with_bad(n, E, 1) is not None, flush=True)
