#!/bin/bash
# The 13 open hard lanes (involution classes, degrees 9/10) in cube mode: every finished cube is saved in
# erdos944/progress/, so a break loses at most the current cube.  Resume: run this script again.  Stop: touch STOP (or STOPNOW).
cd "$(dirname "$0")"
python ../../safe_run.py jobs_cubes.txt results_cubes.jsonl --workers 8 --cap 86400 --mem-gb 2.5 --total-gb 20 --min-free-gb 6 >> runner_cubes.log 2>&1
