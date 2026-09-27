"""Save one SmartScout slim-profile batch result.
usage: python3 ss_save.py <batch_file.json> <batch_index> <out.jsonl>  (stdin: one line per returned row:
Brand Name|Primary Category|Primary Subcategory|Total Products|Total Monthly Revenue ; stdin may be empty when nothing matched)
Appends {"batch":i,"queried":[...],"rows":[...]} to out.jsonl. Refuses to double-save a batch index."""
import sys, json, os, datetime
bf, bi, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
queried = json.load(open(bf))[bi]
if os.path.exists(out):
    for l in open(out):
        if json.loads(l)['batch'] == bi: print(f'batch {bi} already saved'); sys.exit(0)
rows = []
for line in sys.stdin.read().strip().splitlines():
    p = [x.strip() for x in line.split('|')]
    if len(p) < 5 or not p[0]: continue
    rows.append({'SmartScout Brand': p[0], 'Primary Category': p[1], 'Primary Subcategory': p[2], 'Total Products': float(p[3] or 0), 'Total Monthly Revenue': float(p[4] or 0)})
with open(out, 'a') as f:
    f.write(json.dumps({'batch': bi, 'source': bf, 'queried': queried, 'rows': rows, 'pulled_at': datetime.datetime.utcnow().isoformat(timespec='seconds')}) + '\n')
print(f'batch {bi}: queried {len(queried)}, returned {len(rows)}')
