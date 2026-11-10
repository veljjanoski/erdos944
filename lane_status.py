"""Combine the progress files of cube-mode lanes (whole-lane and shard files) and report, per lane, how many of
the lane's cubes are finished (NO) and whether the lane is COMPLETE.

A lane's files are progress/<group>_r<r>_d<a>-<b>_s<k>_fp<sigma>_A<A>.txt and ..._A<A>_shard<i>of<m>.txt.
The cube list of a lane with A sigma-atoms is (i,) for i < A and (i, j) for i < j < A, so it has A + A(A-1)/2
cubes; a cube is done when some file has the line "<key> NO <it> <sec>" with a valid key.  Lines that do not
parse are ignored (never counted as done).  Usage: python lane_status.py [substring filter]
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def lane_cover(filt=""):
    """base -> dict(A, total, done (set of keys), files, dups) over progress/*.txt (whole-lane and shard files)."""
    lanes = {}
    for pf in sorted(glob.glob(os.path.join(HERE, "progress", "*.txt"))):
        name = os.path.basename(pf)[:-4]
        m = re.match(r"(.*_A(\d+))(?:_shard(\d+)of(\d+))?$", name)
        if not m:
            continue
        base, A = m.group(1), int(m.group(2))
        if filt and filt not in base:
            continue
        lane = lanes.setdefault(base, {"A": A, "total": A + A * (A - 1) // 2, "done": set(), "files": 0, "dups": 0})
        lane["files"] += 1
        for line in open(pf):
            f4 = line.split()
            if len(f4) != 4 or f4[1] != "NO" or not (f4[2].isdigit() and f4[3].isdigit()):
                continue
            parts = f4[0].split(",")
            if not all(p.isdigit() for p in parts):
                continue
            idx = [int(p) for p in parts]
            if not (len(idx) == 1 and idx[0] < A or len(idx) == 2 and idx[0] < idx[1] < A):
                continue
            if f4[0] != ",".join(map(str, idx)):      # only the canonical spelling counts (no leading zeros)
                continue
            if f4[0] in lane["done"]:
                lane["dups"] += 1
            lane["done"].add(f4[0])
    return lanes


def main():
    lanes = lane_cover(sys.argv[1] if len(sys.argv) > 1 else "")
    for base, lane in lanes.items():
        total, done = lane["total"], len(lane["done"])
        state = "COMPLETE: lane NO" if done == total else f"open ({total - done} cubes left)"
        print(f"{os.path.basename(base)}: {done}/{total} cubes done in {lane['files']} file(s), "
              f"{lane['dups']} duplicates -> {state}")


if __name__ == "__main__":
    main()
