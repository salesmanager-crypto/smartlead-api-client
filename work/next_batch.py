import sys, json; from helpers import *
todo=next_batch(int(sys.argv[1]) if len(sys.argv)>1 else 25)
for x in todo:
    print(json.dumps({k:x[k] for k in ['row','key','query','sold_by','note','subcat','org','url','summary','cached'] if x.get(k) is not None}, ensure_ascii=False))
print(status())
