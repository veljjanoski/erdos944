src = open(r"C:\Users\danie\Math\erdos944\cegar944b.py", encoding="utf-8").read()
BS = chr(92)
old_w = '            if log: open(log, "a").write(line + "' + BS + 'n")\n            return S\n'
print(src.count(old_w))
new_w = ('            if log: open(log, "a").write(line + "' + BS + 'n")\n'
         '            WIT.append((tuple(S), ok))\n'
         '            chosen = set(a for a in range(A) if x(a) in m)\n'
         '            s.add_clause([-x(a) if a in chosen else x(a) for a in range(A)])\n'
         '            continue\n')
src = src.replace(old_w, new_w)
old_n = '            if log: open(log, "a").write(msg + "' + BS + 'n")\n            return None\n'
print(src.count(old_n))
src = src.replace(old_n, '            if log: open(log, "a").write(msg + "' + BS + 'n")\n            return WIT\n')
a = "    G = group_by_name(spec); atoms = sym_closure_candidates(G); n = G.n; e = G.e\n"
print(src.count(a))
src = src.replace(a, a + "    WIT = []\n", 1)
src = src.replace("print(msg, flush=True)", "pass").replace("print(line, flush=True)", "pass")
src = src.replace('log="cegar2.log"', 'log=None')
open("cegar_all.py", "w", encoding="utf-8").write(src)
