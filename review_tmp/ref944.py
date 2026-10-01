"""Independent reference for (4,r)-Cayley graphs (review of cegar944b).  Shares NO code with c944/search944/cegar944b.
Groups: built independently (permutations / complex matrices / affine maps), identity relabelled to index 0.
(4,r) test by definition with plain SAT 3-colourability (Glucose4, assumptions only, no cardinality encodings):
  G - e 3-colourable (vertex-transitive => vertex-critical), G not 3-colourable, and G - F not 3-colourable for all
  |F| <= r; by left-translation symmetry F may be assumed to contain an edge {e, s} (s one rep per atom of S).
"""
import itertools, cmath
from pysat.solvers import Glucose4

# ---------------- groups ----------------
class Grp:
    def __init__(self, gens, mul, ident, name):
        elems = [ident]; seen = {ident: 0}; i = 0
        while i < len(elems):
            x = elems[i]; i += 1
            for g in gens:
                y = mul(x, g)
                if y not in seen: seen[y] = len(elems); elems.append(y)
        self.elems = elems; self.n = len(elems); self.name = name
        self.T = [[seen[mul(a, b)] for b in elems] for a in elems]
        self.e = 0
        self.inv = [self.T[a].index(0) for a in range(self.n)]
    def order(self, g):
        k, x = 1, g
        while x != 0: x = self.T[x][g]; k += 1
        return k

def cyc(n): return Grp([1 % n], lambda a, b: (a + b) % n, 0, f"Z{n}")
def perm_mul(p, q): return tuple(p[i] for i in q)     # p o q  (apply q first)
def dih(n):
    rot = tuple((i + 1) % n for i in range(n)); ref = tuple((-i) % n for i in range(n))
    return Grp([rot, ref], perm_mul, tuple(range(n)), f"D{n}")
def symm(n):
    gens = [tuple([1, 0] + list(range(2, n))), tuple(list(range(1, n)) + [0])]
    return Grp(gens, perm_mul, tuple(range(n)), f"S{n}")
def altn(n):
    # all 3-cycles (0 1 k) generate A_n
    gens = []
    for k in range(2, n):
        p = list(range(n)); p[0], p[1], p[k] = 1, k, 0; gens.append(tuple(p))
    return Grp(gens, perm_mul, tuple(range(n)), f"A{n}")
def dicyc(n):
    # exact 2x2 monomial matrices, entries None (=0) or exponent k meaning zeta^k, zeta = primitive 2n-th root of 1
    N2 = 2 * n
    def mm(A, B):
        out = []
        for i in range(2):
            for k in range(2):
                terms = [(A[2 * i + j] + B[2 * j + k]) % N2 for j in range(2) if A[2 * i + j] is not None and B[2 * j + k] is not None]
                assert len(terms) <= 1
                out.append(terms[0] if terms else None)
        return tuple(out)
    a = (1, None, None, N2 - 1)          # diag(zeta, zeta^-1)
    x = (None, n, 0, None)               # [[0,-1],[1,0]]
    I = (0, None, None, 0)
    return Grp([a, x], mm, I, f"Dic{n}")
def semi(m, n, t):
    # permutations of Z_m (disjoint union) Z_n : alpha: x->x+1 on Z_m ; beta: x->t x on Z_m and y->y+1 on Z_n
    N = m + n
    al = tuple([(x + 1) % m for x in range(m)] + [m + y for y in range(n)])
    be = tuple([(t * x) % m for x in range(m)] + [m + (y + 1) % n for y in range(n)])
    return Grp([al, be], perm_mul, tuple(range(N)), f"Z{m}x|{t}Z{n}")
def dprod(A, B):
    gens = [(g, 0) for g in range(A.n)] + [(0, h) for h in range(B.n)]
    return Grp(gens, lambda x, y: (A.T[x[0]][y[0]], B.T[x[1]][y[1]]), (0, 0), f"{A.name}x{B.name}")

