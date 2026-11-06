#!/usr/bin/env python3
"""Reconstruct a record-level supplemental abstract table from saved responses."""
import collections
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
SOURCE=BASE.parent/'search_protocol/records.csv'
run=Path(sys.argv[1]).resolve()
manifest=json.loads((run/'input_manifest.json').read_text(encoding='utf-8'))
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=manifest['frozen_sha256']:
    raise ValueError('frozen source hash differs from fetch input')

def norm(x):
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)','',str(x or '').strip(),flags=re.I).lower()
def expand(inv):
    try:
        positions={}
        for word, indices in inv.items():
            for pos in indices:
                if not isinstance(pos,int) or pos<0 or (pos in positions and positions[pos]!=word):
                    return None
                positions[pos]=word
        if not positions or sorted(positions)!=list(range(max(positions)+1)):
            return None
        return ' '.join(positions[i] for i in range(max(positions)+1))
    except (AttributeError,TypeError,ValueError): return None

with SOURCE.open(encoding='utf-8-sig',newline='') as f:
    rows=[r for r in csv.DictReader(f) if r['abstract_status']=='missing']
with (run/'input_doi_map.csv').open(encoding='utf-8-sig',newline='') as f:
    pairs=list(csv.DictReader(f))
dois=sorted({r['doi'] for r in pairs})
by_record=collections.defaultdict(list)
for r in pairs: by_record[r['record_id']].append(r['doi'])
logs=[]
if (run/'request_log.jsonl').exists():
    logs=[json.loads(line) for line in (run/'request_log.jsonl').read_text(encoding='utf-8').splitlines() if line]
by_batch=collections.defaultdict(list)
for log in logs: by_batch[log['batch']].append(log)
outcomes={}
for start in range(0,len(dois),50):
    group=dois[start:start+50]; batch=start//50+1; entries=by_batch.get(batch,[])
    good=[x for x in entries if x['status']=='ok']
    if not good:
        status='request_error' if entries else 'not_attempted'
        for d in group: outcomes[d]={'status':status,'batch':batch}
        continue
    log=good[-1]; raw=json.loads((run/log['raw_file']).read_text(encoding='utf-8'))
    found=collections.defaultdict(list)
    for work in raw.get('results',[]): found[norm(work.get('doi'))].append(work)
    truncated=raw.get('meta',{}).get('count',0)>len(raw.get('results',[]))
    for d in group:
        works=found.get(norm(d),[])
        if not works:
            outcomes[d]={'status':'response_truncated' if truncated else 'not_found','batch':batch,'timestamp':log['started_utc']}; continue
        choices=[]
        for work in works:
            inv=work.get('abstract_inverted_index')
            abstract=expand(inv) if inv else ''
            status='available' if abstract else ('invalid_index' if inv else 'openalex_no_abstract')
            choices.append({'status':status,'abstract':abstract or '', 'batch':batch,'timestamp':log['started_utc'],
                            'work_id':work.get('id',''),'openalex_doi':work.get('doi',''),'openalex_title':work.get('title','')})
        outcomes[d]=next((x for x in choices if x['status']=='available'),choices[0])

result=[]
for r in rows:
    ds=by_record.get(r['record_id'],[]); choices=[(d,outcomes[d]) for d in ds]
    d,o=next(((d,o) for d,o in choices if o['status']=='available'),choices[0] if choices else ('',{'status':'no_doi'}))
    result.append({'record_id':r['record_id'],'original_title':r['title'],'matched_doi':d,
                   'supplement_status':o['status'],'abstract':o.get('abstract',''),
                   'openalex_work_id':o.get('work_id',''),'openalex_doi':o.get('openalex_doi',''),
                   'openalex_title':o.get('openalex_title',''),'batch':o.get('batch',''),
                   'request_started_utc':o.get('timestamp','')})
with (run/'supplement.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(result[0])); w.writeheader(); w.writerows(result)
summary={'frozen_missing_records':len(rows),'status_counts':dict(collections.Counter(r['supplement_status'] for r in result)),
         'successful_batches':sum(any(x['status']=='ok' for x in es) for es in by_batch.values()),
         'attempted_batches':len(by_batch),'total_batches':(len(dois)+49)//50,
         'note':'DOI matching is exact; OpenAlex result or an abstract does not verify study eligibility.'}
(run/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
