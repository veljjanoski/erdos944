"""More groups for the #944 search, as c944.Group multiplication tables.

  PSL27 = PSL(2,7) (order 168), PGL27 = PGL(2,7) (336), SL25 = SL(2,5) (120), PSL28 = PSL(2,8) (504), plus everything
  search944.group_by_name knows (Zn, Dn, Dicn, Sn, An, Zm x|t Zn, direct products).  Direct products of any of these are
  written with 'x', e.g. PSL27xZ2, A5xZ3, S4xS3.  get(spec) builds the group; check() compares orders and element-order
  histograms with the known values.
"""
from collections import Counter
from c944 import Group, direct
from search944 import group_by_name

def closure_group(gens, mul, name):
    elems = set(gens); frontier = list(gens)
    while frontier:
        nxt = []
        for a in frontier:
            for g in gens:
                b = mul(a, g)
                if b not in elems: elems.add(b); nxt.append(b)
        frontier = nxt
    return Group(sorted(elems), mul, name)

def _mat_mul(p, canon):
    def mul(A, B):
        a, b, c, d = A; e, f, g, h = B
        return canon(((a * e + b * g) % p, (a * f + b * h) % p, (c * e + d * g) % p, (c * f + d * h) % p))
    return mul

def psl2(p):
    def canon(M):   # M ~ -M: choose the representative whose first nonzero entry is in 1..(p-1)/2
        x = next(v for v in M if v)
        return M if x <= (p - 1) // 2 else tuple((-v) % p for v in M)
    return closure_group([canon((1, 1, 0, 1)), canon((0, p - 1, 1, 0))], _mat_mul(p, canon), f"PSL(2,{p})")

def pgl2(p, nonsquare):
    def canon(M):   # M ~ tM: scale so that the first nonzero entry is 1
        x = next(v for v in M if v); xi = pow(x, p - 2, p)
        return tuple(v * xi % p for v in M)
    return closure_group([canon((1, 1, 0, 1)), canon((0, p - 1, 1, 0)), canon((nonsquare, 0, 0, 1))], _mat_mul(p, canon), f"PGL(2,{p})")

def sl2(p):
    return closure_group([(1, 1, 0, 1), (0, p - 1, 1, 0)], _mat_mul(p, lambda M: M), f"SL(2,{p})")

def psl28():
    """PSL(2,8) = SL(2,8) acting on the projective line over GF(8) = F2[x]/(x^3+x+1); points 0..7 = field elements, 8 = inf."""
    def gmul(a, b):
        r = 0
        for i in range(3):
            if (b >> i) & 1: r ^= a << i
        for i in (4, 3):
            if (r >> i) & 1: r ^= 0b1011 << (i - 3)
        return r
    ginv = {a: next(b for b in range(1, 8) if gmul(a, b) == 1) for a in range(1, 8)}
    INF = 8
    t = tuple(list(x ^ 1 for x in range(8)) + [INF])                       # x -> x + 1
    m = tuple(list(gmul(2, x) for x in range(8)) + [INF])                  # x -> w x, w = x (primitive)
    i = tuple([INF] + [ginv[x] for x in range(1, 8)] + [0])                # x -> 1/x
    mul = lambda P, Q: tuple(P[Q[k]] for k in range(9))
    return closure_group([t, m, i], mul, "PSL(2,8)")

SPECIAL = {"PSL27": lambda: psl2(7), "PGL27": lambda: pgl2(7, 3), "SL25": lambda: sl2(5), "PSL28": psl28}

def get(spec):
    if any(tok in spec for tok in SPECIAL):
        parts = spec.split("x")
        G = None
        for p in parts:
            H = SPECIAL[p]() if p in SPECIAL else group_by_name(p)
            G = H if G is None else direct(G, H)
        G.name = spec
        return G
    return group_by_name(spec)

KNOWN = {"PSL27": (168, {1: 1, 2: 21, 3: 56, 4: 42, 7: 48}),
         "PGL27": (336, {1: 1, 2: 49, 3: 56, 4: 42, 6: 56, 7: 48, 8: 84}),
         "SL25": (120, {1: 1, 2: 1, 3: 20, 4: 30, 5: 24, 6: 20, 10: 24}),
         "PSL28": (504, {1: 1, 2: 63, 3: 56, 7: 216, 9: 168}),
         "A6": (360, {1: 1, 2: 45, 3: 80, 4: 90, 5: 144}),
         "S5": (120, {1: 1, 2: 25, 3: 20, 4: 30, 5: 24, 6: 20}),
         "A5": (60, {1: 1, 2: 15, 3: 20, 5: 24})}

def check():
    ok = True
    for spec, (order, hist) in KNOWN.items():
        G = get(spec); h = dict(Counter(G.order(g) for g in range(G.n)))
        good = G.n == order and h == hist
        # associativity spot check on a sample of triples
        import random
        rnd = random.Random(1); T = G.table
        assoc = all(T[T[a][b]][c] == T[a][T[b][c]] for a, b, c in ((rnd.randrange(G.n), rnd.randrange(G.n), rnd.randrange(G.n)) for _ in range(20000)))
        ok &= good and assoc
        print(f"{spec:6s} order {G.n:4d} (expected {order})  element orders {'OK' if h == hist else h}  associative(sample) {assoc}", flush=True)
    return ok

if __name__ == "__main__":
    print("ALL OK" if check() else "MISMATCH", flush=True)