def parse(spec):
    def one(s):
        if s.startswith("Dic"): return dicyc(int(s[3:]))
        if s.startswith("D"): return dih(int(s[1:]))
        if s.startswith("S"): return symm(int(s[1:]))
        if s.startswith("A"): return altn(int(s[1:]))
        if "x|" in s:
            a, b = s.split("x|"); t, nn = b.split("Z"); return semi(int(a[1:]), int(nn), int(t))
        return cyc(int(s[1:]))
    if "x|" in spec:
        i = spec.find("x|"); j = spec.find("xZ", i + 2)
        parts = [spec] if j < 0 else [spec[:j], spec[j + 1:]]
    else:
        parts = spec.split("x")
    G = one(parts[0])
    for p in parts[1:]: G = dprod(G, one(p))
    G.name = spec
    return G

# ---------------- table checks and isomorphism ----------------
def is_group_table(T):
    n = len(T); rng = range(n)
    e = [i for i in rng if all(T[i][j] == j and T[j][i] == j for j in rng)]
    if len(e) != 1: return False, "identity"
    e = e[0]
    for a in rng:
        if sorted(T[a]) != list(rng): return False, "latin row"
        if not any(T[a][b] == e for b in rng): return False, "inverse"
    for a in rng:
        Ta = T[a]
        for b in rng:
            ab = Ta[b]; Tab = T[ab]; Tb = T[b]
            for c in rng:
                if Tab[c] != Ta[Tb[c]]: return False, f"assoc {a},{b},{c}"
    return True, "ok"

def orders(T, e):
    n = len(T); out = []
    for g in range(n):
        k, x = 1, g
        while x != e: x = T[x][g]; k += 1
        out.append(k)
    return out

def find_iso(A, B_T, B_e):
    """isomorphism phi: A -> B (index maps), or None.  A is a Grp, B given by table and identity."""
    n = A.n
    if len(B_T) != n: return None
    oa = [A.order(g) for g in range(n)]; ob = orders(B_T, B_e)
    if sorted(oa) != sorted(ob): return None
    # small generating set of A, greedy by element order
    gens = []; H = {0}
    def gen_closure(gs):
        H = {0}; fr = [0]
        while fr:
            nx = []
            for x in fr:
                for g in gs:
                    y = A.T[x][g]
                    if y not in H: H.add(y); nx.append(y)
            fr = nx
        return H
    for g in sorted(range(n), key=lambda g: -oa[g]):
        if g not in H:
            gens.append(g); H = gen_closure(gens)
        if len(H) == n: break
    # word for every element: BFS tree
    parent = {0: None}; fr = [0]; order_list = [0]
    while fr:
        nx = []
        for x in fr:
            for gi, g in enumerate(gens):
                y = A.T[x][g]
                if y not in parent: parent[y] = (x, gi); nx.append(y); order_list.append(y)
        fr = nx
    cands = [[b for b in range(n) if ob[b] == oa[g]] for g in gens]
    for imgs in itertools.product(*cands):
        phi = {0: B_e}
        for y in order_list[1:]:
            x, gi = parent[y]; phi[y] = B_T[phi[x]][imgs[gi]]
        if len(set(phi.values())) != n: continue
        if all(phi[A.T[a][b]] == B_T[phi[a]][phi[b]] for a in range(n) for b in range(n)):
            return [phi[i] for i in range(n)]
    return None

