import sys, glob, os; sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
from search944 import group_by_name
specs=set()
for f in ["all86.txt","dec_9.txt","dec_10.txt","dec_9_12.txt","l5done.txt","l5rest.txt","tall.txt","timeouts.txt"]+glob.glob("list*.txt")+glob.glob("t*.txt"):
    if not os.path.exists(f): continue
    for line in open(f):
        line=line.strip()
        if line and not line.startswith("#"): specs.add(line.split()[0])
import re
for f in glob.glob("*.log"):
    for line in open(f, encoding="utf-8", errors="ignore"):
        m=re.match(r"^\s*(\S+) order (\d+):", line)
        if m: specs.add(m.group(1))
print(len(specs), "specs")
bad=[]
for sp in sorted(specs):
    try: G=group_by_name(sp)
    except Exception as ex: print("PARSE FAIL", sp, ex); continue
    n=G.n; T=G.table; e=G.e
    ok = all(T[e][i]==i and T[i][e]==i for i in range(n))
    ok = ok and all(T[i][G.inv[i]]==e and T[G.inv[i]][i]==e for i in range(n))
    ok = ok and all(sorted(T[i])==list(range(n)) for i in range(n))
    if ok and n<=100:
        ok = all(T[T[a][b]][c]==T[a][T[b][c]] for a in range(n) for b in range(n) for c in range(n))
    if not ok: bad.append(sp)
    print(sp, n, "group" if ok else "NOT A GROUP")
print("bad:", bad)
