#!/usr/bin/env python3
"""Compare separate model calls; disagreements remain pending review."""
import collections,csv,hashlib,json
from pathlib import Path
from postprocess_policy import os_target
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'second_pass/run_manifest.json').read_text(encoding='utf-8'))
source=HERE.parent/'search_protocol/records.csv'
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['input_sha256']
with source.open(encoding='utf-8-sig',newline='') as f: all_records=list(csv.DictReader(f))
with (HERE/'screening_results.csv').open(encoding='utf-8-sig',newline='') as f: first={r['record_id']:r for r in csv.DictReader(f)}
rows=[r for r in all_records if r['abstract'].strip()]; size=manifest['batch_size']; result=[]
for i in range((len(rows)+size-1)//size):
    part=rows[i*size:(i+1)*size]; path=HERE/'second_pass/batches'/f'batch_{i:04d}'/'results.json'
    second=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    valid=len(part)==len(second) and all(a.get('id')==b['record_id'] for a,b in zip(second,part))
    for j,r in enumerate(part):
        a=first[r['record_id']]; b=second[j] if valid else {'decision':'NOT_SCREENED','reason':'missing or invalid batch','evidence':''}
        evidence=b['evidence'].strip(); exact=bool(evidence and evidence.casefold() in (r['title']+' '+r['abstract']).casefold())
        conservative='UNCLEAR' if b['decision']=='EXCLUDE' and (not exact or os_target(r)) else b['decision']
        if a['decision']=='NOT_SCREENED' or conservative=='NOT_SCREENED': status='pending_missing_pass'
        elif a['decision']!=conservative: status='pending_disagreement'
        else: status='agreement_still_requires_independent_review'
        result.append({'record_id':r['record_id'],'first_raw':a['raw_model_decision'],'first_adjusted':a['decision'],'second_raw':b['decision'],'second_adjusted':conservative,'second_reason':b['reason'],'second_evidence':evidence,'second_evidence_exact':str(exact).lower(),'comparison_status':status})
with (HERE/'second_pass/comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(result[0])); w.writeheader(); w.writerows(result)
summary={'records':len(result),'comparison_status':dict(collections.Counter(r['comparison_status'] for r in result)), 'note':'Separate calls to the same model, not independent human review; agreement is not eligibility.'}
(HERE/'second_pass/comparison_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
