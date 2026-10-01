"""Version s: the exact CEGAR search of cegar944c.py restricted to connection sets S fixed by a group automorphism sigma.

Family.  sigma is an automorphism of Gamma of prime order p.  Every automorphism maps inverse pairs to inverse pairs, so it
permutes the atoms of cegar944c (involutions and inverse pairs); a sigma-invariant S is a union of sigma-orbits of atoms
("sigma-atoms").  The search below is cegar944c with the atoms replaced by sigma-atoms.
Completeness of the lane.  A (4,r)-graph is connected, so a witness S generates Gamma and an automorphism fixing S pointwise
is the identity: Stab_Aut(S) acts faithfully on S.  If Stab_Aut(S) != 1 it contains an element tau of prime order p <= |S|.
tau = phi sigma phi^-1 for the representative sigma of its Aut-conjugacy class, and then phi^-1(S) is sigma-invariant and
Cay(Gamma, phi^-1(S)) is isomorphic to Cay(Gamma, S).  So running every class representative sigma of prime order p <= dmax
finds (an isomorphic copy of) every Cayley witness with a nontrivial stabiliser in Aut(Gamma), and nothing else is claimed.
Symmetry breaking.  For phi in the normaliser N of <sigma>, phi(S) is again sigma-invariant (phi sigma phi^-1 is a power of
sigma) and gives an isomorphic graph, so the lex-leader constraints x <=_lex x o pi_phi over the sigma-atom permutations
pi_phi, phi in N, keep at least one member of every N-orbit of sigma-invariant witnesses (the lexicographically smallest).
Extra constraints on the colouring y of Gamma - e (all sound, each behind a flag):
  * colsym: y(g0) = 0 and y(g1) in {0, 1} for the first two non-identity elements g0, g1 (rename colours; the split
    constraint and properness are invariant under renaming);
  * cut weights capped at r+1: sum_a w_a x_a >= r+1  <=>  sum_a min(w_a, r+1) x_a >= r+1 for 0/1 variables (same constraint,
    much smaller encoding);
  * cut persistence: every counterexample colouring of Gamma (a 3-colouring with <= r monochromatic edges for the current
    candidate) is appended to cuts/<group>_r<r>.<tag>.txt; on start all cut files of the same group and r are replayed.  A cut
    says "S has >= r+1 edges monochromatic under col", which every (4,r)-witness satisfies, for any S, sigma and degree.
Usage:
  python cegar944s.py GROUP --list [dmax]                    list prime-order automorphism classes (index, order, size, #sigma-atoms)
  python cegar944s.py GROUP r dmin dmax --sigma K [--nocolsym] [--nocuts] [--enum] [--cubes]   (K = class index, or 'id' for sigma = 1)
"""
import sys, os, time, glob, hashlib
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from c944 import cayley, col3_with_bad, verify_4r_explicit
from search944 import sym_closure_candidates
from auto944 import automorphisms
import groups944

HERE = os.path.dirname(os.path.abspath(__file__))
MAXAUT = 20000
MAXREPLAY = 3000       # at most this many distinct stored cuts are replayed at start (the newest ones)

def perm_order(p):
    k, q = 1, p
    ident = tuple(range(len(p)))
    while q != ident: q = tuple(p[i] for i in q); k += 1
    return k

def is_prime(k): return k > 1 and all(k % d for d in range(2, int(k ** 0.5) + 1))

def aut_data(G):
    auts, _ = automorphisms(G, limit=MAXAUT + 1)
    if len(auts) > MAXAUT: raise RuntimeError(f"|Aut| > {MAXAUT}: refusing (classes would be incomplete)")
    auts = [tuple(a) for a in auts]
    assert len(set(auts)) == len(auts)
    return auts

def prime_classes(G, auts, pmax=None):
    """Conjugacy classes (in Aut) of automorphisms of prime order (all primes; the numbering does not depend on any degree
    bound -- pmax is ignored and kept only for old callers); deterministic order.  Returns [(sigma, p, size)], inv."""
    inv = {a: tuple(sorted(range(G.n), key=lambda g: a[g])) for a in auts}      # a^-1 as a tuple: inv[a][a[g]] = g
    for a in auts: assert all(inv[a][a[g]] == g for g in range(G.n))
    seen = set(); out = []
    for s in auts:
        if s in seen: continue
        p = perm_order(s)
        if not is_prime(p): continue
        cls = {tuple(f[s[inv[f][g]]] for g in range(G.n)) for f in auts}        # f s f^-1
        seen |= cls; out.append((s, p, len(cls)))
    return out, inv

