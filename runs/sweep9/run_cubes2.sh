#!/bin/bash
# The 4 lanes left open on 2026-09-30, continued with 6 workers (2026-11-05): the two PSL28 lanes are split into
# 2 shards each (--shard k/2, own progress files), the two PSL27xZ2 lanes run whole.  All earlier progress
# (progress/*.txt) is reused.  Resume: run this script again.  Stop: touch STOP (running jobs finish) or STOPNOW.
# Lane verdicts: python ../../lane_status.py   (a lane is NO only when the union of its files covers every cube).
cd "$(dirname "$0")"
# Every job here is resumable (finished cubes are skipped), so on a resume keep only the DONE records: safe_run.py would
# otherwise skip TIMEOUT jobs (the 48 h cap) and FAILED ones after the retry budget (stop_at_boundary.py kills -> FAILED).
[ -f results_cubes2.jsonl ] && python -c "
import json, io
keep = [l for l in io.open('results_cubes2.jsonl', encoding='utf-8') if json.loads(l).get('status') == 'DONE']
io.open('results_cubes2.jsonl', 'w', encoding='utf-8').writelines(keep)"
python ../../safe_run.py jobs_cubes2.txt results_cubes2.jsonl --workers 6 --cap 172800 --mem-gb 2.5 --total-gb 16 --min-free-gb 4 >> runner_cubes2.log 2>&1
