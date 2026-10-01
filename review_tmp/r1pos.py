import sys, random, time; sys.path.insert(0, r'C:\Users\danie\Math\erdos944\review_tmp')
from compare import *
import c944
random.seed(944); t0 = time.time()
allp = []; kinds = {}
known = {("S4xZ2" if "48" in nm else "Z5x|2Z12"): S for nm, Gt, S in c944.known_graphs()}
for sp, S in known.items():
    Th, M, phi, inv_phi, R = setup(sp)
    base = sorted({R.atom_of[inv_phi[s]] for s in S})
    others = [a for a in range(len(R.atoms)) if a not in base]
    tests = []
    for k in (2, 3, 4, 5):
        for _ in range(3): tests.append(("known+%d" % k, base + random.sample(others, k)))
    for _ in range(4):   # drop one known atom, add 4-6 random ones
        b = list(base); b.remove(random.choice(b)); tests.append(("known-1+", b + random.sample(others, random.randint(4, 6))))
    for _ in range(3): tests.append(("random10", random.sample(range(len(R.atoms)), 10)))
    for lab, sub in tests:
        for (r, dmin, dmax) in ((1, 6, 8), (1, 6, 10), (2, 9, 12), (0, 4, 6)):
            if time.time() - t0 > 480: break
            p = compare(sp, r, dmin, dmax, atom_subset_mine=sorted(sub), label=f"[{lab:9s}] ")
            allp += p
print("TOTAL problems:", len(allp), f"{time.time()-t0:.0f}s")
