import itertools, random, pysat
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153
print("pysat", pysat.__version__)
random.seed(1)
bad=0; tests=0
for trial in range(400):
    nv = random.randint(1,5)
    L = [random.randint(1,nv) for _ in range(random.randint(0,10))]
    if random.random()<0.3: L=[l if random.random()<0.7 else -l for l in L]
    k = random.randint(0, len(L)+2)
    top = nv + random.randint(0,3)
    for kind in ("atleast","atmost"):
        if kind=="atleast" and k>len(L): continue
        cnf = (CardEnc.atleast if kind=="atleast" else CardEnc.atmost)(lits=L, bound=k, top_id=top, encoding=EncType.seqcounter)
        # aux vars must be > top
        auxmax = max([abs(l) for cl in cnf.clauses for l in cl] + [0])
        aux = set(abs(l) for cl in cnf.clauses for l in cl) - set(range(1, nv+1))
        if aux and min(aux) <= top: print("AUX CLASH", L,k,top,sorted(aux)); bad+=1
        if auxmax > max(cnf.nv, top): print("NV too small", L, k, top, cnf.nv, auxmax); bad+=1
        for assign in itertools.product([0,1], repeat=nv):
            val = lambda l: assign[abs(l)-1] if l>0 else 1-assign[abs(l)-1]
            ssum = sum(val(l) for l in L)
            want = ssum>=k if kind=="atleast" else ssum<=k
            s=Cadical153(bootstrap_with=cnf.clauses)
            got = s.solve(assumptions=[(i+1) if assign[i] else -(i+1) for i in range(nv)]); s.delete()
            tests+=1
            if got!=want: bad+=1; print("MISMATCH",kind,L,k,assign,ssum,got,want) if bad<10 else None
print("tests",tests,"bad",bad)
