import sys; sys.path.insert(0, r'C:\Users\danie\Math\erdos944\review_tmp')
from compare import *
specs = ["Z4","Z5","Z6","Z7","Z8","Z9","Z10","Z11","Z12","Z13","Z14","Z15","Z16","D3","D4","D5","D6","D7","D8","Dic2","Dic3","Dic4","A4","Z2xZ2","Z2xZ4","Z2xZ6","Z3xZ3","Z2xZ2xZ2","Z3x|2Z4","Z5x|2Z4","Z7x|2Z3","Z4x|3Z4","Z8x|3Z2","Z2xZ8","Z4xZ4","D4xZ2","Dic2xZ2","S3xZ3","Z2xZ2xZ4"]
allp = []; nwit = 0; ncmp = 0
for sp in specs:
    Th, M, phi, inv_phi, R = setup(sp)
    for d in range(3, min(M.n - 1, 9) + 1):
        p = compare(sp, 0, d, d); allp += p; ncmp += 1
print("r=0 comparisons", ncmp, "TOTAL problems:", len(allp))
