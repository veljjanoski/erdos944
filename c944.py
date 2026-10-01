"""Erdős #944, case k = 4.  A (4,r)-graph is 4-vertex-critical (chi = 4, chi(G - v) = 3 for all v) and has no
critical edge set of size <= r, i.e. every 3-colouring of G has at least r + 1 monochromatic edges.
d3(G) := min number of monochromatic edges over all 3-colourings ("3-defect");  (4,r)-graph <=> vertex-critical and d3 >= r+1.

Groups are multiplication tables (list of lists), Cayley graphs use right multiplication g ~ g*s, s in S = S^-1.
"""
import itertools, sys
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType

# ---------- groups as multiplication tables ----------
class Group:
    def __init__(self, elems, mul, name):
        self.elems = list(elems); self.idx = {e: i for i, e in enumerate(self.elems)}; self.n = len(self.elems)
        self.table = [[self.idx[mul(a, b)] for b in self.elems] for a in self.elems]
        self.name = name
        self.e = next(i for i in range(self.n) if all(self.table[i][j] == j for j in range(self.n)))
        self.inv = [next(j for j in range(self.n) if self.table[i][j] == self.e) for i in range(self.n)]
    def order(self, g):
        k, x = 1, g
        while x != self.e: x = self.table[x][g]; k += 1
        return k

def cyclic(n): return Group(range(n), lambda a, b: (a + b) % n, f"Z{n}")
def direct(G, H):
    return Group([(a, b) for a in range(G.n) for b in range(H.n)],
                 lambda x, y: (G.table[x[0]][y[0]], H.table[x[1]][y[1]]), f"{G.name}x{H.name}")
def semidirect(m, n, t):
    """Z_m x| Z_n, generator of Z_n acts on Z_m by multiplication by t (t^n = 1 mod m).  Elements (a, b)."""
    assert pow(t, n, m) == 1 % m
    return Group([(a, b) for a in range(m) for b in range(n)],
                 lambda x, y: ((x[0] + pow(t, x[1], m) * y[0]) % m, (x[1] + y[1]) % n), f"Z{m}x|{t}Z{n}")
def perm_group(gens, name):
    """closure of permutation tuples under composition (p*q)(i) = p[q[i]]"""
    deg = len(gens[0]); e = tuple(range(deg)); elems = {e}; frontier = [e]
    while frontier:
        nxt = []
        for p in frontier:
            for g in gens:
                q = tuple(p[g[i]] for i in range(deg))
                if q not in elems: elems.add(q); nxt.append(q)
        frontier = nxt
    return Group(sorted(elems), lambda p, q: tuple(p[q[i]] for i in range(deg)), name)
def sym(n): return perm_group([tuple([1, 0] + list(range(2, n))), tuple(list(range(1, n)) + [0])], f"S{n}")
def alt(n):
    if n == 3: return cyclic(3)
    return perm_group([tuple([1, 2, 0] + list(range(3, n))), tuple(list(range(1, n)) + [0]) if n % 2 else tuple([0] + list(range(2, n)) + [1])], f"A{n}")
def dihedral(n):  # order 2n, elements (rot, flip)
    return Group([(a, f) for a in range(n) for f in range(2)],
                 lambda x, y: ((x[0] + (y[0] if x[1] == 0 else -y[0])) % n, x[1] ^ y[1]), f"D{n}")
def dicyclic(n):  # order 4n: <a, x | a^{2n}=1, x^2=a^n, x a x^-1 = a^-1>, elements (i, j) = a^i x^j
    m = 2 * n
    def mul(x, y):
        i, j = x; k, l = y
        if j == 0: return ((i + k) % m, l)
        if l == 0: return ((i - k) % m, 1)
        return ((i - k + n) % m, 0)
    return Group([(i, j) for i in range(m) for j in range(2)], mul, f"Dic{n}")

# ---------- graphs ----------
def cayley(G, S):
    S = sorted(set(S)); assert all(G.inv[s] in S for s in S) and G.e not in S
    edges = set()
    for g in range(G.n):
        for s in S:
            h = G.table[g][s]; edges.add((min(g, h), max(g, h)))
    return G.n, sorted(edges)

def graph6(s):
    data = [ord(c) - 63 for c in s]
    n = data[0]; bits = []
    for d in data[1:]: bits += [(d >> k) & 1 for k in range(5, -1, -1)]
    edges = []; p = 0
    for j in range(1, n):
        for i in range(j):
            if bits[p]: edges.append((i, j))
            p += 1
    return n, edges

