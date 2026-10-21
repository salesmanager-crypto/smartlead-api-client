#!/bin/sh
# start N Amazon HTTP workers in the background, PIDs in pipeline/work/amz_http.pids
cd "$(dirname "$0")/.." || exit 1
N=${1:-2}
: > pipeline/work/amz_http.pids
w=0
while [ $w -lt $N ]; do
  nohup python3 pipeline/amazon_http.py run $w $N >> pipeline/work/amz_$w.log 2>&1 &
  echo $! >> pipeline/work/amz_http.pids
  w=$((w+1))
done
