"""cegar944 with the neighbourhood-split constraint (version b).

Same exact search as cegar944.py (see its docstring), plus one extra constraint on the 3-colouring y of Gamma - e:

    every colour appears on at least r+1 of the neighbours of e, i.e. on at least r+1 elements of S.

Soundness: if Cay(Gamma, S) is a (4,r)-graph, then G - e is 3-colourable, and EVERY proper 3-colouring y of G - e
gives each colour to at least r+1 neighbours of e; otherwise colouring e with the rarest colour would give a
3-colouring of G with at most r monochromatic edges, i.e. d3(G) <= r.  So every witness S, together with any proper
colouring y of its G - e, satisfies the new constraint: nothing is excluded that the old program could find.
At degree 3(r+1) (degree 9 for r = 2) this forces an exact (r+1, r+1, r+1) split of S.

To make the colour counts meaningful y also gets at-most-one-colour clauses (any proper colouring can be taken with
exactly one colour per vertex, so this excludes nothing either).

Usage: python cegar944b.py GROUP r dmin dmax [maxiter] [--nosplit]
"""
import sys, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from c944 import *
from search944 import group_by_name, sym_closure_candidates

def run(spec, r, dmin, dmax, maxiter=100000, log=None, split=True):
    G = group_by_name(spec); atoms = sym_closure_candidates(G); n = G.n; e = G.e
    WIT = []
    A = len(atoms)
    x = lambda a: a + 1
    y = lambda g, c: A + 3 * g + c + 1
    top = A + 3 * n
    s = Cadical153()
    def add(cnf):
        nonlocal top
        top = max(top, cnf.nv)
        for cl in cnf.clauses: s.add_clause(cl)
    for g in range(n):
        if g == e: continue
        s.add_clause([y(g, c) for c in range(3)])
        if split:
            for c1 in range(3):
                for c2 in range(c1 + 1, 3): s.add_clause([-y(g, c1), -y(g, c2)])
    # y proper on Cay(Gamma, S) - e: each undirected edge {g, g t} once, from its smaller endpoint
    for a, atom in enumerate(atoms):
        for g in range(n):
            if g == e: continue
            for t in atom:
                h = G.table[g][t]
                if h == e or h < g: continue
                for c in range(3): s.add_clause([-x(a), -y(g, c), -y(h, c)])
    # degree range
    wl = []
    for a, atom in enumerate(atoms): wl += [x(a)] * len(atom)
    add(CardEnc.atleast(lits=wl, bound=dmin, top_id=top, encoding=EncType.seqcounter))
    add(CardEnc.atmost(lits=wl, bound=dmax, top_id=top, encoding=EncType.seqcounter))
    # neighbourhood split: for each colour c, #{t in S : y(t) = c} >= r+1.  z(t,c) -> x(atom of t) and z(t,c) -> y(t,c)
    if split:
        for c in range(3):
            zs = []
            for a, atom in enumerate(atoms):
                for t in atom:
                    top += 1; z = top; zs.append(z)
                    s.add_clause([-z, x(a)]); s.add_clause([-z, y(t, c)])
            add(CardEnc.atleast(lits=zs, bound=r + 1, top_id=top, encoding=EncType.seqcounter))
    t0 = time.time(); it = 0
    tag = "b" if split else "b-nosplit"
    while it < maxiter:
        it += 1
        if not s.solve():
            msg = f"{spec} order {n}: NO (4,{r})-Cayley graph with degree in [{dmin},{dmax}]  ({it} iterations, {time.time()-t0:.0f}s) [{tag}]"
            pass
            if log: open(log, "a").write(msg + "\n")
            return WIT
        m = set(l for l in s.get_model() if l > 0)
        S = sorted(set().union(*[atoms[a] for a in range(A) if x(a) in m])) if any(x(a) in m for a in range(A)) else []
        if split:  # self-check of the model: y proper on G - e and split satisfied
            yc = {g: [c for c in range(3) if y(g, c) in m] for g in range(n) if g != e}
            assert all(len(v) == 1 for v in yc.values())
            nn, E = cayley(G, S)
            assert all(yc[u][0] != yc[v][0] for (u, v) in E if e not in (u, v))
            assert all(sum(1 for t in S if yc[t][0] == c) >= r + 1 for c in range(3))
        nn, E = cayley(G, S)
        col = col3_with_bad(nn, E, r)
        if col is None:
            ok, msg = verify_4r_explicit(nn, E, r)
            line = f"{spec} order {n}: WITNESS degree {len(S)} S={[G.elems[t] for t in S]} explicit={ok} {msg} ({it} it, {time.time()-t0:.0f}s) [{tag}]"
            pass
            if log: open(log, "a").write(line + "\n")
            WIT.append((tuple(S), ok))
            chosen = set(a for a in range(A) if x(a) in m)
            s.add_clause([-x(a) if a in chosen else x(a) for a in range(A)])
            continue
        # counterexample colouring col of Gamma: every valid S' has >= r+1 edges monochromatic under col
        lits = []
        for a, atom in enumerate(atoms):
            cnt = 0
            for g in range(n):
                for t in atom:
                    h = G.table[g][t]
                    if h < g: continue
                    if col[g] == col[h]: cnt += 1
            lits += [x(a)] * cnt
        add(CardEnc.atleast(lits=lits, bound=r + 1, top_id=top, encoding=EncType.seqcounter))
        if it % 50 == 0: print(f"  {spec} it {it} deg {len(S)} {time.time()-t0:.0f}s", flush=True)
    print(f"{spec}: maxiter reached [{tag}]", flush=True); return "maxiter"

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    spec, r, dmin, dmax = args[0], int(args[1]), int(args[2]), int(args[3])
    run(spec, r, dmin, dmax, int(args[4]) if len(args) > 4 else 100000, log=None, split="--nosplit" not in sys.argv)
