"""Compare cegar944b.run against the independent reference ref944 (definition-level, all symmetric S enumerated)."""
import sys, io, re, time, contextlib, itertools, random
sys.path.insert(0, r'C:\Users\danie\Math\erdos944'); sys.path.insert(0, r'C:\Users\danie\Math\erdos944\review_tmp')
from ref944 import *
import search944, cegar944b

_cache = {}
def setup(spec):
    if spec in _cache: return _cache[spec]
    Th = search944.group_by_name(spec); M = parse(spec)
    phi = find_iso(M, Th.table, Th.e); assert phi is not None, spec
    inv_phi = {b: a for a, b in enumerate(phi)}
    R = Ref(M)
    _cache[spec] = (Th, M, phi, inv_phi, R); return _cache[spec]

def run_cegar(spec, r, dmin, dmax, atoms_theirs=None, maxiter=5000):
    orig = cegar944b.sym_closure_candidates
    if atoms_theirs is not None: cegar944b.sym_closure_candidates = lambda G: list(atoms_theirs)
    buf = io.StringIO(); t0 = time.time()
    try:
        with contextlib.redirect_stdout(buf):
            res = cegar944b.run(spec, r, dmin, dmax, maxiter=maxiter, log=None)
    finally:
        cegar944b.sym_closure_candidates = orig
    out = buf.getvalue(); it = None
    m = re.search(r"\((\d+) iterations", out) or re.search(r"\((\d+) it,", out)
    if m: it = int(m.group(1))
    return res, it, out.strip().splitlines()[-1] if out.strip() else "", time.time() - t0

def compare(spec, r, dmin, dmax, atom_subset_mine=None, split_diag=True, label=""):
    Th, M, phi, inv_phi, R = setup(spec)
    atoms_theirs = None
    if atom_subset_mine is not None:
        atoms_theirs = [frozenset(phi[g] for g in R.atoms[a]) for a in atom_subset_mine]
    try:
        res, it, last, tc = run_cegar(spec, r, dmin, dmax, atoms_theirs)
    except ValueError as ex:
        res, it, last, tc = "CRASH:" + str(ex), None, "", 0.0
    t0 = time.time(); nS = 0; wits = []; split_exists = None; nvc = 0
    for combo in enumerate_S(R, dmin, dmax, atom_subset_mine):
        nS += 1; Sat = set(combo)
        if not R.colourable(Sat, remove_e=True): continue
        nvc += 1
        if R.is_4r(Sat, r): wits.append(combo)
        if split_diag and not split_exists and R.split_feasible(Sat, r): split_exists = True
    if split_diag and split_exists is None: split_exists = False
    tr = time.time() - t0
    problems = []
    if res == "maxiter": verdict = "MAXITER"
    elif isinstance(res, str) and res.startswith("CRASH"): verdict = res.replace(" ", "_")
    elif res is None:
        verdict = "NO"
        if wits: problems.append(f"BLOCKER wrong NO: reference has {len(wits)} witnesses e.g. {[sorted(R.atoms[a]) for a in wits[0]]}")
    else:
        verdict = f"WITNESS deg {len(res)}"
        Sm = sorted(inv_phi[s] for s in res); Sat = {R.atom_of[s] for s in Sm}
        deg = len(set().union(*[R.atoms[a] for a in Sat])) if Sat else 0
        if set(Sm) != set().union(*[R.atoms[a] for a in Sat]): problems.append("BLOCKER witness S not symmetric")
        if not (dmin <= deg <= dmax): problems.append(f"BLOCKER witness degree {deg} out of range")
        if atom_subset_mine is not None and not Sat <= set(atom_subset_mine): problems.append("BLOCKER witness uses excluded atom")
        if not R.is_4r(Sat, r): problems.append("BLOCKER witness fails reference is_4r")
        if not wits: problems.append("BLOCKER witness but reference found none")
    if split_diag and it is not None and res is None:
        if (it == 1) != (not split_exists): problems.append(f"SPLIT-DIAG mismatch: cegar iterations={it}, reference split-feasible exists={split_exists}")
    if split_diag and wits and not split_exists: problems.append("SPLIT unsound?: witnesses exist but none split-feasible")
    line = (f"{label}{spec:10s} r={r} deg[{dmin},{dmax}] cegar={verdict} it={it} ({tc:.1f}s) | ref: {nS} S, {nvc} G-e 3col, "
            f"{len(wits)} witnesses, split-feasible={'yes' if split_exists else 'no' if split_exists is not None else '-'} ({tr:.1f}s)")
    print(line + ("  <<< " + "; ".join(problems) if problems else "  OK"), flush=True)
    return problems

def count_S(spec, dmin, dmax):
    Th, M, phi, inv_phi, R = setup(spec)
    return sum(1 for _ in enumerate_S(R, dmin, dmax))

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "count":
        for spec in sys.argv[4:]:
            print(spec, count_S(spec, int(sys.argv[2]), int(sys.argv[3])), flush=True)
    elif mode == "cmp":
        r, dmin, dmax = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        allp = []
        for spec in sys.argv[5:]: allp += compare(spec, r, dmin, dmax)
        print("TOTAL problems:", len(allp))
