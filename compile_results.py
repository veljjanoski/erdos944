"""Compile every r = 2 verdict in this folder into RESULTS.md (deterministic; reads logs only).

Full search (all symmetric connection sets S of the given size; programs cegar944.py = a, cegar944b.py = b, cegar944c.py = c,
cegar944s.py with sigma = id = s-id): lines "G order n: NO (4,2)-Cayley graph with degree in [a,b] ..." in *.log and in
runs/*/logs/*.out; TIMEOUT lines "G deg d: TIMEOUT ..." in frontier*.log.  A degree is listed as decided if any program
decided it.  Also the 2026-09-26 cross-checks in review_tmp/*.log (CEGAR and brute force both NO; program 'brute').
Sigma lane (cegar944s.py, S fixed by an automorphism of prime order, one per Aut-class): results*.jsonl of
runs/sweep9 (DONE = NO) and COMPLETE lines in progress/*.txt (cube mode).
"""
import re, glob, json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
NO = re.compile(r"^(\S+) order (\d+): NO \(4,2\)-Cayley graph with degree in \[(\d+),(\d+)\]\s+\(\d+ iterations, \d+s\)\s*(\[[^\]]*\])?")
TO = re.compile(r"^(\S+) deg (\d+): TIMEOUT")
full = collections.defaultdict(set); prog_of = collections.defaultdict(set); order = {}; tout = collections.defaultdict(set)
files = sorted(glob.glob("*.log")) + sorted(glob.glob("runs/*/logs/*.out"))
for fn in files:
    for line in open(fn, encoding="utf-8", errors="replace"):
        m = NO.match(line.strip())
        if m:
            g, n, a, b, tag = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), (m.group(5) or "[]")
            if "sigma=" in tag and "sigma=id" not in tag: continue          # sigma lanes are handled below
            p = "s-id" if "sigma=id" in tag else ("c" if tag.startswith("[c") else "b" if tag.startswith("[b") else "a")
            order[g] = n
            for d in range(a, b + 1): full[g].add(d); prog_of[(g, d)].add(p)
            continue
        m = TO.match(line.strip())
        if m: tout[m.group(1)].add(int(m.group(2)))
# cross-checks of 2026-09-26 (review_tmp/): CEGAR verdict AND an independent brute-force reference over all S, both NO
XC = re.compile(r"^(\S+)\s+r=2 deg\[(\d+),(\d+)\] cegar=NO .*\| ref: \d+ S, \d+ G-e 3col, 0 witnesses.*\bOK\s*$")
for fn in sorted(glob.glob("review_tmp/*.log")):
    for line in open(fn, encoding="utf-8", errors="replace"):
        m = XC.match(line.strip())
        if m:
            g, a, b = m.group(1), int(m.group(2)), int(m.group(3))
            for d in range(a, b + 1): full[g].add(d); prog_of[(g, d)].add("brute")
for g in tout: tout[g] -= full.get(g, set())
full = {g: v for g, v in full.items() if v}                 # groups with at least one decided degree
import groups944
for g in set(full) | set(tout):
    if g not in order: order[g] = groups944.get(g).n

lanes = {}       # (group, degree, class) -> NO / TIMEOUT / open
for fn in sorted(glob.glob("runs/sweep9/results*.jsonl")):
    for line in open(fn):
        r = json.loads(line)
        m = re.match(r"(?:t4h_|cube_)?s(9|10)_(.+)_c(\d+)$", r["id"])
        if not m: continue
        key = (m.group(2).replace("_", "|"), int(m.group(1)), int(m.group(3)))
        if r["status"] == "DONE" and "NO (4,2)" in r["last"]: lanes[key] = "NO"
        elif lanes.get(key) != "NO": lanes[key] = r["status"]
for fn in glob.glob("progress/*.txt"):
    m = re.match(r"progress[\\/](.+)_r2_d(\d+)-\d+_s(\d+)_fp", fn)
    key = (m.group(1).replace("_", "|"), int(m.group(2)), int(m.group(3)))
    if any(l.startswith("COMPLETE") and "NO (4,2)" in l for l in open(fn)): lanes[key] = "NO"
    elif lanes.get(key) != "NO": lanes[key] = "open (cube run stopped)"
cls = {}
for fn in glob.glob("runs/list/logs/*.out"):
    L = open(fn).read().splitlines(); g, n, aut = L[0].split()[0], int(L[0].split()[2]), int(L[0].split()[3].split("=")[1])
    cls[g] = (n, aut, len([l for l in L if "class" in l]))

