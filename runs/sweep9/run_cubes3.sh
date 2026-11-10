#!/bin/bash
# The 2 PSL28 lanes left open (2026-11-06), resumed with cube splitting: CaDiCaL 3.0, pairs (i,j) with i >= j-10 pre-split,
# any cube that 100000 conflicts do not finish is split (measured 2026-11-06: the 5 h cube (14,15) of d10 takes 37 min,
# the 2.8 h cube (14,18) of d9 21 min, no sub-cube over 1 min; rows j >= 40 take seconds).  6 shards per lane = 12 workers (all 12 cores of the Ryzen 5900X, overnight run; workers run BELOW_NORMAL);
# all earlier progress (whole-lane and 2-shard files) is reused.  Resume: run this script again.  Stop: touch STOP (running
# jobs finish) or STOPNOW (loses at most the current sub-cube, i.e. about a minute per worker).
# Lane verdicts: python ../../lane_status.py   (a lane is NO only when the union of its files covers every cube).
cd "$(dirname "$0")"
[ -f results_cubes3.jsonl ] && python -c "
import json, io
keep = [l for l in io.open('results_cubes3.jsonl', encoding='utf-8') if json.loads(l).get('status') == 'DONE']
io.open('results_cubes3.jsonl', 'w', encoding='utf-8').writelines(keep)"
python ../../safe_run.py jobs_cubes3.txt results_cubes3.jsonl --workers 12 --cap 172800 --mem-gb 2.5 --total-gb 20 --min-free-gb 4 >> runner_cubes3.log 2>&1
