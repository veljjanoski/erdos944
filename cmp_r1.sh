#!/bin/bash
# old vs new on r=1 degree 6, 300 s cap each; prints one line per group: group | old verdict | new verdict
while read -r g; do
  [ -z "$g" ] && continue
  o=$(timeout 300 python cegar944.py "$g" 1 6 6 2>&1 | grep -E "WITNESS|NO \(4" | sed 's/.*: //;s/ S=.*//;s/ with degree.*//' ); [ -z "$o" ] && o="TIMEOUT"
  nv=$(timeout 300 python cegar944b.py "$g" 1 6 6 2>&1 | grep -E "WITNESS|NO \(4|Traceback|Assert" | sed 's/.*: //;s/ S=.*//;s/ with degree.*//' ); [ -z "$nv" ] && nv="TIMEOUT"
  echo "$g | old: $o | new: $nv"
done < "$1"
