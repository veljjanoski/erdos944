"""Automorphism group of a finite group given by a multiplication table (c944.Group).

Method: pick a generating set g_1..g_k greedily; an automorphism is determined by images h_i (same element orders, and
order(h_i h_j) = order(g_i g_j) as a filter).  A candidate tuple defines phi by phi(e) = e, phi(u g_i) = phi(u) h_i
(breadth-first over the Cayley graph of the generators); it is an automorphism iff this is consistent for every u and i
and bijective.  Consistency for all (u, i) gives phi(u w) = phi(u) phi(w) by induction on the word length of w, so it is a
homomorphism; bijective makes it an automorphism.  Every automorphism arises this way (it is determined by the h_i).
"""
import itertools

def closure(G, gens):
    seen = {G.e}; frontier = [G.e]
    while frontier:
        nxt = []
        for u in frontier:
            for g in gens:
                v = G.table[u][g]
                if v not in seen: seen.add(v); nxt.append(v)
        frontier = nxt
    return seen

def generating_set(G):
    order = [G.order(g) for g in range(G.n)]
    gens = []; H = {G.e}
    while len(H) < G.n:
        # element outside H that makes the generated subgroup largest (ties: larger order)
        best = max((g for g in range(G.n) if g not in H), key=lambda g: (len(closure(G, gens + [g])), order[g]))
        gens.append(best); H = closure(G, gens)
    return gens

def extend(G, gens, imgs):
    phi = [-1] * G.n; phi[G.e] = G.e; frontier = [G.e]
    while frontier:
        nxt = []
        for u in frontier:
            for g, h in zip(gens, imgs):
                v = G.table[u][g]; w = G.table[phi[u]][h]
                if phi[v] == -1: phi[v] = w; nxt.append(v)
                elif phi[v] != w: return None
        frontier = nxt
    # consistency for every (u, i) including already-mapped targets is checked above because every u is expanded once
    if -1 in phi or len(set(phi)) != G.n: return None
    return phi

def automorphisms(G, limit=None):
    gens = generating_set(G); order = [G.order(g) for g in range(G.n)]
    cand = [[h for h in range(G.n) if order[h] == order[g]] for g in gens]
    pair_ord = {(i, j): order[G.table[gens[i]][gens[j]]] for i in range(len(gens)) for j in range(len(gens)) if i != j}
    out = []
    def rec(i, imgs):
        if limit and len(out) >= limit: return
        if i == len(gens):
            phi = extend(G, gens, imgs)
            if phi is not None: out.append(phi)
            return
        for h in cand[i]:
            if any(order[G.table[imgs[j]][h]] != pair_ord[(j, i)] or order[G.table[h][imgs[j]]] != pair_ord[(i, j)] for j in range(i)): continue
            rec(i + 1, imgs + [h])
    rec(0, [])
    return out, gens

def atom_permutation(G, atoms, phi):
    idx = {a: k for k, a in enumerate(atoms)}
    return [idx[frozenset(phi[t] for t in a)] for a in atoms]

if __name__ == "__main__":
    # validation against known |Aut| and a full homomorphism check on small groups
    import sys
    from search944 import group_by_name
    from math import gcd
    phi_e = lambda n: sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)
    known = {'Z12': phi_e(12), 'Z30': phi_e(30), 'Z60': phi_e(60), 'D12': 12 * phi_e(12), 'D15': 15 * phi_e(15),
             'D30': 30 * phi_e(30), 'S4': 24, 'A5': 120, 'Z2xZ2xZ2': 168, 'Z2xZ4': 8, 'Dic2': 24, 'A4': 24,
             'S4xZ2': 48, 'Z3xZ3': 48, 'D4': 8, 'Z5x|2Z4': 20, 'Z7x|2Z3': 42, 'Z2xZ6xZ6': None}
    for spec, expect in known.items():
        G = group_by_name(spec); auts, gens = automorphisms(G)
        full_ok = all(all(p[G.table[a][b]] == G.table[p[a]][p[b]] for a in range(G.n) for b in range(G.n)) for p in auts) if G.n <= 60 else 'skipped'
        print(f"{spec:10s} order {G.n:3d} gens {len(gens)} |Aut| = {len(auts):5d} expected {expect}  hom-check {full_ok}  "
              f"{'OK' if expect is None or expect == len(auts) else 'MISMATCH'}", flush=True)