def esc(g): return g.replace("|", "\\|")          # '|' inside a Markdown table cell must be escaped
out = ["# Results (compiled by compile_results.py from the logs)", "",
       "Group names: Zn cyclic, Dn dihedral of order 2n, Dicn dicyclic of order 4n, Sn/An symmetric/alternating,",
       "Zm x|t Zn the semidirect product where the generator of Zn acts on Zm by multiplication by t, PSL27 = PSL(2,7),",
       "PGL27 = PGL(2,7), SL25 = SL(2,5), PSL28 = PSL(2,8), 'x' = direct product.", "",
       "## Full search: all symmetric connection sets of the given size (r = 2)", "",
       "Degrees in the 'NO' column are decided (no (4,2)-Cayley graph of that degree on that group). For a group of odd",
       "order there is no symmetric S of odd size, so odd degrees are trivially NO there. A few groups occur under two",
       "isomorphic names (Z5x|4Z6 = Z15x|4Z2, Z5x|3Z16 = Z5x|2Z16, Z2xZ2xZ2xZ3 = Z2xZ2xZ6, Z3x|2Z4xZ2 = Dic3xZ2).",
       "Programs: a = cegar944.py, b = cegar944b.py, c = cegar944c.py, s-id = cegar944s.py with sigma = id, brute = cegar944b",
       "verdict confirmed by an independent brute force over all connection sets (review_tmp/).", "",
       "| group | order | NO at degrees | timeout at degrees | programs |", "|---|---|---|---|---|"]
for g in sorted(set(full) | set(tout), key=lambda g: (order.get(g, 0), g)):
    ds = sorted(full.get(g, set())); progs = sorted({p for d in ds for p in prog_of[(g, d)]})
    out.append(f"| {esc(g)} | {order.get(g, '?')} | {','.join(map(str, ds)) or '-'} | {','.join(map(str, sorted(tout[g]))) or '-'} | {','.join(progs)} |")
nfull = sum(len(v) for v in full.values())
all4 = [g for g in full if {9, 10, 11, 12} <= full[g]]
orders = sorted(order[g] for g in full)
ISO = {"Z15x|4Z2": "Z5x|4Z6", "Z5x|2Z16": "Z5x|3Z16", "Z2xZ2xZ6": "Z2xZ2xZ2xZ3", "Dic3xZ2": "Z3x|2Z4xZ2",
       "Z5x|2Z12xZ2": "Z5x|2Z4xZ6"}                    # isomorphic names (second name kept)
uniq = {}
for g, v in full.items(): uniq.setdefault(ISO.get(g, g), set()).update(v)
cnt = {d: sum(1 for v in uniq.values() if d in v) for d in (9, 10, 11, 12)}
out += ["", f"Up to isomorphism: {len(uniq)} groups; decided at degree 9 for {cnt[9]}, at 10 for {cnt[10]}, at 11 and 12 for {cnt[11]}."]
out += ["", f"{len(full)} group names (orders {orders[0]}..{orders[-1]}), {nfull} decided (name, degree) cases; degrees 9-12 all decided "
        f"for {len(all4)} groups (orders up to {max(order[g] for g in all4)}); {sum(len(v) for v in tout.values())} cases timed out "
        f"({', '.join(f'{esc(g)} d{d}' for g in sorted(tout) for d in sorted(tout[g]))}).", "",
        "## Sigma lane: connection sets fixed by an automorphism of prime order (r = 2, degrees 9 and 10)", "",
        "One row per group; 'classes' = conjugacy classes of automorphisms of prime order, one lane each. Z5x|2Z12xZ2 and",
        "Z5x|2Z4xZ6 are the same group (F20 x Z6, since Z5x|2Z12 = F20 x Z3); it was run under both names.", "",
        "| group | order | Aut | classes | degree 9 | degree 10 |", "|---|---|---|---|---|---|"]
for g in sorted(cls, key=lambda g: (cls[g][0], g)):
    n, aut, k = cls[g]; row = []
    for d in (9, 10):
        st = [lanes.get((g, d, c), "missing") for c in range(k)]
        bad = [f"c{c}: {s}" for c, s in enumerate(st) if s != "NO"]
        row.append("all NO" if not bad else "; ".join(bad))
    out.append(f"| {esc(g)} | {n} | {aut} | {k} | {row[0]} | {row[1]} |")
nl = sum(1 for v in lanes.values() if v == "NO")
dl = {k: v for k, v in lanes.items() if ISO.get(k[0], k[0]) == k[0]}            # drop the runs under a second name
out += ["", f"{nl} of {len(lanes)} lane runs NO ({sum(1 for v in dl.values() if v == 'NO')} of {len(dl)} distinct (group, class, degree) cases); open: " + ", ".join(f"{g} d{d} c{c}" for (g, d, c), v in sorted(lanes.items()) if v != "NO")]
open("RESULTS.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[-3:])); print(f"full search: {len(full)} groups, {nfull} cases")
