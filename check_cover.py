"""Independent check of the progress files of cube-mode lanes (whole-lane file plus shard files): the recorded cubes
must cover the lane.

Top level: every single (i,) and every pair (i, j), i < j < A, must have a line "<key> NO <it> <sec>" in some file.
Splits: whenever a prefix cube c occurs as a split parent (a line "c,k" or "c=" exists), the lines "c", "c=" and "c,k"
for every k from c[-1]+1 to A-1 must all exist; a child that is itself a parent is checked the same way, so the cover
is verified down to the leaves.  Duplicate lines are counted and reported (they do not affect the cover).  A is read from the file name (..._A<A>[_shard<i>of<m>].txt).
Usage: python check_cover.py [substring filter]      exit code 1 if any lane is not completely covered.
"""
import collections
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def lane_files():
    """base -> (A, [files]) over progress/*.txt."""
    lanes = {}
    for pf in sorted(glob.glob(os.path.join(HERE, "progress", "*.txt"))):
        m = re.match(r"(.*_A(\d+))(?:_shard(\d+)of(\d+))?$", os.path.basename(pf)[:-4])
        if m:
            lanes.setdefault(m.group(1), (int(m.group(2)), []))[1].append(pf)
    return lanes


def check(A, files):
    keys = collections.Counter()
    for pf in files:
        for line in open(pf):
            p = line.split()
            if len(p) == 4 and p[1] == "NO" and p[2].isdigit() and p[3].isdigit():
                keys[p[0]] += 1
    top = {str(i) for i in range(A)} | {f"{i},{j}" for j in range(A) for i in range(j)}
    missing = sorted(top - set(keys))
    parents = {k.rsplit(",", 1)[0] for k in keys if k.count(",") >= 2 and not k.endswith("=")}
    parents |= {k[:-1] for k in keys if k.endswith("=")}
    incomplete = []
    for par in sorted(parents):
        idx = [int(v) for v in par.split(",")]
        need = [par, par + "="] + [f"{par},{k}" for k in range(idx[-1] + 1, A)]
        if any(n not in keys for n in need):
            incomplete.append(par)
    dups = sum(c - 1 for c in keys.values() if c > 1)
    return len(keys), missing, len(parents), incomplete, dups


def main():
    filt = sys.argv[1] if len(sys.argv) > 1 else ""
    ok = True
    for base, (A, files) in lane_files().items():
        if filt and filt not in base:
            continue
        nkeys, missing, nparents, incomplete, dups = check(A, files)
        good = not missing and not incomplete          # duplicate lines are harmless for the cover: reported only
        ok = ok and good
        print(f"{os.path.basename(base)}: {len(files)} file(s), {nkeys} keys, {nparents} split parents, "
              f"{len(missing)} top-level cubes missing, {len(incomplete)} splits incomplete, {dups} duplicates -> "
              f"{'COVER COMPLETE' if good else 'NOT COMPLETE'}"
              + (f" (missing e.g. {missing[:3]})" if missing else "") + (f" (incomplete e.g. {incomplete[:3]})" if incomplete else ""))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
