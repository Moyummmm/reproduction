#!/usr/bin/env python3
"""Replay saved third-pass responses and conservatively mark bad quotations."""
import collections,csv,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; out=HERE/'third_pass'
manifest=json.loads((out/'manifest.json').read_text())
queue=HERE/'high_priority_review_queue.csv'
assert hashlib.sha256(queue.read_bytes()).hexdigest()==manifest['queue_sha256']
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
paths=[HERE.parent/'search_protocol/records.csv',HERE.parent/'arxiv_pagination/combined_20261105/new_records.csv']
for p in paths: assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest['inputs'][p.name]
sources={r['record_id']:r for p in paths for r in read(p)}
selected=[sources[x['record_id']] for x in read(queue) if sources[x['record_id']]['abstract'].strip()]
results=[]
for i in range((len(selected)+19)//20):
    batch=selected[i*20:(i+1)*20]; p=out/'batches'/f'batch_{i:03d}'/'results.json'
    data=json.loads(p.read_text()) if p.exists() else []
    valid=len(data)==len(batch) and all(x['id']==r['record_id'] for x,r in zip(data,batch))
    if not valid: data=[{'id':r['record_id'],'os_target':'unknown','llm_role':'unknown','security_task':'unknown','evidence':'','suggested':'unclear','uncertainty':'batch missing or invalid'} for r in batch]
    for x,r in zip(data,batch):
        evidence=x['evidence']; exact=bool(evidence and evidence.casefold() in (r['title']+' '+r['abstract']).casefold())
        results.append({'id':x['id'],'os_target':x['os_target'],'llm_role':x['llm_role'],'security_task':x['security_task'],'evidence':evidence,'raw_suggested':x['suggested'],'conservative_suggested':x['suggested'] if exact else 'unclear','uncertainty':x['uncertainty'],'evidence_exact':str(exact).lower(),'review_status':'model recheck only; independent final eligibility review pending'})
with (out/'third_review.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
summary={'records':len(results),'raw':dict(collections.Counter(r['raw_suggested'] for r in results)),'conservative':dict(collections.Counter(r['conservative_suggested'] for r in results)),'evidence_exact':dict(collections.Counter(r['evidence_exact'] for r in results)),'status':'all require independent final eligibility review; model agreement is not accuracy'}
(out/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
