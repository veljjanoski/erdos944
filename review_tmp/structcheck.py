"""Record the CNF built by cegar944b.run and check it structurally and semantically against independent computations."""
import sys, random, itertools
sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
import cegar944b
from pysat.solvers import Cadical153 as RealCad
from c944 import cayley
from search944 import group_by_name, sym_closure_candidates

class Rec:
    inst = []
    def __init__(self, *a, **k):
        self.s = RealCad(); self.clauses = []; self.solves = []; self.col_calls = []
        Rec.inst.append(self)
    def add_clause(self, cl):
        self.clauses.append(list(cl)); self.s.add_clause(cl)
    def solve(self, *a, **k):
        self.solves.append(len(self.clauses)); return self.s.solve(*a, **k)
    def get_model(self): return self.s.get_model()
cegar944b.Cadical153 = Rec
cols = []
orig_col3 = cegar944b.col3_with_bad
def rec_col3(n, E, t, *a, **k):
    c = orig_col3(n, E, t, *a, **k); cols.append(c); return c
cegar944b.col3_with_bad = rec_col3

def indep_feasible(G, S, r, split):
    """exists proper 3-colouring of Cay(G,S)-e with each colour on >= r+1 elements of S (split) -- plain SAT, assignments enumerated"""
    n, E = cayley(G, S); e = G.e
    v = lambda g, c: 3 * g + c + 1
    s = RealCad()
    for g in range(n):
        if g == e: continue
        s.add_clause([v(g, c) for c in range(3)])
        for c1, c2 in itertools.combinations(range(3), 2): s.add_clause([-v(g, c1), -v(g, c2)])
    for (a, b) in E:
        if e in (a, b): continue
        for c in range(3): s.add_clause([-v(a, c), -v(b, c)])
    if not split:
        ok = s.solve(); s.delete(); return ok
    for assign in itertools.product(range(3), repeat=len(S)):
        if min(assign.count(c) for c in range(3)) < r + 1: continue
        if s.solve(assumptions=[v(t, c) for t, c in zip(S, assign)]): s.delete(); return True
    s.delete(); return False

def check(spec, r, dmin, dmax, split, nsamp=300, seed=0):
    rnd = random.Random(seed)
    Rec.inst.clear(); cols.clear()
    G = group_by_name(spec); atoms = sym_closure_candidates(G); A = len(atoms); n = G.n; e = G.e
    res = cegar944b.run(spec, r, dmin, dmax, maxiter=2, log=None, split=split)
    R = Rec.inst[-1]
    base = R.clauses[:R.solves[0]]
    x = lambda a: a + 1; y = lambda g, c: A + 3 * g + c + 1
    problems = []
    # structural: edge clauses
    edge_cl = set()
    for cl in base:
        if len(cl) == 3 and all(l < 0 for l in cl) and -cl[0] <= A:
            a = -cl[0] - 1; u = (-cl[1] - A - 1) // 3; cu = (-cl[1] - A - 1) % 3; w = (-cl[2] - A - 1) // 3; cw = (-cl[2] - A - 1) % 3
            if cu != cw: problems.append(("edge clause colour mismatch", cl)); continue
            edge_cl.add((a, min(u, w), max(u, w), cu))
    want = set()
    for a, atom in enumerate(atoms):
        _, E = cayley(G, sorted(atom))
        for (u, w) in E:
            if e in (u, w): continue
            for c in range(3): want.add((a, u, w, c))
    if edge_cl != want: problems.append(("edge clauses differ", len(edge_cl - want), len(want - edge_cl)))
    # variable ranges: aux vars must be > A + 3n
    maxv = max(abs(l) for cl in R.clauses for l in cl)
    # semantic check of base formula over sampled / all S
    s = RealCad(bootstrap_with=base)
    subsets = []
    if A <= 12:
        for k in range(0, A + 1):
            subsets += list(itertools.combinations(range(A), k))
    else:
        for _ in range(nsamp):
            k = rnd.randint(1, A); subsets.append(tuple(sorted(rnd.sample(range(A), k))))
    mism = 0; nsat = 0; tested = 0
    for sub in subsets:
        S = sorted(set().union(*[atoms[a] for a in sub])) if sub else []
        d = len(S)
        if split and not (dmin <= d <= dmax and len(S) <= 13) and (dmin <= d <= dmax): continue  # too many assignments to enumerate
        want_ok = dmin <= d <= dmax and indep_feasible(G, S, r, split)
        got = s.solve(assumptions=[x(a) if a in sub else -x(a) for a in range(A)])
        tested += 1; nsat += got
        if got != want_ok:
            mism += 1
            if mism <= 3: problems.append(("semantic mismatch", [G.elems[t] for t in S], "want", want_ok, "got", got))
    s.delete()
    # cut semantics (if one was added)
    cutinfo = "no cut"
    if len(R.solves) >= 2 and cols and cols[0] is not None:
        col = cols[0]; cut = R.clauses[R.solves[0]:R.solves[1]]
        s2 = RealCad(bootstrap_with=cut); cm = 0
        for sub in subsets[:400]:
            S = sorted(set().union(*[atoms[a] for a in sub])) if sub else []
            _, E = cayley(G, S) if S else (n, [])
            mono = sum(1 for (u, w) in E if col[u] == col[w])
            got = s2.solve(assumptions=[x(a) if a in sub else -x(a) for a in range(A)])
            if got != (mono >= r + 1):
                cm += 1
                if cm <= 3: problems.append(("cut mismatch", S, mono, got))
        s2.delete(); cutinfo = f"cut checked on {min(400, len(subsets))} S, {cm} mismatches"
    print(f"{spec} r={r} [{dmin},{dmax}] split={split}: A={A} result={'NO' if res is None else res} tested={tested} sat={nsat} {cutinfo} maxvar={maxv} problems={problems}", flush=True)

if __name__ == "__main__":
    for spec in ["Z7", "Z8", "Z9", "Z10", "Z11", "Z12", "Z13", "D5", "D6", "Dic3", "A4", "Z2xZ6", "Z3xZ3", "Z2xZ2xZ2", "Z7x|2Z3", "S4", "Z5x|2Z4"]:
        for (r, dmin, dmax) in [(0, 1, 30), (1, 4, 9), (2, 6, 12)]:
            for split in (True, False):
                check(spec, r, dmin, dmax, split)
