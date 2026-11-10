#!/bin/bash
# Validation of cube splitting and sharding in cegar944s.py (run 2026-11-10 with saved logs; the same checks were first
# run on 6 Nov 2026 without logs).  Everything here is short (minutes); it uses a fast PSL(2,8) lane (sigma class 1) and
# the small groups D20 and A5, and leaves its progress files under runs/val_split/progress/.
cd "$(dirname "$0")/../.."
{
echo "== validate_s.py lanesplit: every pair cube pre-split + 50-conflict budget (CaDiCaL 3.0), enum mode; the sigma lanes"
echo "   must find exactly the witness classes with a nontrivial stabiliser, as computed independently from cegar944c"
python validate_s.py lanesplit D20 0 9
python validate_s.py lanesplit D20 0 10
python validate_s.py lanesplit A5 0 9
} > runs/val_split/lanesplit.log 2>&1
rm -f progress/PSL28_r2_d10-10_s1_*.txt
OPT="--solver cadical300 --presplit 10 --budget 100000"
{
echo "== (a) fast lane PSL28 d10 sigma 1, whole lane with splitting"
python cegar944s.py PSL28 2 10 10 --sigma 1 --cubes --norecord $OPT | tail -n 1
python check_cover.py PSL28_r2_d10-10_s1; python lane_status.py PSL28_r2_d10-10_s1
mkdir -p runs/val_split/progress/whole; mv progress/PSL28_r2_d10-10_s1_*.txt runs/val_split/progress/whole/
echo "== (b) 2 shards with splitting; shard 0 killed after 45 s and resumed"
timeout -s TERM 45 python cegar944s.py PSL28 2 10 10 --sigma 1 --cubes --norecord --shard 0/2 $OPT | tail -n 1
echo "   killed: $(cat progress/PSL28_r2_d10-10_s1_*_shard0of2.txt | wc -l) lines so far"
python cegar944s.py PSL28 2 10 10 --sigma 1 --cubes --norecord --shard 0/2 $OPT | tail -n 1
python cegar944s.py PSL28 2 10 10 --sigma 1 --cubes --norecord --shard 1/2 $OPT | tail -n 1
python check_cover.py PSL28_r2_d10-10_s1; python lane_status.py PSL28_r2_d10-10_s1
mkdir -p runs/val_split/progress/kill_resume; mv progress/PSL28_r2_d10-10_s1_*.txt runs/val_split/progress/kill_resume/
echo "== (c) an unsplit shard 0/2 (CaDiCaL 1.5.3) plus three split shards k/3: the mixed files must cover the lane"
python cegar944s.py PSL28 2 10 10 --sigma 1 --cubes --norecord --shard 0/2 | tail -n 1
for k in 0 1 2; do python cegar944s.py PSL28 2 10 10 --sigma 1 --cubes --norecord --shard $k/3 $OPT | tail -n 1; done
python check_cover.py PSL28_r2_d10-10_s1; python lane_status.py PSL28_r2_d10-10_s1
mkdir -p runs/val_split/progress/mixed; mv progress/PSL28_r2_d10-10_s1_*.txt runs/val_split/progress/mixed/
} > runs/val_split/fastlane.log 2>&1
echo DONE
