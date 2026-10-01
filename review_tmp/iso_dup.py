import sys, itertools
sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
from search944 import group_by_name

def gens_iso(G, H, gensG):
    """try to find an isomorphism G->H by mapping generators gensG to all tuples of same-order elems of H"""
    # BFS words for G elements from generators
    word = {G.e: []}; frontier=[G.e]
    while frontier:
        nxt=[]
        for x in frontier:
            for k,g in enumerate(gensG):
                y=G.table[x][g]
                if y not in word: word[y]=word[x]+[k]; nxt.append(y)
        frontier=nxt
    assert len(word)==G.n
    cands=[[h for h in range(H.n) if H.order(h)==G.order(g)] for g in gensG]
    for img in itertools.product(*cands):
        f={}
        for x,w in word.items():
            y=H.e
            for k in w: y=H.table[y][img[k]]
            f[x]=y
        if len(set(f.values()))!=G.n: continue
        if all(f[G.table[a][b]]==H.table[f[a]][f[b]] for a in range(G.n) for b in range(G.n)):
            return img
    return None

def gens_of(G):
    # greedy small generating set
    gens=[]; sub={G.e}
    def closure(gs):
        s={G.e}; fr=[G.e]
        while fr:
            nx=[]
            for x in fr:
                for g in gs:
                    y=G.table[x][g]
                    if y not in s: s.add(y); nx.append(y)
            fr=nx
        return s
    for g in sorted(range(G.n), key=lambda g:-G.order(g)):
        if g not in sub:
            gens.append(g); sub=closure(gens)
            if len(sub)==G.n: break
    return gens

for a,b in [("Z15x|4Z2","Z5x|4Z6"),("Z5x|2Z16","Z5x|3Z16")]:
    G=group_by_name(a); H=group_by_name(b)
    gs=gens_of(G)
    img=gens_iso(G,H,gs)
    print(a,b,G.n,H.n,"gens",[G.elems[g] for g in gs],"iso image",None if img is None else [H.elems[h] for h in img])
for s in ["D12","Dic6"]:
    print(s, group_by_name(s).n)
l5=[l.strip() for l in open(r"C:\Users\danie\Math\erdos944\list5.txt") if l.strip()]
a86=[l.strip() for l in open(r"C:\Users\danie\Math\erdos944\all86.txt") if l.strip()]
print("in both:", [g for g in l5 if g in a86])
