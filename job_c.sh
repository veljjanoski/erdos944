#!/bin/bash
# one job: GROUP r dmin dmax cap -> appends verdict to frontier_c.log (TIMEOUT only on exit code 124, anything else = FAILED)
cap="${5%$'\r'}"
res=$(timeout "$cap" python cegar944c.py "$1" "$2" "$3" "$4" 2>&1); rc=$?
out=$(echo "$res" | grep -E "WITNESS|NO \(4" | tail -n 1)
if [ -n "$out" ]; then echo "$out" >> frontier_c.log
elif [ $rc -eq 124 ]; then echo "$1 deg $3: TIMEOUT after $cap s" >> frontier_c.log
else echo "$1 deg $3: FAILED rc=$rc $(echo "$res" | tail -n 1)" >> frontier_c.log; fi
