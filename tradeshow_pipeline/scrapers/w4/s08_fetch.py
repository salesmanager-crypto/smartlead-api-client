import sys, json, os
sys.path.insert(0,'/home/user/smartlead-api-client/tradeshow_pipeline'); os.chdir('/home/user/smartlead-api-client/tradeshow_pipeline')
from common import fetch
q=open('/tmp/claude-0/-home-user-smartlead-api-client/7519c69d-6156-51fe-ab59-a19f5c60f214/scratchpad/w4/jisq.txt').read()
old='org-bdb7e9dd-9ae4-4ab0-a907-dab300052b6e'
assert old in q
hits=json.load(open('cache/pages/S08/algolia_hits.json'))
out='cache/pages/S08/details.jsonl'
done=set()
if os.path.exists(out):
    for l in open(out): done.add(json.loads(l)['org'])
H={'Origin':'https://www.jisshow.com','Referer':'https://www.jisshow.com/','x-clientid':'uhQVcmxLwXAjVtVpTvoerERiZSsNz0om','accept':'application/json'}
f=open(out,'a')
for i,h in enumerate(hits):
    org=h['organisationGuid']
    if org in done: continue
    r=fetch('https://api.reedexpo.com/graphql/',method='POST',json_body={'query':q.replace(old,org)},headers=H)
    try: d=json.loads(r)['data']['exhibitingOrganisation']
    except Exception as e: print('fail',org,str(r)[:200]); d=None
    f.write(json.dumps({'org':org,'data':d})+'\n'); f.flush(); done.add(org)
    if i%25==0: print(i, h['exhibitorName'], flush=True)
print('DONE')
