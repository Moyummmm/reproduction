#!/usr/bin/env python3
"""Freeze a reproducible stratified audit sample of completed decisions."""
import collections
import csv
import hashlib
import json
import random
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESULTS=HERE/'screening_results_sample_frame.csv'
RECORDS=ROOT/'search_protocol/records.csv'
SEED=20261105
PER_STRATUM=10

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))

screened=read(RESULTS)
source={r['record_id']:r for r in read(RECORDS)}
groups=collections.defaultdict(list)
for r in screened:
    if r['raw_model_decision']=='NOT_SCREENED': continue
    raw=r['raw_model_decision']
    has_abstract=bool(source[r['record_id']]['abstract'].strip())
    groups[(raw,'has_abstract' if has_abstract else 'no_abstract')].append(r)
rng=random.Random(SEED); sample=[]
for group,rows in sorted(groups.items()):
    rows=sorted(rows,key=lambda x:x['record_id'])
    for r in sorted(rng.sample(rows,min(PER_STRATUM,len(rows))),key=lambda x:x['record_id']):
        s=source[r['record_id']]
        sample.append({'record_id':r['record_id'],'stratum':':'.join(group),'title':s['title'],
                       'abstract':s['abstract'],'source_url':s['urls'],'model_decision':r['raw_model_decision'],
                       'effective_decision':r['decision'],'model_reason':r['reason'],'model_evidence':r['evidence'],
                       'evidence_match':r['evidence_match']})
if not sample: raise RuntimeError('No completed records; do not draw a premature sample.')
path=HERE/'screening_audit_sample.csv'
if path.exists(): raise RuntimeError('Sample already exists; preserve it and review before drawing again.')
with path.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=sample[0].keys());writer.writeheader();writer.writerows(sample)
meta={'seed':SEED,'per_stratum':PER_STRATUM,'method':'sorted raw model decision x actual abstract present; sample without replacement; only completed model batches',
      'source_results_sha256':hashlib.sha256(RESULTS.read_bytes()).hexdigest(),
      'source_results_snapshot':'audit/screening_results_sample_frame.csv',
      'source_records_sha256':hashlib.sha256(RECORDS.read_bytes()).hexdigest(),
      'completed_population':sum(len(x) for x in groups.values()),
      'strata':{':'.join(k):{'population':len(v),'sample':min(PER_STRATUM,len(v))} for k,v in sorted(groups.items())},
      'limitation':'Small targeted strata are not a representative population estimate; audit is a separate, non-blinded Codex review with prior model labels and reasons visible, not a human or independent screen.'}
(HERE/'screening_audit_sample_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(meta,ensure_ascii=False,indent=2))
