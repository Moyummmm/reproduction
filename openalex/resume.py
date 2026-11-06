#!/usr/bin/env python3
"""Resume unsuccessful OpenAlex batches; honor server cooldown and preserve attempts."""
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
run=Path(sys.argv[1]).resolve()
source=HERE.parent/'search_protocol/records.csv'
manifest=json.loads((run/'input_manifest.json').read_text(encoding='utf-8'))
if hashlib.sha256(source.read_bytes()).hexdigest()!=manifest['frozen_sha256']:
    raise ValueError('frozen input has changed')
logs=[json.loads(s) for s in (run/'request_log.jsonl').read_text(encoding='utf-8').splitlines() if s]
key=os.environ.get('LLM4OSSEC_OPENALEX_API_KEY','').strip()
# Old logs did not extract Retry-After. Read the provider's saved response body.
if not key and logs and logs[-1].get('http_status')==429 and logs[-1].get('raw_file'):
    try:
        body=json.loads((run/logs[-1]['raw_file']).read_text(encoding='utf-8'))
        wait=float(body.get('retryAfter',0))
        then=dt.datetime.fromisoformat(logs[-1]['started_utc'])
        remaining=wait-(dt.datetime.now(dt.timezone.utc)-then).total_seconds()
        if remaining>0:
            print('Rate-limit cooldown active, seconds remaining:',int(remaining),'; no requests made')
            sys.exit(0)
    except (ValueError,TypeError,KeyError):
        print('Could not interpret saved rate-limit cooldown; no requests made')
        sys.exit(1)

previous=run
run=run.parent/(run.name+'_resume_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
shutil.copytree(previous,run)
print('OUTPUT',run,flush=True)
with (run/'input_doi_map.csv').open(encoding='utf-8-sig',newline='') as f:
    dois=sorted({r['doi'] for r in csv.DictReader(f)})
done={x['batch'] for x in logs if x['status']=='ok'}
for start in range(0,len(dois),50):
    batch=start//50+1
    if batch in done: continue
    group=dois[start:start+50]
    params={'filter':'doi:'+'|'.join('https://doi.org/'+d for d in group),
            'select':'id,doi,title,abstract_inverted_index','per-page':'50'}
    url='https://api.openalex.org/works?'+urllib.parse.urlencode(params)
    attempt=1+max([x['attempt'] for x in logs if x['batch']==batch] or [0])
    entry={'batch':batch,'attempt':attempt,'doi_count':len(group),'url':url,
           'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'error',
           'http_status':None,'error':'','raw_file':'','returned':0,'retry_after_seconds':None}
    headers={'User-Agent':'LLM4OSSec-literature-review/1.0','Accept':'application/json'}
    if key: headers['Authorization']='Bearer '+key
    try:
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=50) as res:
            body=res.read(); entry['http_status']=res.status
        name=f'raw/batch_{batch:04d}_attempt_{attempt}.json'
        (run/name).write_bytes(body); entry['raw_file']=name
        obj=json.loads(body); entry.update(status='ok',returned=len(obj.get('results',[])),total=obj.get('meta',{}).get('count'))
    except urllib.error.HTTPError as e:
        body=e.read(); name=f'raw/batch_{batch:04d}_attempt_{attempt}_http_error.txt'
        (run/name).write_bytes(body); entry.update(http_status=e.code,error=str(e),raw_file=name)
        try:
            obj=json.loads(body); entry['retry_after_seconds']=obj.get('retryAfter') or e.headers.get('Retry-After')
        except ValueError: entry['retry_after_seconds']=e.headers.get('Retry-After')
    except (urllib.error.URLError,TimeoutError,ValueError,KeyError) as e: entry['error']=str(e)
    with (run/'request_log.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(entry,ensure_ascii=False)+'\n')
    logs.append(entry)
    print('batch',batch,entry['status'],entry['error'],flush=True)
    # Stop at first error, especially 429; do not hammer the service.
    if entry['status']!='ok': break
    time.sleep(2)
