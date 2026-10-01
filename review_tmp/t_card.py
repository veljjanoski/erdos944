# Test pysat CardEnc seqcounter with duplicate literals (weighted sums), atleast and atmost, exhaustively on small cases.
import itertools, random
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153
random.seed(1)
bad = 0; tests = 0
for trial in range(400):
    nv = random.randint(1, 5)
    L = random.randint(1, 9)
    lits = [random.randint(1, nv) for _ in range(L)]          # positive, with duplicates (as used in cegar944b)
    for kind in ("atleast", "atmost"):
        for k in range(0, L + 1):
            try:
                cnf = (CardEnc.atleast if kind == "atleast" else CardEnc.atmost)(lits=lits, bound=k, top_id=nv, encoding=EncType.seqcounter)
            except ValueError as ex:
                print("ValueError", kind, lits, k, ex); continue
            s = Cadical153(bootstrap_with=cnf.clauses)
            for assign in itertools.product([0, 1], repeat=nv):
                val = sum(assign[l - 1] for l in lits)
                want = (val >= k) if kind == "atleast" else (val <= k)
                got = s.solve(assumptions=[(v + 1) if assign[v] else -(v + 1) for v in range(nv)])
                tests += 1
                if got != want:
                    bad += 1
                    if bad < 10: print("MISMATCH", kind, lits, k, assign, want, got)
            s.delete()
print("tests", tests, "mismatches", bad)
# bound > len(lits) behaviour
for kind in ("atleast",):
    try:
        cnf = CardEnc.atleast(lits=[1, 1], bound=3, top_id=1); print("no error", cnf.clauses)
    except Exception as ex: print("bound>len raises:", type(ex).__name__, ex)
try:
    cnf = CardEnc.atleast(lits=[], bound=1, top_id=1); print("empty lits bound1:", cnf.clauses)
except Exception as ex: print("empty raises:", type(ex).__name__, ex)