# ---------------- reference (4,r) checker ----------------
class Ref:
    def __init__(self, G):
        self.G = G; n = G.n; T = G.T
        atoms = []; atom_of = [None] * n
        for g in range(1, n):
            if atom_of[g] is None:
                a = frozenset([g, G.inv[g]]); atom_of[g] = atom_of[G.inv[g]] = len(atoms); atoms.append(a)
        self.atoms = atoms; self.atom_of = atom_of; A = len(atoms)
        self.col = lambda v, c: 3 * v + c + 1
        self.sel = lambda a: 3 * n + a + 1
        self.keep = 3 * n + A + 1
        self.pairs = [(g, h) for g in range(n) for h in range(g + 1, n)]
        self.rem = {p: 3 * n + A + 2 + i for i, p in enumerate(self.pairs)}
        s = Glucose4()
        s.add_clause([-self.keep] + [self.col(0, c) for c in range(3)])
        for v in range(1, n): s.add_clause([self.col(v, c) for c in range(3)])
        for (g, h) in self.pairs:
            a = atom_of[T[G.inv[g]][h]]
            for c in range(3): s.add_clause([-self.sel(a), -self.col(g, c), -self.col(h, c), self.rem[(g, h)]])
        self.s = s
    def edges(self, Sat):
        G = self.G; out = set()
        for a in Sat:
            for t in self.atoms[a]:
                for g in range(G.n):
                    h = G.T[g][t]; out.add((min(g, h), max(g, h)))
        return sorted(out)
    def colourable(self, Sat, remove_e=False, F=()):
        Fs = set(F)
        ass = [self.sel(a) if a in Sat else -self.sel(a) for a in range(len(self.atoms))]
        ass.append(-self.keep if remove_e else self.keep)
        ass += [self.rem[p] if p in Fs else -self.rem[p] for p in self.pairs]
        return self.s.solve(assumptions=ass)
    def is_4r(self, Sat, r):
        Sat = set(Sat)
        if not self.colourable(Sat, remove_e=True): return False
        if self.colourable(Sat): return False
        if r == 0: return True
        E = self.edges(Sat)
        for a in Sat:
            s0 = min(self.atoms[a]); f0 = (0, s0)
            if self.colourable(Sat, F=[f0]): return False
            if r >= 2:
                for f in E:
                    if f != f0 and self.colourable(Sat, F=[f0, f]): return False
            if r >= 3: raise NotImplementedError
        return True
    def full_verify(self, Sat, r):
        """no symmetry: every vertex removal colourable, every F with |F| <= r non-colourable (r <= 2)."""
        Sat = set(Sat); n = self.G.n; E = self.edges(Sat)
        # vertex v removal: use a fresh plain solver
        for v in range(n):
            s = Glucose4()
            for u in range(n):
                if u != v: s.add_clause([self.col(u, c) for c in range(3)])
            for (g, h) in E:
                if v in (g, h): continue
                for c in range(3): s.add_clause([-self.col(g, c), -self.col(h, c)])
            ok = s.solve(); s.delete()
            if not ok: return False, f"G-{v} not 3-col"
        for k in range(0, r + 1):
            for F in itertools.combinations(E, k):
                if self.colourable(Sat, F=F): return False, f"critical F={F}"
        return True, "ok"
    def split_feasible(self, Sat, r):
        """proper 3-colouring of G - e (exactly one colour per vertex) with each colour on >= r+1 elements of S.
        naive 'at least k of L' encoding: every (L-k+1)-subset contains a true literal."""
        G = self.G; n = G.n; S = sorted(set().union(*[self.atoms[a] for a in Sat])); E = self.edges(set(Sat))
        s = Glucose4(); col = self.col
        for v in range(1, n):
            s.add_clause([col(v, c) for c in range(3)])
            for c1 in range(3):
                for c2 in range(c1 + 1, 3): s.add_clause([-col(v, c1), -col(v, c2)])
        for (g, h) in E:
            if 0 in (g, h): continue
            for c in range(3): s.add_clause([-col(g, c), -col(h, c)])
        L = len(S); k = r + 1
        if k > L: s.delete(); return False
        for c in range(3):
            for sub in itertools.combinations(S, L - k + 1): s.add_clause([col(t, c) for t in sub])
        ok = s.solve(); s.delete(); return ok

def enumerate_S(ref, dmin, dmax, atom_subset=None):
    atoms = ref.atoms; idx = list(range(len(atoms))) if atom_subset is None else list(atom_subset)
    for k in range(0, len(idx) + 1):
        for combo in itertools.combinations(idx, k):
            d = sum(len(atoms[a]) for a in combo)
            if dmin <= d <= dmax: yield combo
