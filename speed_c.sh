#!/bin/bash
while read -r g r a b; do timeout 7200 python cegar944c.py "$g" "$r" "$a" "$b" 2>&1 | grep -E "NO \(4|WITNESS|Trace" | tail -n 1; done
