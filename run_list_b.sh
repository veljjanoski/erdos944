#!/bin/bash
# usage: run_list.sh LISTFILE r dmin dmax capseconds
while read -r g; do
  [ -z "$g" ] && continue
  timeout "$5" python cegar944b.py "$g" "$2" "$3" "$4" 2>&1 | grep -v "^  " | tail -n 2
  [ ${PIPESTATUS[0]} -eq 124 ] && echo "$g: TIMEOUT after $5 s"
done < "$1"
