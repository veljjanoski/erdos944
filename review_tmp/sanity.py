import sys, itertools, random, time
sys.path.insert(0, '..'); sys.path.insert(0, '.')
from ref944 import *
import search944, c944
t0 = time.time()
# 1. group isomorphism my construction vs theirs
specs = ["Z4","Z12","Z16","Z24","D3","D6","D12","Dic2","Dic3","Dic6","S3","S4","A4","A5","A4xZ2","S4xZ2","Z5x|2Z12","Z3x|2Z4","Z3x|2Z8","Z5x|2Z4","Z7x|2Z3","Z2xZ2xZ4","Z2xZ12","D4xZ2","Dic2xZ2","Dic3xZ2","S3xZ3","Z15x|2Z4","Z5x|4Z4","Z4x|3Z4","Z8x|3Z2","Z8x|5Z2","Z8x|7Z2"]
isos = {}
for sp in specs:
    try:
        Th = search944.group_by_name(sp)
    except Exception as ex:
        print(sp, "their parse error", ex); continue
    ok, msg = is_group_table(Th.table)
    M = parse(sp)
    phi = find_iso(M, Th.table, Th.e)
    isos[sp] = phi
    print(f"{sp:12s} theirs n={Th.n} group={ok}({msg}) mine n={M.n} iso={'yes' if phi else 'NO'}", flush=True)
# 2. colourable vs exhaustive on random small graphs: use Z_n Cayley graphs and D_n
def brute_min_mono(n, E, remove=None):
    best = 10**9
    verts = [v for v in range(n) if v != remove]
    for colr in itertools.product(range(3), repeat=len(verts) - 1):
        c = dict(zip(verts, (0,) + colr))
        m = sum(1 for (u, v) in E if u != remove and v != remove and c[u] == c[v])
        best = min(best, m)
    return best
bad = 0; cnt = 0
for sp in ["Z7", "Z8", "Z9", "D4", "D5", "Z10", "Dic2"]:
    M = parse(sp); R = Ref(M)
    for combo in enumerate_S(R, 1, M.n - 1):
        Sat = set(combo); E = R.edges(Sat)
        d3 = brute_min_mono(M.n, E); dve = brute_min_mono(M.n, E, remove=0)
        cnt += 1
        if R.colourable(Sat) != (d3 == 0) or R.colourable(Sat, remove_e=True) != (dve == 0): bad += 1; print("MISMATCH col", sp, combo)
        for r in (0, 1, 2):
            want = (dve == 0) and d3 >= r + 1
            if R.is_4r(Sat, r) != want: bad += 1; print("MISMATCH is_4r", sp, combo, r, d3, dve)
print("exhaustive cross-check sets", cnt, "mismatches", bad, f"{time.time()-t0:.0f}s", flush=True)
# 3. known graphs
M = parse("Z4"); R = Ref(M); print("K4 (4,0):", R.is_4r({R.atom_of[1], R.atom_of[2]}, 0), R.full_verify({R.atom_of[1], R.atom_of[2]}, 0))
for name, Gt, S in c944.known_graphs():
    sp = "S4xZ2" if "48" in name else "Z5x|2Z12"
    M = parse(sp); phi = isos[sp]; inv_phi = {b: a for a, b in enumerate(phi)}
    Sm = [inv_phi[s] for s in S]; R = Ref(M); Sat = {R.atom_of[s] for s in Sm}
    print(name, "deg", len(set().union(*[R.atoms[a] for a in Sat])), "is(4,1):", R.is_4r(Sat, 1), "is(4,2):", R.is_4r(Sat, 2), "full(4,1):", R.full_verify(Sat, 1), f"{time.time()-t0:.0f}s", flush=True)
