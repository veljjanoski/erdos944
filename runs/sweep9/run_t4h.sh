#!/bin/bash
# re-run of the 16 degree-9/10 timeouts with a 4 h cap (stored cuts are replayed).  Resumable: run again.  Stop: touch STOP.
cd "$(dirname "$0")"
python ../../safe_run.py jobs_t4h.txt results_t4h.jsonl --workers 8 --cap 14400 --mem-gb 2.5 --total-gb 20 --min-free-gb 6 >> runner_t4h.log 2>&1
