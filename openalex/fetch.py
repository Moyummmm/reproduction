#!/usr/bin/env python3
"""Fetch OpenAlex abstract metadata for records missing abstracts in a frozen snapshot."""
import csv
import datetime as dt
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parent / 'search_protocol' / 'records.csv'
EXPECTED = 'f208532691daab6add97eeb13e39322617e1233b0a80a24d4618ae10bb3e09c5'

def main():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED:
        raise ValueError('Frozen records hash mismatch; no requests made')
    with SOURCE.open(encoding='utf-8-sig', newline='') as f:
        rows = [r for r in csv.DictReader(f) if r['abstract_status'] == 'missing']
    pairs = [(r['record_id'], d.strip().lower()) for r in rows for d in r['doi'].split(';') if d.strip()]
    dois = sorted({d for _, d in pairs})
    out = BASE / ('run_' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir(exist_ok=False)
    (out/'raw').mkdir()
    with (out/'input_doi_map.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['record_id','doi']); w.writerows(pairs)
    (out/'input_manifest.json').write_text(json.dumps({'frozen_sha256':digest,'missing_records':len(rows),
        'record_doi_pairs':len(pairs),'unique_dois':len(dois),'batch_size':50,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat()},indent=2),encoding='utf-8')
    for n in range(0,len(dois),50):
        group = dois[n:n+50]
        batch = n//50 + 1
        params = {'filter':'doi:'+'|'.join('https://doi.org/'+d for d in group),
                  'select':'id,doi,title,abstract_inverted_index','per-page':'50'}
        url = 'https://api.openalex.org/works?' + urllib.parse.urlencode(params)
        success = False
        for attempt in range(1,5):
            entry = {'batch':batch,'attempt':attempt,'doi_count':len(group),'url':url,
                     'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':'error',
                     'http_status':None,'error':'','raw_file':'','returned':0,'retry_after_seconds':None}
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'LLM4OSSec-literature-review/1.0','Accept':'application/json'})
                with urllib.request.urlopen(req,timeout=50) as response:
                    body=response.read(); entry['http_status']=response.status
                name=f'raw/batch_{batch:04d}_attempt_{attempt}.json'
                (out/name).write_bytes(body); entry['raw_file']=name
                obj=json.loads(body); entry.update(status='ok',returned=len(obj.get('results',[])),total=obj.get('meta',{}).get('count'))
                success=True
            except urllib.error.HTTPError as e:
                entry['http_status']=e.code; entry['error']=str(e)
                body=e.read(); name=f'raw/batch_{batch:04d}_attempt_{attempt}_http_error.txt'
                (out/name).write_bytes(body); entry['raw_file']=name
                try: entry['retry_after_seconds']=json.loads(body).get('retryAfter') or e.headers.get('Retry-After')
                except ValueError: entry['retry_after_seconds']=e.headers.get('Retry-After')
            except (urllib.error.URLError,TimeoutError,ValueError,KeyError) as e:
                entry['error']=str(e)
            with (out/'request_log.jsonl').open('a',encoding='utf-8') as f:
                f.write(json.dumps(entry,ensure_ascii=False)+'\n')
            print('batch',batch,'/',(len(dois)+49)//50,'attempt',attempt,entry['status'],entry['returned'],entry['error'],flush=True)
            if success or entry['http_status']==429: break
            if attempt<4: time.sleep([5,15,30][attempt-1])
        if not success:
            print('Stopped after failed batch; remaining requests not attempted.',flush=True)
            break
        time.sleep(1.3)
    print('OUTPUT',out,flush=True)

if __name__=='__main__': main()
