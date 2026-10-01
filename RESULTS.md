# Results (compiled by compile_results.py from the logs)

Group names: Zn cyclic, Dn dihedral of order 2n, Dicn dicyclic of order 4n, Sn/An symmetric/alternating,
Zm x|t Zn the semidirect product where the generator of Zn acts on Zm by multiplication by t, PSL27 = PSL(2,7),
PGL27 = PGL(2,7), SL25 = SL(2,5), PSL28 = PSL(2,8), 'x' = direct product.

## Full search: all symmetric connection sets of the given size (r = 2)

Degrees in the 'NO' column are decided (no (4,2)-Cayley graph of that degree on that group). For a group of odd
order there is no symmetric S of odd size, so odd degrees are trivially NO there. A few groups occur under two
isomorphic names (Z5x|4Z6 = Z15x|4Z2, Z5x|3Z16 = Z5x|2Z16, Z2xZ2xZ2xZ3 = Z2xZ2xZ6, Z3x|2Z4xZ2 = Dic3xZ2).
Programs: a = cegar944.py, b = cegar944b.py, c = cegar944c.py, s-id = cegar944s.py with sigma = id, brute = cegar944b
verdict confirmed by an independent brute force over all connection sets (review_tmp/).

| group | order | NO at degrees | timeout at degrees | programs |
|---|---|---|---|---|
| Z7x\|6Z2 | 14 | 9,10 | - | a,b,c |
| D4xZ2 | 16 | 9,10,11,12 | - | brute |
| D8 | 16 | 9,10,11,12 | - | brute |
| Dic2xZ2 | 16 | 9,10,11,12 | - | brute |
| Dic4 | 16 | 9,10,11,12 | - | brute |
| Z16 | 16 | 9,10,11,12 | - | a,b,brute |
| Z2xZ2xZ2xZ2 | 16 | 9,10,11,12 | - | brute |
| Z2xZ2xZ4 | 16 | 9,10,11,12 | - | brute |
| Z2xZ8 | 16 | 9,10,11,12 | - | brute |
| Z4xZ4 | 16 | 9,10,11,12 | - | brute |
| D9 | 18 | 9,10,11,12 | - | brute |
| S3xZ3 | 18 | 9,10,11,12 | - | brute |
| Z18 | 18 | 9,10,11,12 | - | a,b,brute |
| Z3xZ6 | 18 | 9,10,11,12 | - | brute |
| D10 | 20 | 9,10,11,12 | - | brute |
| Dic5 | 20 | 9,10,11,12 | - | brute |
| Z20 | 20 | 9,10,11,12 | - | a,b,brute |
| Z2xZ10 | 20 | 9,10,11,12 | - | brute |
| Z5x\|2Z4 | 20 | 9,10,11,12 | - | a,b,brute |
| Z21 | 21 | 9,10,11,12 | - | a,b,brute |
| Z7x\|2Z3 | 21 | 9,10,11,12 | - | a,b,brute |
| D11 | 22 | 9,10,11,12 | - | brute |
| Z22 | 22 | 9,10,11,12 | - | a,b,brute |
| A4xZ2 | 24 | 9,10,11,12 | - | a,b,brute |
| D12 | 24 | 9,10,11,12 | - | a,b,brute |
| Dic3xZ2 | 24 | 9,10,11,12 | - | brute |
| Dic6 | 24 | 9,10,11,12 | - | a,b,brute |
| S3xZ4 | 24 | 9,10,11,12 | - | brute |
| S4 | 24 | 9,10,11,12 | - | a,b,brute |
| Z24 | 24 | 9,10,11,12 | - | a,b,brute |
| Z2xZ12 | 24 | 9,10,11,12 | - | a,b,brute |
| Z2xZ2xZ2xZ3 | 24 | 9,10,11,12 | - | brute |
| Z2xZ2xZ6 | 24 | 9,10,11,12 | - | brute |
| Z3x\|2Z4xZ2 | 24 | 9,10,11,12 | - | brute |
| Z3x\|2Z8 | 24 | 9,10,11,12 | - | a,b,brute |
| Z26 | 26 | 9,10,11,12 | - | a,b |
| Z27 | 27 | 9,10,11,12 | - | a,b |
| Z9x\|4Z3 | 27 | 9,10 | - | a,b |
| Z28 | 28 | 9,10,11,12 | - | a,b |
| D15 | 30 | 9,10,11,12 | - | a,b |
| Z15x\|4Z2 | 30 | 9,10 | - | a,b |
| Z30 | 30 | 9,10,11,12 | - | a,b |
| Z5x\|4Z6 | 30 | 9 | - | a,b |
| Dic8 | 32 | 9,10,11,12 | - | a,b |
| Z2xZ2xZ8 | 32 | 9,10,11,12 | - | a,b |
| Z2xZ4xZ4 | 32 | 9,10,11,12 | - | a,b |
| Z32 | 32 | 9,10,11,12 | - | a,b |
| Z33 | 33 | 9,10,11,12 | - | a,b |
| Z35 | 35 | 9,10,11,12 | - | a,b |
| A4xZ3 | 36 | 9,10,11,12 | - | a,b |
| D18 | 36 | 9,10,11,12 | - | a,b |
| Z2xZ18 | 36 | 9,10,11,12 | - | a,b |
| Z36 | 36 | 9,10,11,12 | - | a,b |
| Z3xZ12 | 36 | 9,10,11,12 | - | a,b |
| Z6xZ6 | 36 | 9,10,11,12 | - | a,b |
| Z13x\|3Z3 | 39 | 9,10,11,12 | - | a,b |
| Z39 | 39 | 9,10,11,12 | - | a,b |
| D20 | 40 | 9,10,11,12 | - | a,b |
| Z2xZ20 | 40 | 9,10,11,12 | - | a,b |
| Z40 | 40 | 9,10,11,12 | - | a,b |
| Z5x\|2Z8 | 40 | 9,10,11,12 | - | a,b |
| D21 | 42 | 9,10,11,12 | - | a,b |
| Z42 | 42 | 9,10,11,12 | - | a,b |
| Z7x\|2Z6 | 42 | 9,10,11,12 | - | a,b |
| Z7x\|3Z6 | 42 | 9,10,11,12 | - | a,b |
| Z44 | 44 | 9,10,11,12 | - | a,b |
| Z3xZ15 | 45 | 9,10,11,12 | - | a,b |
| Z45 | 45 | 9,10,11,12 | - | a,b |
| A4xZ4 | 48 | 9,10,11,12 | - | a,b |
| D24 | 48 | 9,10,11,12 | - | a,b,c,s-id |
| Dic12 | 48 | 9,10,11,12 | - | a,b |
| S4xZ2 | 48 | 9,10,11,12 | - | a,b |
| Z2xZ24 | 48 | 9,10,11,12 | - | a,b |
| Z2xZ2xZ12 | 48 | 9,10,11,12 | - | a,b |
| Z3x\|2Z16 | 48 | 9,10 | - | a,b |
| Z48 | 48 | 9,10,11,12 | - | a,b |
| Z4xZ12 | 48 | 9,10,11,12 | - | a,b |
| Z50 | 50 | 9,10,11,12 | - | a,b |
| Z13x\|5Z4 | 52 | 9,10,11,12 | - | a,b |
| Z52 | 52 | 9,10,11,12 | - | a,b |
| Z3xZ18 | 54 | 9,10,11,12 | - | a,b |
| Z3xZ3xZ6 | 54 | 9,10,11,12 | - | a,b |
| Z54 | 54 | 9,10,11,12 | - | a,b |
| Z9x\|2Z6 | 54 | 9,10,11,12 | - | a,b |
| Z11x\|3Z5 | 55 | 9,10,11,12 | - | a,b |
| Z56 | 56 | 9,10,11,12 | - | a,b |
| Z19x\|7Z3 | 57 | 9,10 | - | b |
| A4xZ5 | 60 | 9,10,11,12 | - | a,b |
| A5 | 60 | 9,10,11,12 | - | a,b |
| D30 | 60 | 9,10,11,12 | - | a,c |
| Dic15 | 60 | 9,10,11,12 | - | a,b |
| Z15x\|2Z4 | 60 | 9,10,11,12 | - | a,b |
| Z2xZ30 | 60 | 9,10,11,12 | - | a,b |
| Z5x\|2Z12 | 60 | 9,10,11,12 | - | a,b |
| Z60 | 60 | 9,10,11,12 | - | a,b |
| Z21x\|4Z3 | 63 | 9,10 | - | a,b |
| Z3xZ21 | 63 | 9,10,11,12 | - | a,b |
| Z63 | 63 | 9,10,11,12 | - | a,b |
| Z7x\|2Z9 | 63 | 9,10 | - | a,b |
| Z16x\|3Z4 | 64 | 9,10,11,12 | - | a,b |
| Z16x\|5Z4 | 64 | 9,10 | - | b |
| Z4xZ16 | 64 | 9,10,11,12 | - | a,b |
| Z64 | 64 | 9,10,11,12 | - | a,b |
| Z8xZ8 | 64 | 9,10,11,12 | - | a,b |
| Z66 | 66 | 9,10,11,12 | - | a,b |
| Z17x\|4Z4 | 68 | 9,10 | - | b,c |
| Z70 | 70 | 9,10,11,12 | - | a,b |
| A4xS3 | 72 | 9,10 | - | a,b |
| A4xZ6 | 72 | 9,10,11,12 | - | a,b |
| D36 | 72 | 9,10 | - | c |
| Dic18 | 72 | 9,10 | - | b |
| S4xZ3 | 72 | 9,10,11,12 | - | a,b |
| Z2xZ36 | 72 | 9,10,11,12 | - | a,b |
| Z2xZ6xZ6 | 72 | 9,10,11,12 | - | a,b |
| Z6xZ12 | 72 | 9,10,11,12 | - | a,b |
| Z72 | 72 | 9,10,11,12 | - | a,b |
| Z2xZ40 | 80 | 9,10,11,12 | - | a,b |
| Z5x\|2Z16 | 80 | 9,10 | - | a,b |
| Z5x\|3Z16 | 80 | 9 | - | a,b |
| Z80 | 80 | 9,10 | - | b,c,s-id |
| A4xZ7 | 84 | 9,10 | - | a,b |
| D42 | 84 | - | 9,10 |  |
| Z7x\|2Z12 | 84 | 9,10 | - | a,b |
| Z84 | 84 | 9,10 | - | b,c |
| Z90 | 90 | 9,10 | - | b,c |
| A4xZ8 | 96 | 9,10 | - | a,b,c |
| D48 | 96 | - | 9,10 |  |
| Dic24 | 96 | 9,10 | - | b |
| S4xZ4 | 96 | 9,10 | - | c,s-id |
| Z96 | 96 | 9,10 | - | b,c |
| Z100 | 100 | 9,10 | - | b,c |
| Z25x\|7Z4 | 100 | 9,10 | - | c |
| Z105 | 105 | 9,10 | - | b,c |
| Z108 | 108 | 9,10 | - | b,c |
| Z11x\|2Z10 | 110 | 9,10,11,12 | - | c |
| Z112 | 112 | 9,10 | - | b,c |
| A5xZ2 | 120 | - | 9,10 |  |
| D60 | 120 | - | 9,10 |  |
| Dic30 | 120 | 9,10 | - | b |
| Z120 | 120 | 9,10 | - | b,c |
| Z21x\|2Z6 | 126 | 9,10,11,12 | - | a |
| Z17x\|2Z8 | 136 | 9,10 | - | c |
| S4xS3 | 144 | - | 9,10 |  |
| Z13x\|2Z12 | 156 | 9,10 | - | c |
| Z19x\|4Z9 | 171 | 9,10 | - | b,c |
| Z27x\|4Z9 | 243 | 9 | 10 | b |
| Z32x\|3Z8 | 256 | - | 9,10 |  |
| Z35x\|2Z12 | 420 | - | 9,10 |  |

