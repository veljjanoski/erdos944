# Erdős problem #944, k = 4, r = 2 — searching for a (4,2)-graph (negative results)

**Problem** (https://www.erdosproblems.com/944). A graph G is k-vertex-critical if χ(G) = k and χ(G − v) < k for every
vertex v. Erdős asked whether for k ≥ 4 and r ≥ 1 there is a k-vertex-critical graph in which no set of at most r edges
is critical (deleting any ≤ r edges keeps χ = k). For r = 1 this is Dirac's conjecture (Brown for k = 5; Lattanzio and
Jensen for k ≥ 5). Martinsson and Steiner proved the statement for every r when k is large, and Skottova and Steiner for
all k ≥ 5 and r ≥ 1. For k = 4, the case r = 1 (the last open case of Dirac's conjecture) was settled in September 2026
by explicit 6-regular Cayley graphs: Kenta Kitamura (on S4 × Z2, 48 vertices) and Alex Chan (on Z5 ⋊₂ Z12, 60
vertices), both with Lean formalisations. The case k = 4, r = 2 is open; one explicit (4,2)-graph would settle it.

For k = 4: G is a (4,r)-graph iff every G − v is 3-colourable and every map V → {1,2,3} has at least r + 1
monochromatic edges. A (4,r)-graph has minimum degree at least 3r + 3, so at least 9 for r = 2 (Skottova–Steiner,
Prop. 5.1). Notation: Zm ⋊ₜ Zn (written `Zm x|t Zn` in the code) is the semidirect product in which the generator of Zn
acts on Zm by multiplication by t; Dn is the dihedral group of order 2n.

**What this repository shows.** No (4,2)-graph was found. The searches below can only find a (4,2)-graph or exclude the
families they cover; they say nothing about other graphs, other groups or other degrees.

1. **No (4,2)-graph contains one of the known r = 1 graphs (exact).** Our search finds exactly five degree-6
   (4,1)-Cayley graphs on S4 × Z2, Z5 ⋊₂ Z12 and Z15 ⋊₂ Z4 up to group automorphism: three on S4 × Z2 (one of them
   Kitamura's graph), Chan's graph, and one on Z15 ⋊₂ Z4 with connection set {(9,2), (9,3), (10,1), (10,3), (12,1),
   (12,2)} (found by this search). None of the five is a subgraph of a (4,2)-graph. Proof idea (`closure944.py`,
   docstring): if H ⊇ G1 is 4-vertex-critical and χ(G1) = 4, then V(H) = V(G1) (otherwise H − v ⊇ G1 for a vertex v
   outside G1). So H = G1 + F for a set F of non-edges, and H is vertex-critical iff for every u some proper 3-colouring
   of G1 − u is also proper on the edges of F not containing u. Since d3(G1) = 2, H has d3 ≥ 3 iff every 3-colouring
   with exactly two monochromatic edges of G1 makes some edge of F monochromatic. Taking F as large as the chosen
   colourings allow, this is one SAT instance per graph; all five are unsatisfiable (CaDiCaL and Glucose agree; solver
   verdicts, no proof certificates). The colourings involved were counted two ways (with and without the symmetry under
   renaming colours, with another solver and cardinality encoding): 1, 1, 8, 16, 16 proper colourings of G1 − e and 1464,
   1464, 3024, 4200, 4200 colourings with exactly two monochromatic edges, up to renaming colours. Log:
   `runs/closure/logs/` (the line "c found falsified original clause" is CaDiCaL's normal message when an instance is
   already unsatisfiable by unit propagation). The S4 × Z2 classes come from the exact enumeration with and without
   symmetry breaking (`vc2_S4xZ2.log`); for the two order-60 groups brute force gives the same witness sets.
2. **Exhaustive search over Cayley graphs** (`cegar944*.py`): no symmetric connection set of size 9 gives a
   (4,2)-graph on any of 137 groups (up to isomorphism) of order 14 to 243; the same holds at size 10 for 136 of them
   (order up to 171) and at sizes 11 and 12 for 104 of them (order up to 126). For a group of odd order there is no
   symmetric S of odd size, so odd sizes are trivially excluded there; the largest even order at sizes 9 and 10 is 156.
   15 further group/degree cases timed out: D42, D48, D60 (orders 84, 96, 120), A5 × Z2, S4 × S3, Z32 ⋊₃ Z8 and
   Z35 ⋊₂ Z12 at sizes 9 and 10, Z27 ⋊₄ Z9 at size 10. Full table: `RESULTS.md`.
3. **Symmetric connection sets on 15 larger groups** (`cegar944s.py`): orders 120 to 504 — A5 × Z2, S5, SL(2,5),
   S4 × S3, PSL(2,7), PGL(2,7), A5 × Z3, A6, PSL(2,8), PSL(2,7) × Z2 and groups close to the r = 1 examples (S4 × Z5,
   S4 × Z6, F20 × Z6, (Z15 ⋊₂ Z4) × Z2, (Z15 ⋊₂ Z4) × Z3). For every automorphism σ of prime order (one per conjugacy
   class in Aut(Γ)), no σ-invariant connection set of size 9 or 10 gives a (4,2)-graph: 182 of the 186 (group, class,
   size) cases are decided (F20 × Z6 was also run under a second name, Z5 ⋊₂ Z12 × Z2, as a consistency check, with the
   same verdicts), 4 are open: PSL(2,7) × Z2 for two classes at size 10, and PSL(2,8) for one class at sizes 9 and 10.
   Hence, apart from these 4 cases, every (4,2)-Cayley graph of degree 9 or 10 on these groups has a connection set
   with trivial stabiliser in Aut(Γ): a (4,r)-graph is connected, so S generates Γ and its stabiliser acts faithfully
   on S; a nontrivial stabiliser therefore contains an automorphism of prime order p ≤ |S|, conjugate to one of the σ
   used, and the search for that σ finds an isomorphic copy. Table: `RESULTS.md`.

**How the searches work.** `cegar944c.py` decides, for a group Γ, r and a degree range, whether some symmetric
S ⊆ Γ \ {e} makes Cay(Γ, S) a (4,r)-graph. One SAT instance contains the choice of S and a proper 3-colouring y of
Cay(Γ, S) − e (the graph is vertex-transitive, so one vertex suffices). Whenever the solver proposes S, a second SAT call
looks for a 3-colouring of Cay(Γ, S) with at most r monochromatic edges; if there is one, the constraint "S has at least
r + 1 edges monochromatic under this colouring" is added (it holds for every witness) and the solver continues; if there
is none, S is a witness and is checked again from the definition (`c944.verify_4r_explicit`). Two sound restrictions
speed this up: every colour of y occurs at least r + 1 times on S (otherwise e could be coloured with at most r bad
edges), and lexicographic symmetry breaking over Aut(Γ). `cegar944s.py` adds the restriction to σ-invariant S, symmetry
breaking over the normaliser of ⟨σ⟩, colour-renaming symmetry, a smaller equivalent encoding of the added constraints,
storage of those constraints, and an optional split into subproblems ("cubes") whose results are saved one by one.

**Validation.**
- Positive controls: the searches find Kitamura's and Chan's graphs (r = 1, degree 6) and the third order-60 example;
  every reported witness is re-checked from the definition. `c944.py` also reproduces the 13 critical edges of the
  13-vertex 6-regular graph of arXiv:2606.18462.
- `cegar944.py` and `cegar944b.py` agree with brute force over all connection sets on small groups (`brute944.py`,
  `review_tmp/`); `cegar944c.py` finds exactly one witness per Aut-orbit against brute force in 86 small cases with
  r = 0, 1 (`validate_c.log`, `vc2_*.log`), gives the verdicts of `cegar944b.py` on 86 groups at r = 1 and on 8 hard
  r = 2 cases (`cmp_c_r1_*.log`, `speed_c_*.log`); Z2 × Z30 at degree 9 was confirmed by brute force over all 64701 sets
  (`brute_Z2xZ30.log`).
- `validate_s.py`: on groups where all witnesses are known (r = 0 and r = 1 cases), the σ search finds exactly the witness
  classes with a nontrivial stabiliser, with and without cubes (`runs/val_s*`, `runs/val_cubes`); with σ = identity it
  gives the same verdicts as `cegar944c.py`. `groups944.py` checks the new groups against known orders and element-order
  statistics (`groups944_check.log`), `auto944.py` checks Aut(Γ) against known orders (`auto944_check.log`).
- The new code was reviewed (read-only) before the long runs; the robustness issues found were fixed and the validation
  repeated.

**Reproducing.** Python 3.12 with `python-sat`. `python closure944.py S4xZ2 1 6` (likewise `'Z5x|2Z12'` and
`'Z15x|2Z4'`, quoted because of the `|`) reproduces part 1. Part 2: `python cegar944c.py GROUP 2 d d`; the larger runs
used `job_c.sh` / `job_b.sh` over `jobs_c.txt` / `jobs_b.txt` with `xargs -L 1`. Part 3 runs through `safe_run.py`
(Windows only: Job Objects with a per-process memory limit; results appended per job, finished jobs skipped on restart):
`runs/sweep9/run_sweep.sh`, `run_t4h.sh`, `run_cubes.sh`. `python compile_results.py` rebuilds `RESULTS.md` from the logs.

**Files.** `c944.py` (groups, Cayley graphs, SAT checks), `search944.py`, `auto944.py` (automorphism groups),
`cegar944.py`, `cegar944b.py`, `cegar944c.py` (exhaustive search, versions a, b, c), `cegar944s.py` (σ search),
`groups944.py` (PSL(2,7), PGL(2,7), SL(2,5), PSL(2,8), products), `closure944.py` (part 1), `validate_c*.py`,
`validate_s.py`, `brute944.py`, `brute_split.py`, `safe_run.py`, `compile_results.py`; logs `*.log`, `runs/`,
`progress/` (cube progress), `review_tmp/` (cross-checks of 26 Sep 2026); job lists `*.txt` and their parts (`a86_*`,
`c86_*`, `l5_*`, `l5r_*`, `sp_*`, `t10_*`).

**Credits.** Kenta Kitamura and Alex Chan for the r = 1 graphs; Ema Skottova and Raphael Steiner (arXiv:2508.08703) for
the k ≥ 5 result and the degree bound; Alper Ferudun (arXiv:2606.18462) for the 13-vertex test graph.

AI-usage disclosure: Claude (Anthropic) was used as assistant.
