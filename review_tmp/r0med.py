import sys, random, time; sys.path.insert(0, r'C:\Users\danie\Math\erdos944\review_tmp')
import compare as C
random.seed(11); t0 = time.time(); allp = []
for sp in ["Z17","Z19","Z20","Z21","Z22","Z24","Z26","Z27","Z28","Z30","D9","D10","D11","D12","D13","D15","Dic5","Dic6","Dic7","A4xZ2","S4","Z3x|2Z8","Z5x|2Z4","Z7x|2Z3","S3xZ3","Z2xZ12","Z3xZ9","Z3xZ3xZ3","Dic3xZ2","A4xZ3"]:
    if time.time() - t0 > 400: print("time cap"); break
    for (dmin, dmax) in ((3, 5), (6, 7), (8, 8)):
        allp += C.compare(sp, 0, dmin, dmax, split_diag=(dmax <= 7))
# random restricted atoms on medium/large groups, r = 0 and r = 1
for sp in ["S4xZ2", "Z5x|2Z12", "A5", "Z15x|2Z4", "D24", "A4xZ4"]:
    Th, M, phi, inv_phi, R = C.setup(sp)
    for _ in range(4):
        if time.time() - t0 > 540: break
        sub = sorted(random.sample(range(len(R.atoms)), 9))
        allp += C.compare(sp, 0, 3, 7, atom_subset_mine=sub, label="[rnd9] ")
print("TOTAL problems:", len(allp), f"{time.time()-t0:.0f}s")
