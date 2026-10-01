#!/bin/bash
# #944 sigma-lane sweep, r = 2, degree 9 then 10.  Resumable: just run this script again (finished jobs are skipped).
# Stop cleanly: create the file STOP here (running jobs finish) or STOPNOW (running jobs are killed, and redone on restart).
cd "$(dirname "$0")"
python ../../safe_run.py jobs.txt results9.jsonl --workers 6 --cap 1800 --mem-gb 2.5 --total-gb 15 --min-free-gb 6 >> runner9.log 2>&1
[ -f STOP ] || [ -f STOPNOW ] && exit 0
python ../../safe_run.py jobs10.txt results10.jsonl --workers 6 --cap 1800 --mem-gb 2.5 --total-gb 15 --min-free-gb 6 >> runner10.log 2>&1
