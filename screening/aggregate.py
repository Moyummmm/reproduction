#!/usr/bin/env python3
"""Report every input, including failed/unrun batches and evidence problems."""
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path
from postprocess_policy import os_target

ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(); ap.add_argument('--input-file',default=str(ROOT.parent/'search_protocol'/'records.csv')); ap.add_argument('--output-dir',default=str(ROOT)); args=ap.parse_args()
HERE=Path(args.output_dir).resolve()
source=Path(args.input_file).resolve()
manifest=json.loads((HERE/'run_manifest.json').read_text(encoding='utf-8'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['input_sha256'], 'input changed'
with source.open(encoding='utf-8-sig',newline='') as f: records=list(csv.DictReader(f))
size=manifest['batch_size']; n=(len(records)+size-1)//size
out=[]; batches=[]
for i in range(n):
    part=records[i*size:(i+1)*size]
    path=HERE/'batches'/f'batch_{i:04d}'/'results.json'
    results=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    valid=len(results)==len(part) and all(x.get('id')==r['record_id'] for x,r in zip(results,part))
    batches.append({'batch':i,'records':len(part),'status':'complete' if valid else 'missing_or_invalid'})
    for j,r in enumerate(part):
        x=results[j] if valid else {'decision':'NOT_SCREENED','reason':'Batch unavailable or invalid','evidence':''}
        year=r['year'].strip(); y=int(year) if re.fullmatch(r'\d{4}',year) else None
        scope=('in_range' if 2020<=y<=2026 else 'outside_range') if y else 'unknown'
        text=(r['title']+' '+r['abstract']).casefold(); evidence=x['evidence'].strip()
        quote='exact' if evidence and evidence.casefold() in text else ('no_source_text' if not text.strip() and not evidence else 'not_exact')
        raw_decision=x['decision']; decision=raw_decision; override=''
        if raw_decision=='EXCLUDE' and not r['abstract'].strip():
            decision='UNCLEAR'; override='missing abstract: title alone cannot establish absence of a core contribution'
        if raw_decision=='EXCLUDE' and quote!='exact':
            decision='UNCLEAR'; override=(override+'; ' if override else '')+'supporting excerpt not verified against source'
        target_hits=os_target(r)
        if raw_decision=='EXCLUDE' and target_hits:
            decision='UNCLEAR'; override=(override+'; ' if override else '')+'OS target or known seed requires review: '+', '.join(target_hits)
        flags=[]
        if quote!='exact': flags.append('quote_'+quote)
        if not r['abstract'].strip(): flags.append('abstract_missing')
        if scope!='in_range': flags.append('year_'+scope)
        if x['decision']=='NOT_SCREENED': flags.append('batch_unavailable')
        out.append({'record_id':r['record_id'],'batch_id':f'{i:04d}','title':r['title'],'year':year,'year_scope':scope,'year_scope_note':'provisional; version and exact dates not independently verified', 'abstract_status':r['abstract_status'],'source_set':r['source_set'],'raw_model_decision':raw_decision,'decision':decision,'override_reason':override,'os_target_hits':'; '.join(target_hits),'reason':x['reason'],'evidence':evidence,'evidence_match':quote,'flags':'; '.join(flags),'review_status':'automated preliminary triage; independent review pending','model':manifest['model']})
with (HERE/'screening_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
with (HERE/'batch_status.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['batch','records','status']); w.writeheader(); w.writerows(batches)
summary={'input_records':len(records),'total_batches':n,'batch_status':dict(collections.Counter(x['status'] for x in batches)),'decisions':dict(collections.Counter(x['decision'] for x in out)),'evidence_match':dict(collections.Counter(x['evidence_match'] for x in out)),'year_scope':dict(collections.Counter(x['year_scope'] for x in out)),'disclaimer':'Automated preliminary triage; all decisions require independent verification. A missing batch is not an exclusion.'}
(HERE/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
