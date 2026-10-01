import sys; sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
from search944 import group_by_name
def check(s1, s2, f):
    G, H = group_by_name(s1), group_by_name(s2)
    m = [H.idx[f(x)] for x in G.elems]
    assert len(set(m)) == G.n == H.n
    ok = all(m[G.table[i][j]] == H.table[m[i]][m[j]] for i in range(G.n) for j in range(G.n))
    print(s1, "->", s2, "explicit isomorphism:", ok)
# Z15x|4Z2 -> Z5x|4Z6 : (a,b) -> (a mod 5, d) with d = a mod 3, d = b mod 2 (CRT)
check("Z15x|4Z2", "Z5x|4Z6", lambda x: (x[0] % 5, next(d for d in range(6) if d % 3 == x[0] % 3 and d % 2 == x[1])))
# Z5x|2Z16 -> Z5x|3Z16 : (a,b) -> (a, 3b)
check("Z5x|2Z16", "Z5x|3Z16", lambda x: (x[0], 3 * x[1] % 16))
L5 = open(r"C:\Users\danie\Math\erdos944\list5.txt").read().split()
A86 = open(r"C:\Users\danie\Math\erdos944\all86.txt").read().split()
print("in both:", sorted(set(L5) & set(A86)))
print("dup within list5:", len(L5) - len(set(L5)))
print("D12 order", group_by_name("D12").n, "Dic6 order", group_by_name("Dic6").n)
