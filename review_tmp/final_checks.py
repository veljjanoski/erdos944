import sys, re, glob, time, itertools; sys.path.insert(0, r'C:\Users\danie\Math\erdos944\review_tmp')
import compare as C, search944, c944
from ref944 import *
from pysat.solvers import Glucose4
t0 = time.time()
# (1) all specs in the real list files / logs: valid group of the expected order
specs = set()
for f in glob.glob(r'C:\Users\danie\Math\erdos944\*.txt') + glob.glob(r'C:\Users\danie\Math\erdos944\*.log'):
    for line in open(f):
        m = re.match(r'\s*([A-Za-z0-9|]+?)(?: order (\d+))?[:\s]', line + ' ')
        tok = line.split()[0] if line.split() else ''
        if re.fullmatch(r'(Z\d+|D\d+|Dic\d+|S\d|A\d|Z\d+x\|\d+Z\d+)(x(Z\d+|S\d|A\d|D\d+|Dic\d+))*', tok): specs.add(tok)
        mo = re.match(r'(\S+) order (\d+)', line)
        if mo: specs.add(mo.group(1))
def expected_order(sp):
    def one(s):
        if s.startswith("Dic"): return 4 * int(s[3:])
        if s.startswith("D"): return 2 * int(s[1:])
        if s.startswith("S"): import math; return math.factorial(int(s[1:]))
        if s.startswith("A"): import math; return math.factorial(int(s[1:])) // 2
        if "x|" in s: a, b = s.split("x|"); return int(a[1:]) * int(b.split("Z")[1])
        return int(s[1:])
    if "x|" in sp:
        i = sp.find("x|"); j = sp.find("xZ", i + 2); parts = [sp] if j < 0 else [sp[:j], sp[j + 1:]]
    else: parts = sp.split("x")
    o = 1
    for p in parts: o *= one(p)
    return o
bad = 0
for sp in sorted(specs):
    try: G = search944.group_by_name(sp)
    except Exception as ex: print("PARSE FAIL", sp, ex); bad += 1; continue
    ok, msg = is_group_table(G.table) if G.n <= 72 else (True, "skipped")
    if not ok or G.n != expected_order(sp): print("GROUP PROBLEM", sp, G.n, expected_order(sp), msg); bad += 1
print(f"(1) {len(specs)} specs from logs checked, problems: {bad}  {time.time()-t0:.0f}s", flush=True)
# (2) split lemma on witnesses: for each witness and colour c, no proper colouring of G - e with colour c on <= r elements of S
def rare_colour_colouring(R, Sat, r, c):
    G = R.G; n = G.n; S = sorted(set().union(*[R.atoms[a] for a in Sat])); E = R.edges(set(Sat)); col = R.col
    s = Glucose4()
    for v in range(1, n):
        s.add_clause([col(v, k) for k in range(3)])
        for k1 in range(3):
            for k2 in range(k1 + 1, 3): s.add_clause([-col(v, k1), -col(v, k2)])
    for (g, h) in E:
        if 0 in (g, h): continue
        for k in range(3): s.add_clause([-col(g, k), -col(h, k)])
    for sub in itertools.combinations(S, r + 1): s.add_clause([-col(t, c) for t in sub])   # at most r of S get colour c
    ok = s.solve(); s.delete(); return ok
nw = 0; viol = 0
for sp, r, dmin, dmax in [("Z7",0,4,4),("Z13",0,4,6),("Z16",0,4,7),("D5",0,4,5),("D8",0,4,7),("Z19",0,4,8),("D11",0,5,8)]:
    Th, M, phi, inv_phi, R = C.setup(sp)
    for combo in enumerate_S(R, dmin, dmax):
        if R.is_4r(set(combo), r):
            nw += 1
            for c in range(3):
                if rare_colour_colouring(R, combo, r, c): viol += 1; print("LEMMA VIOLATION", sp, r, combo, c)
for nm, Gt, S in c944.known_graphs():
    sp = "S4xZ2" if "48" in nm else "Z5x|2Z12"
    Th, M, phi, inv_phi, R = C.setup(sp); Sat = {R.atom_of[inv_phi[s]] for s in S}; nw += 1
    for c in range(3):
        if rare_colour_colouring(R, Sat, 1, c): viol += 1; print("LEMMA VIOLATION", sp, 1, c)
print(f"(2) split lemma: {nw} witnesses tested, violations {viol}  {time.time()-t0:.0f}s")
