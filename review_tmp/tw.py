import sys, random; sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
from c944 import cayley
from search944 import group_by_name, sym_closure_candidates
random.seed(3); bad=0; tests=0
for spec in ["S4xZ2","Z5x|2Z12","A5","Dic6","D12","A4xZ3","Z2xZ2xZ12","Z13x|3Z3"]:
    G=group_by_name(spec); atoms=sym_closure_candidates(G); n=G.n
    for _ in range(200):
        col=[random.randrange(3) for _ in range(n)]
        w=[]
        for a, atom in enumerate(atoms):   # verbatim from cegar944b
            cnt = 0
            for g in range(n):
                for t in atom:
                    h = G.table[g][t]
                    if h < g: continue
                    if col[g] == col[h]: cnt += 1
            w.append(cnt)
        ch=[a for a in range(len(atoms)) if random.random()<0.3]
        if not ch: continue
        S=sorted(set().union(*[atoms[a] for a in ch])); _,E=cayley(G,S)
        mono=sum(1 for u,v in E if col[u]==col[v]); tests+=1
        if mono!=sum(w[a] for a in ch): bad+=1
        # edge count per atom
        if len(E)!=n*len(S)//2: bad+=1
print("tests",tests,"bad",bad)