Up to isomorphism: 137 groups; decided at degree 9 for 137, at 10 for 136, at 11 and 12 for 104.

141 group names (orders 14..243), 491 decided (name, degree) cases; degrees 9-12 all decided for 106 groups (orders up to 126); 15 cases timed out (A5xZ2 d9, A5xZ2 d10, D42 d9, D42 d10, D48 d9, D48 d10, D60 d9, D60 d10, S4xS3 d9, S4xS3 d10, Z27x\|4Z9 d10, Z32x\|3Z8 d9, Z32x\|3Z8 d10, Z35x\|2Z12 d9, Z35x\|2Z12 d10).

## Sigma lane: connection sets fixed by an automorphism of prime order (r = 2, degrees 9 and 10)

One row per group; 'classes' = conjugacy classes of automorphisms of prime order, one lane each. Z5x|2Z12xZ2 and
Z5x|2Z4xZ6 are the same group (F20 x Z6, since Z5x|2Z12 = F20 x Z3); it was run under both names.

| group | order | Aut | classes | degree 9 | degree 10 |
|---|---|---|---|---|---|
| A5xZ2 | 120 | 120 | 4 | all NO | all NO |
| S4xZ5 | 120 | 96 | 6 | all NO | all NO |
| S5 | 120 | 120 | 4 | all NO | all NO |
| SL25 | 120 | 120 | 4 | all NO | all NO |
| Z15x\|2Z4xZ2 | 120 | 240 | 9 | all NO | all NO |
| Z5x\|2Z12xZ2 | 120 | 80 | 8 | all NO | all NO |
| Z5x\|2Z4xZ6 | 120 | 80 | 8 | all NO | all NO |
| S4xS3 | 144 | 144 | 8 | all NO | all NO |
| S4xZ6 | 144 | 96 | 12 | all NO | all NO |
| PSL27 | 168 | 336 | 4 | all NO | all NO |
| A5xZ3 | 180 | 240 | 7 | all NO | all NO |
| Z15x\|2Z4xZ3 | 180 | 240 | 9 | all NO | all NO |
| PGL27 | 336 | 336 | 4 | all NO | all NO |
| PSL27xZ2 | 336 | 336 | 4 | all NO | c1: open (cube run stopped); c3: open (cube run stopped) |
| A6 | 360 | 1440 | 5 | all NO | all NO |
| PSL28 | 504 | 1512 | 5 | c4: open (cube run stopped) | c4: open (cube run stopped) |

198 of 202 lane runs NO (182 of 186 distinct (group, class, degree) cases); open: PSL27xZ2 d10 c1, PSL27xZ2 d10 c3, PSL28 d9 c4, PSL28 d10 c4
