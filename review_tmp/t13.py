import sys; sys.path.insert(0, r"C:\Users\danie\Math\erdos944")
from c944 import *
import networkx as nx
n, E = graph6("L?bFFbw~B{FwFw")
degs=[0]*n
for u,v in E: degs[u]+=1; degs[v]+=1
print(n, len(E), sorted(set(degs)), "d3", defect3(n,E), "vc", vertex_critical(n,E))
crit=[e for e in E if col3_with_bad(n,E,0,removed_edges=[e]) is not None]
print("critical edges", len(crit))
G=nx.Graph(E)
# is it circulant? check vertex transitivity quickly via automorphisms
from networkx.algorithms.isomorphism import GraphMatcher
GM=GraphMatcher(G,G); cnt=0
orb=set()
for m in GM.isomorphisms_iter():
    cnt+=1; orb.add(m[0])
    if cnt>100000: break
print("auts>=",cnt,"orbit of 0:",sorted(orb))
