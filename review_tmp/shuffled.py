import sys, random, time; sys.path.insert(0, r'C:\Users\danie\Math\erdos944\review_tmp')
import compare as C, search944, cegar944b, c944
random.seed(7); t0 = time.time()
orig = search944.group_by_name
def shuffled_group(spec):
    G = orig(spec); labels = list(range(G.n)); random.Random(hash(spec) % 1000).shuffle(labels)
    # element k of the new group is original element labels[k]; mul via original table
    return c944.Group(labels, lambda a, b: G.table[a][b], G.name + "~")
search944.group_by_name = shuffled_group; cegar944b.group_by_name = shuffled_group
allp = []
for sp in ["Z7", "Z10", "Z13", "Z16", "D5", "D8", "Dic3", "A4", "Z8x|3Z2", "Z2xZ2xZ4", "D4xZ2", "Z5x|2Z4", "S3xZ3"]:
    G = shuffled_group(sp); assert G.e != 0 or sp in (), None
    print(f"# {sp} identity index {G.e}", flush=True)
    for d in range(3, min(G.n - 1, 8) + 1): allp += C.compare(sp, 0, d, d, label="[shuf] ")
    allp += C.compare(sp, 1, 6, 8, label="[shuf] ")
    if G.n > 12: allp += C.compare(sp, 2, 9, 12, label="[shuf] ")
# positive r=1 on shuffled S4xZ2 / Z5x|2Z12 : restricted atoms around the known graphs
for nm, Gt, S in c944.known_graphs():
    sp = "S4xZ2" if "48" in nm else "Z5x|2Z12"
    Th, M, phi, inv_phi, R = C.setup(sp)          # Th is the shuffled table now
    # transport known S: original indices -> shuffled indices via element labels
    Sm = [inv_phi[Th.idx[s]] for s in S]; base = sorted({R.atom_of[s] for s in Sm})
    others = [a for a in range(len(R.atoms)) if a not in base]
    print(f"# {sp} identity index {Th.e}, known S is (4,1) in reference: {R.is_4r(set(base), 1)}", flush=True)
    for k in (3, 5):
        for _ in range(2): allp += C.compare(sp, 1, 6, 8, atom_subset_mine=sorted(base + random.sample(others, k)), label="[shuf+known] ")
print("TOTAL problems:", len(allp), f"{time.time()-t0:.0f}s")
