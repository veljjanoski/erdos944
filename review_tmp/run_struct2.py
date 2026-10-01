import sys
sys.path.insert(0, r"C:\Users\danie\Math\erdos944\review_tmp")
from structcheck import check
specs = sys.argv[1].split(",")
for spec in specs:
    for (r, dmin, dmax) in [(0, 1, 30), (1, 4, 9), (2, 6, 12), (2, 9, 12)]:
        for split in (True, False):
            check(spec, r, dmin, dmax, split, nsamp=150)