def sigma_atoms(G, sigma):
    atoms = sym_closure_candidates(G)
    if sigma is None: return atoms
    idx = {a: k for k, a in enumerate(atoms)}
    done = set(); out = []
    for a in atoms:
        if a in done: continue
        orb = [a]; b = frozenset(sigma[t] for t in a)
        while b != a: orb.append(b); b = frozenset(sigma[t] for t in b)
        assert all(o in idx for o in orb)
        done |= set(orb); out.append(frozenset().union(*orb))
    return out

def normaliser(G, auts, inv, sigma):
    if sigma is None: return auts
    powers = set(); q = sigma
    while True:
        powers.add(q)
        q = tuple(sigma[q[g]] for g in range(G.n))
        if q == sigma: break
    return [f for f in auts if tuple(f[sigma[inv[f][g]]] for g in range(G.n)) in powers]

def fingerprint(sigma): return "id" if sigma is None else hashlib.sha1(repr(tuple(sigma)).encode()).hexdigest()[:8]

def run(spec, r, dmin, dmax, sigma_k, colsym=True, cuts=True, enum_all=False, log=None, tag=None, record=True, cubes=False, progress=True):
    """record=False: never write WITNESSES.txt (validation runs)."""
    G = groups944.get(spec); n = G.n; e = G.e; t0 = time.time()
    auts = aut_data(G)
    if sigma_k == 'id':
        sigma = None; label = "sigma=id"; N = auts
    else:
        classes, inv = prime_classes(G, auts)
        sigma, p, size = classes[int(sigma_k)]
        label = f"sigma={sigma_k} (order {p}, class size {size}, fp {fingerprint(sigma)})"
        if p > dmax:        # a sigma of prime order p > |S| cannot fix a witness S (Stab(S) acts faithfully on S)
            print(f"{spec} order {n}: SKIP {label}: order {p} > dmax {dmax}, not needed", flush=True)
            return [] if enum_all else None
        N = normaliser(G, auts, inv, sigma)
    atoms = sigma_atoms(G, sigma); A = len(atoms)
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
        for c1 in range(3):
            for c2 in range(c1 + 1, 3): s.add_clause([-y(g, c1), -y(g, c2)])
    if colsym:
        others = [g for g in range(n) if g != e]
        s.add_clause([y(others[0], 0)]); s.add_clause([y(others[1], 0), y(others[1], 1)])
    for a, atom in enumerate(atoms):
        for g in range(n):
            if g == e: continue
            for t in atom:
                h = G.table[g][t]
                if h == e or h < g: continue
                for c in range(3): s.add_clause([-x(a), -y(g, c), -y(h, c)])
    wl = []
    for a, atom in enumerate(atoms): wl += [x(a)] * len(atom)
    if dmin > 0: add(CardEnc.atleast(lits=wl, bound=dmin, top_id=top, encoding=EncType.seqcounter))
    add(CardEnc.atmost(lits=wl, bound=dmax, top_id=top, encoding=EncType.seqcounter))
    for c in range(3):                      # neighbourhood split (as in cegar944b/c)
        zs = []
        for a, atom in enumerate(atoms):
            for t in atom:
                top += 1; z = top; zs.append(z)
                s.add_clause([-z, x(a)]); s.add_clause([-z, y(t, c)])
        add(CardEnc.atleast(lits=zs, bound=r + 1, top_id=top, encoding=EncType.seqcounter))
    idx = {a: k for k, a in enumerate(atoms)}
    perms = set()
    for f in N:
        perms.add(tuple(idx[frozenset(f[t] for t in a)] for a in atoms))
    perms.discard(tuple(range(A)))
    for pi in perms:                        # lex-leader, as in cegar944c
        prev = None
        for i in range(A):
            if pi[i] == i: continue
            xi, yi = x(i), x(pi[i])
            s.add_clause([-xi, yi] + ([-prev] if prev else []))
            if i == A - 1: break
            top += 1; nxt = top; base = [-prev] if prev else []
            s.add_clause(base + [-xi, -yi, nxt]); s.add_clause(base + [xi, yi, nxt])
            prev = nxt
    def cut_lits(col):
        lits = []
        for a, atom in enumerate(atoms):
            cnt = 0
            for g in range(n):
                for t in atom:
                    h = G.table[g][t]
                    if h < g: continue
                    if col[g] == col[h]: cnt += 1
            lits += [x(a)] * min(cnt, r + 1)
        return lits
    def add_cut(col):
        lits = cut_lits(col)
        if len(lits) < r + 1: s.add_clause([]); return        # no candidate can satisfy it: UNSAT
        add(CardEnc.atleast(lits=lits, bound=r + 1, top_id=top, encoding=EncType.seqcounter))
    safe = spec.replace("|", "_")
    cutfile = None; ncut0 = 0
    if cuts:
        os.makedirs(os.path.join(HERE, "cuts"), exist_ok=True)
        pool = []; seen_cuts = set()                          # distinct stored cuts, newest files last
        for fn in sorted(glob.glob(os.path.join(HERE, "cuts", f"{safe}_r{r}.*.txt")), key=os.path.getmtime):
            for line in open(fn):
                line = line.strip()
                if len(line) == n and set(line) <= set("012") and line not in seen_cuts: seen_cuts.add(line); pool.append(line)
        for line in pool[-MAXREPLAY:]:                         # replaying fewer cuts is still sound (weaker constraints)
            add_cut([int(ch) for ch in line]); ncut0 += 1
        cutfile = os.path.join(HERE, "cuts", f"{safe}_r{r}.{tag or f'd{dmin}-{dmax}_s{sigma_k}_{os.getpid()}'}.txt")
    stag = f"s {label}" + ("" if colsym else " nocolsym") + ("" if cuts else " nocuts")
    print(f"{spec} order {n}: |Aut|={len(auts)} {label} |N|={len(N)} atoms={A} lex-perms={len(perms)} replayed cuts={ncut0}  [{time.time()-t0:.0f}s]", flush=True)
    found = []; it = 0
    def handle(m):
        """Process one model: witness -> return S (non-enum) or record + block (enum); otherwise add the cut.  Returns S or None."""
        chosen = [a for a in range(A) if x(a) in m]
        S = sorted(set().union(*[atoms[a] for a in chosen])) if chosen else []
        yc = {g: [c for c in range(3) if y(g, c) in m] for g in range(n) if g != e}
        assert all(len(v) == 1 for v in yc.values())
        nn, E = cayley(G, S)
        assert all(yc[u][0] != yc[v][0] for (u, v) in E if e not in (u, v))
        assert all(sum(1 for t in S if yc[t][0] == c) >= r + 1 for c in range(3))
        assert dmin <= len(S) <= dmax
        if sigma is not None: assert set(sigma[t] for t in S) == set(S)
        col = col3_with_bad(nn, E, r)
        if col is None:
            # save the candidate BEFORE the (slow for r = 2) explicit check, so a time cap cannot lose it
            cand = f"{spec} order {n}: CANDIDATE (4,{r}) degree {len(S)} S={[G.elems[t] for t in S]} S_idx={S} ({it} it, {time.time()-t0:.0f}s) [{stag}]"
            print(cand, flush=True)
            if log: open(log, "a").write(cand + "\n")
            if record and not enum_all:
                with open(os.path.join(HERE, "WITNESSES.txt"), "a") as f: f.write(cand + "\n"); f.flush(); os.fsync(f.fileno())
            ok, msg = verify_4r_explicit(nn, E, r)
            line = f"{spec} order {n}: WITNESS (4,{r}) degree {len(S)} S={[G.elems[t] for t in S]} explicit={ok} {msg} ({it} it, {time.time()-t0:.0f}s) [{stag}]"
            print(line, flush=True)
            if log: open(log, "a").write(line + "\n")
            if not enum_all:
                if record:
                    with open(os.path.join(HERE, "WITNESSES.txt"), "a") as f: f.write(line + "\n"); f.flush(); os.fsync(f.fileno())
                s.delete(); return S
            found.append(S)
            s.add_clause([-x(a) for a in chosen] + [x(a) for a in range(A) if a not in chosen])
            return None
        if cutfile:
            with open(cutfile, "a") as f: f.write("".join(str(c) for c in col) + "\n"); f.flush()
        add_cut(col)
        if it % 50 == 0: print(f"  {spec} it {it} deg {len(S)} {time.time()-t0:.0f}s", flush=True)
        return None
    # Cubes (cubes=True): the chosen sigma-atom sets are split by their smallest members -- cube (i,) = "exactly atom i",
    # cube (i, j) = "i < j are the two smallest chosen atoms" (x_k = 0 for k < j, k != i).  Every nonempty set lies in exactly
    # one cube, so the lane is NO iff every cube is UNSAT.  Cubes are solved one after another on the same (incremental)
    # solver via assumptions; cuts are global.  With progress=True every finished cube is appended (fsync) to
    # progress/<group>_r<r>_d<dmin>-<dmax>_s<k>.txt and skipped on restart, so a break loses at most the current cube.
    prog = None; done_cubes = set()
    if cubes:
        cube_list = [(i,) for i in range(A)] + [(i, j) for j in range(A) for i in range(j)]
        if progress and not enum_all:     # never in enum mode: there a cube's "NO" would hide the witnesses it contained
            # the file name pins sigma (fingerprint) and the atom count, so a file can only be reused for the same lane
            prog = os.path.join(HERE, "progress", f"{safe}_r{r}_d{dmin}-{dmax}_s{sigma_k}_fp{fingerprint(sigma)}_A{A}.txt")
            os.makedirs(os.path.dirname(prog), exist_ok=True)
            valid = {",".join(map(str, c)) for c in cube_list}
            if os.path.exists(prog):
                for l in open(prog):
                    f4 = l.split()
                    if len(f4) == 4 and f4[1] == "NO" and f4[0] in valid and f4[2].isdigit() and f4[3].isdigit(): done_cubes.add(f4[0])
        print(f"  {len(cube_list)} cubes, {len(done_cubes)} already done", flush=True)
    else:
        cube_list = [None]
    ndone = 0
    for cube in cube_list:
        key = None if cube is None else ",".join(map(str, cube))
        if key in done_cubes: ndone += 1; continue
        if cube is None: assum = []
        elif len(cube) == 1: assum = [x(cube[0])] + [-x(k) for k in range(A) if k != cube[0]]
        else: assum = [x(cube[0]), x(cube[1])] + [-x(k) for k in range(cube[1]) if k != cube[0]]
        res = None
        while True:
            it += 1
            if not s.solve(assumptions=assum): break
            res = handle(set(l for l in s.get_model() if l > 0))
            if res is not None and not enum_all: return res
        ndone += 1
        if prog:
            with open(prog, "a") as f: f.write(f"{key} NO {it} {time.time()-t0:.0f}\n"); f.flush(); os.fsync(f.fileno())
        if cube is not None and ndone % 500 == 0: print(f"  {spec} cubes done {ndone}/{len(cube_list)}, it {it}, {time.time()-t0:.0f}s", flush=True)
    ctag = f" cubes={len(cube_list)}" if cubes else ""
    if enum_all and found:
        msg = f"{spec} order {n}: ENUM DONE: {len(found)} (4,{r}) witness(es) with degree in [{dmin},{dmax}]  ({it} iterations, {time.time()-t0:.0f}s) [{stag}{ctag}]"
    else:
        msg = f"{spec} order {n}: NO (4,{r})-Cayley graph with degree in [{dmin},{dmax}]  ({it} iterations, {time.time()-t0:.0f}s) [{stag}{ctag}]"
    print(msg, flush=True)
    if log: open(log, "a").write(msg + "\n")
    if prog:
        with open(prog, "a") as f: f.write(f"COMPLETE {msg}\n"); f.flush(); os.fsync(f.fileno())
    s.delete(); return found if enum_all else None

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--list" in sys.argv:
        spec = args[0]; dmax = int(args[1]) if len(args) > 1 else None
        G = groups944.get(spec); auts = aut_data(G); classes, inv = prime_classes(G, auts)
        print(f"{spec} order {G.n} |Aut|={len(auts)} atoms={len(sym_closure_candidates(G))}")
        for k, (sg, p, size) in enumerate(classes):
            need = "" if dmax is None else ("  needed" if p <= dmax else f"  not needed for dmax {dmax}")
            print(f"  class {k}: order {p}, size {size}, sigma-atoms {len(sigma_atoms(G, sg))}, |N|={len(normaliser(G, auts, inv, sg))}, fp {fingerprint(sg)}{need}")
        sys.exit(0)
    spec, r, dmin, dmax = args[0], int(args[1]), int(args[2]), int(args[3])
    k = sys.argv[sys.argv.index("--sigma") + 1] if "--sigma" in sys.argv else "id"
    run(spec, r, dmin, dmax, k, colsym="--nocolsym" not in sys.argv, cuts="--nocuts" not in sys.argv, enum_all="--enum" in sys.argv,
        cubes="--cubes" in sys.argv)
