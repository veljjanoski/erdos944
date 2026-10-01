"""Exact search for (4,r)-Cayley graphs on a given group by counterexample-guided SAT.

Unknowns: x_a for each "atom" a (an involution {s} or an inverse pair {s, s^-1}) -- S is the union of chosen atoms --
and a 3-colouring y of Gamma - e that must be proper for Cay(Gamma, S) - e (this is vertex-criticality up to the
requirement chi(G) = 4, which follows from d3 >= r+1 >= 1).  Degree = sum |a| x_a is constrained to [dmin, dmax].
Loop: solve -> S -> look for a 3-colouring c of Cay(Gamma,S) with <= r monochromatic edges; if one exists add the
constraint  sum_a w_a(c) x_a >= r+1  (w_a(c) = number of edges g ~ g s, s in a, monochromatic under c), which every
valid S must satisfy since c has >= r+1 monochromatic edges in every (4,r)-graph; else S is a witness (then verified
independently by verify_4r_explicit).  UNSAT = no (4,r)-Cayley graph on this group in the degree range.

Usage: python cegar944.py GROUP r dmin dmax [maxiter]
"""
import sys, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from c944 import *
from search944 import group_by_name, sym_closure_candidates

def run(spec, r, dmin, dmax, maxiter=100000, log=None):
    G = group_by_name(spec); atoms = sym_closure_candidates(G); n = G.n; e = G.e
    A = len(atoms)
    x = lambda a: a + 1
    y = lambda g, c: A + 3 * g + c + 1
    top = A + 3 * n
    s = Cadical153()
    for g in range(n):
        if g != e: s.add_clause([y(g, c) for c in range(3)])
    for a, atom in enumerate(atoms):
        for g in range(n):
            if g == e: continue
            for t in atom:
                h = G.table[g][t]
                if h == e or h < g and G.inv[t] in atom: continue  # each undirected edge once (pair atoms give both directions)
                for c in range(3): s.add_clause([-x(a), -y(g, c), -y(h, c)])
    wl = []
    for a, atom in enumerate(atoms): wl += [x(a)] * len(atom)
    for cnf in (CardEnc.atleast(lits=wl, bound=dmin, top_id=top, encoding=EncType.seqcounter),):
        top = max(top, cnf.nv); [s.add_clause(cl) for cl in cnf.clauses]
    cnf = CardEnc.atmost(lits=wl, bound=dmax, top_id=top, encoding=EncType.seqcounter)
    top = max(top, cnf.nv); [s.add_clause(cl) for cl in cnf.clauses]
    t0 = time.time(); it = 0
    while it < maxiter:
        it += 1
        if not s.solve():
            msg = f"{spec} order {n}: NO (4,{r})-Cayley graph with degree in [{dmin},{dmax}]  ({it} iterations, {time.time()-t0:.0f}s)"
            print(msg, flush=True)
            if log: open(log, "a").write(msg + "\n")
            return None
        m = set(l for l in s.get_model() if l > 0)
        S = sorted(set().union(*[atoms[a] for a in range(A) if x(a) in m])) if any(x(a) in m for a in range(A)) else []
        nn, E = cayley(G, S)
        col = col3_with_bad(nn, E, r)
        if col is None:
            ok, msg = verify_4r_explicit(nn, E, r)
            line = f"{spec} order {n}: WITNESS degree {len(S)} S={[G.elems[t] for t in S]} explicit={ok} {msg} ({it} it, {time.time()-t0:.0f}s)"
            print(line, flush=True)
            if log: open(log, "a").write(line + "\n")
            return S
        # counterexample colouring: weights per atom
        w = []
        for a, atom in enumerate(atoms):
            cnt = 0
            for g in range(n):
                for t in atom:
                    h = G.table[g][t]
                    if h < g and G.inv[t] in atom: continue
                    if col[g] == col[h]: cnt += 1
            w.append(cnt)
        lits = []
        for a in range(A): lits += [x(a)] * w[a]
        cnf = CardEnc.atleast(lits=lits, bound=r + 1, top_id=top, encoding=EncType.seqcounter)
        top = max(top, cnf.nv); [s.add_clause(cl) for cl in cnf.clauses]
        if it % 50 == 0: print(f"  {spec} it {it} deg {len(S)} {time.time()-t0:.0f}s", flush=True)
    print(f"{spec}: maxiter reached", flush=True); return "maxiter"

if __name__ == "__main__":
    spec, r, dmin, dmax = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    run(spec, r, dmin, dmax, int(sys.argv[5]) if len(sys.argv) > 5 else 100000, log="cegar.log")
