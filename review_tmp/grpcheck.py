import sys, itertools, math, collections
sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
import numpy as np
from search944 import group_by_name
from c944 import Group

def expected_order(spec):
    import re
    if "x|" in spec:
        i = spec.find("x|"); j = spec.find("xZ", i + 2)
        parts = [spec] if j < 0 else [spec[:j], spec[j+1:]]
    else:
        parts = spec.split("x")
    o = 1
    for p in parts:
        if p.startswith("Dic"): o *= 4*int(p[3:])
        elif p.startswith("D"): o *= 2*int(p[1:])
        elif p.startswith("S"): o *= math.factorial(int(p[1:]))
        elif p.startswith("A"): o *= math.factorial(int(p[1:]))//2 if int(p[1:])>3 else 3
        elif "x|" in p:
            a, b = p.split("x|"); m = int(a[1:]); t, n = b.split("Z"); o *= m*int(n)
        else: o *= int(p[1:])
    return o, parts

def invariants(G):
    T = np.array(G.table)
    n = G.n
    orders = [G.order(g) for g in range(n)]
    hist = dict(sorted(collections.Counter(orders).items()))
    center = sum(1 for g in range(n) if all(T[g, h] == T[h, g] for h in range(n)))
    abelian = center == n
    # derived subgroup size
    comms = set()
    for a in range(n):
        for b in range(n):
            comms.add(T[T[G.inv[a], G.inv[b]], T[a, b]])
    D = set(comms); frontier = list(D)
    while frontier:
        nxt = []
        for x in frontier:
            for y in list(comms):
                z = T[x, y]
                if z not in D: D.add(z); nxt.append(z)
        frontier = nxt
    return dict(n=n, hist=hist, center=center, derived=len(D))

def check(spec):
    G = group_by_name(spec)
    T = np.array(G.table); n = G.n
    errs = []
    eo, parts = expected_order(spec)
    if n != eo: errs.append(f"order {n} != expected {eo}")
    # latin square
    for i in range(n):
        if len(set(T[i])) != n or len(set(T[:, i])) != n: errs.append("not latin"); break
    # associativity: T[T[a,b],c] == T[a,T[b,c]]
    lhs = T[T[:, :, None], np.arange(n)[None, None, :]]  # T[T[a,b], c]
    rhs = T[np.arange(n)[:, None, None], T[None, :, :]]  # T[a, T[b,c]]
    if not np.array_equal(lhs, rhs): errs.append("NOT ASSOCIATIVE")
    e = G.e
    if not (all(T[e, j] == j and T[j, e] == j for j in range(n))): errs.append("identity not two-sided")
    if not all(T[i, G.inv[i]] == e and T[G.inv[i], i] == e for i in range(n)): errs.append("inverse not two-sided")
    return G, errs

specs = []
for f in ["all86.txt", "list5.txt"]:
    specs += [l.strip() for l in open(rf"C:\Users\danie\Math\erdos944\{f}") if l.strip()]
seen = set()
for spec in specs:
    if spec in seen: continue
    seen.add(spec)
    G, errs = check(spec)
    inv = invariants(G)
    print(f"{spec:14s} parts={expected_order(spec)[1]} n={inv['n']} center={inv['center']} derived={inv['derived']} orders={inv['hist']} {'OK' if not errs else 'ERR '+str(errs)}", flush=True)
