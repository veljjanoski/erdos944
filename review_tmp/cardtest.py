import itertools, random
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153
random.seed(1)
bad = 0; tests = 0
for trial in range(3000):
    nv = random.randint(1, 5)
    L = random.randint(0, 9)
    lits = [random.choice([1, -1]) * random.randint(1, nv) if random.random() < 0.2 else random.randint(1, nv) for _ in range(L)]
    bound = random.randint(-1, L + 2)
    top = nv + random.randint(0, 3)
    for kind in ("atleast", "atmost"):
        try:
            cnf = getattr(CardEnc, kind)(lits=lits, bound=bound, top_id=top, encoding=EncType.seqcounter)
        except Exception as ex:
            print("EXC", kind, lits, bound, ex); bad += 1; continue
        aux_ok = all(abs(l) <= nv or abs(l) > top for cl in cnf.clauses for l in cl)
        nv_ok = all(abs(l) <= max(cnf.nv, top) for cl in cnf.clauses for l in cl)
        if not aux_ok or not nv_ok:
            print("VAR COLLISION/NV", kind, lits, bound, top, cnf.nv, cnf.clauses); bad += 1
        for assign in itertools.product([False, True], repeat=nv):
            val = lambda l: assign[abs(l) - 1] if l > 0 else not assign[abs(l) - 1]
            cnt = sum(1 for l in lits if val(l))
            want = cnt >= bound if kind == "atleast" else cnt <= bound
            s = Cadical153(bootstrap_with=cnf.clauses)
            got = s.solve(assumptions=[v + 1 if assign[v] else -(v + 1) for v in range(nv)]); s.delete()
            tests += 1
            if got != want:
                bad += 1
                if bad < 15: print("MISMATCH", kind, "lits", lits, "bound", bound, "assign", assign, "want", want, "got", got, "clauses", cnf.clauses)
print("tests", tests, "bad", bad)