# ---------- SAT tests ----------
def col3_with_bad(n, edges, t, removed_vertex=None, removed_edges=()):
    """Return a 3-colouring of the graph (minus removed_vertex / removed_edges) with at most t monochromatic edges,
    or None if none exists."""
    var = lambda v, c: 3 * v + c + 1
    top = 3 * n
    s = Cadical153()
    for v in range(n):
        if v == removed_vertex: continue
        s.add_clause([var(v, c) for c in range(3)])
    rem = set(removed_edges); bad = []
    for (u, v) in edges:
        if removed_vertex in (u, v) or (u, v) in rem: continue
        if t == 0:
            for c in range(3): s.add_clause([-var(u, c), -var(v, c)])
        else:
            top += 1; b = top; bad.append(b)
            for c in range(3): s.add_clause([-var(u, c), -var(v, c), b])
    if t > 0:
        cnf = CardEnc.atmost(lits=bad, bound=t, top_id=top, encoding=EncType.seqcounter)
        for cl in cnf.clauses: s.add_clause(cl)
    if not s.solve(): s.delete(); return None
    m = set(l for l in s.get_model() if l > 0); s.delete()
    col = [next((c for c in range(3) if var(v, c) in m), -1) for v in range(n)]
    return col

def defect3(n, edges, cap=4):
    """d3(G) computed exactly up to cap (returns cap if >= cap)."""
    for t in range(cap):
        if col3_with_bad(n, edges, t) is not None: return t
    return cap

def vertex_critical(n, edges, vertices=None):
    """chi(G - v) <= 3 for the given vertices (default: all)."""
    for v in (range(n) if vertices is None else vertices):
        if col3_with_bad(n, edges, 0, removed_vertex=v) is None: return False
    return True

def verify_4r_explicit(n, edges, r):
    """Independent definition-level check that G is a (4,r)-graph: chi(G) = 4 (not 3-colourable, 4-colourable),
    every G - v 3-colourable, and G - F not 3-colourable for every edge set F with |F| <= r (plain SAT, no counter)."""
    if col3_with_bad(n, edges, 0) is not None: return False, "3-colourable"
    var = lambda v, c: 4 * v + c + 1; s = Cadical153()
    for v in range(n): s.add_clause([var(v, c) for c in range(4)])
    for (u, v) in edges:
        for c in range(4): s.add_clause([-var(u, c), -var(v, c)])
    ok = s.solve(); s.delete()
    if not ok: return False, "not 4-colourable"
    if not vertex_critical(n, edges): return False, "not vertex-critical"
    for k in range(1, r + 1):
        for F in itertools.combinations(edges, k):
            if col3_with_bad(n, edges, 0, removed_edges=F) is not None: return False, f"critical edge set {F}"
    return True, "ok"

def sw(a, b): p = list(range(4)); p[a], p[b] = b, a; return tuple(p)
def mulp(p, q): return tuple(p[q[i]] for i in range(4))

def known_graphs():
    """The two Lean-verified (4,1)-graphs of September 2026."""
    S4 = sym(4); G48 = direct(S4, cyclic(2))
    gens48 = [(sw(2, 3), 0), (sw(1, 2), 0), (mulp(sw(0, 1), sw(2, 3)), 0), (sw(0, 2), 0), (tuple(range(4)), 1), (mulp(sw(0, 2), sw(1, 3)), 1)]
    G60 = semidirect(5, 12, 2)   # elements (i in Z5, e in Z12); Chan writes (e, i)
    gens60 = [(0, 1), (0, 11), (1, 5), (2, 7), (0, 6), (3, 6)]
    return (("Kitamura48", G48, [G48.idx[(S4.idx[p], c)] for p, c in gens48]), ("Chan60", G60, [G60.idx[g] for g in gens60]))

if __name__ == "__main__":
    for name, G, S in known_graphs():
        n, E = cayley(G, S)
        print(name, "n =", n, "m =", len(E), "d3 =", defect3(n, E), "vertex-critical:", vertex_critical(n, E), flush=True)
        print("  explicit (4,1) check:", verify_4r_explicit(n, E, 1), flush=True)
    n, E = graph6("L?bFFbw~B{FwFw")
    degs = [0] * n
    for u, v in E: degs[u] += 1; degs[v] += 1
    crit = [e for e in E if col3_with_bad(n, E, 0, removed_edges=[e]) is not None]
    print("13-vertex graph: m =", len(E), "degrees", sorted(set(degs)), "d3 =", defect3(n, E), "vertex-critical:", vertex_critical(n, E), "critical edges:", len(crit))
