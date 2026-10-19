#!/bin/sh
# Start (or restart) the Amazon store crawl with N workers (default 1). One worker is the safe default: Amazon
# flags several sessions from one address at once, even after the soft check.
N=${1:-1}
cd "$(dirname "$0")/.." || exit 1
pkill -f "python3 -u pipeline/amazon_store[.]py run" 2>/dev/null
sleep 1
w=0
while [ "$w" -lt "$N" ]; do
  echo "--- start worker $w of $N $(date -u +%T)" >> pipeline/work/amz_log_$w.txt
  nohup python3 -u pipeline/amazon_store.py run "$w" "$N" >> pipeline/work/amz_log_$w.txt 2>&1 &
  w=$((w + 1))
done
