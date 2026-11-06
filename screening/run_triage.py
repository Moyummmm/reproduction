#!/usr/bin/env python3
"""Automated title/abstract triage; requires user-configured OpenCode service."""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORDS = HERE.parent / 'search_protocol' / 'records.csv'
PROTOCOL = (HERE / 'protocol.txt').read_text(encoding='utf-8')
MODEL = 'deepseek/deepseek-flash'

def call(batch, records, retry, output):
    base = output / 'batches' / f'batch_{batch:04d}'
    base.mkdir(parents=True, exist_ok=True)
    items = [{'id': r['record_id'], 'title': r['title'], 'year': r['year'], 'abstract': r['abstract'],
              'abstract_status': r['abstract_status']} for r in records]
    prompt = PROTOCOL + ('\n\nOutput ONLY a JSON array, with one object per input, '
        'in the same order. Every object must have exactly these keys: id, decision, '
        'reason, evidence. decision must be POSSIBLE_CORE, EXCLUDE, or UNCLEAR. '
        'Reason and evidence must be short strings. Do not use markdown.\nINPUT:\n') + json.dumps(items,ensure_ascii=False)
    (base / 'prompt.txt').write_text(prompt,encoding='utf-8')
    previous=[int(p.name.split('_')[1].split('.')[0]) for p in base.glob('attempt_*.jsonl')]
    first=max(previous,default=0)+1
    for attempt in range(first,first+retry):
        prefix=base / f'attempt_{attempt:02d}'
        start=datetime.now(timezone.utc).isoformat()
        try:
            p=subprocess.run(['opencode','run','-m',MODEL,'--format','json',prompt], cwd=HERE,
                             capture_output=True,text=True,timeout=600)
            out,err,code=p.stdout,p.stderr,p.returncode
        except subprocess.TimeoutExpired as e:
            out=e.stdout.decode() if isinstance(e.stdout,bytes) else (e.stdout or '')
            err='timeout after 600 seconds'; code=-1
        except OSError as e:
            out=''; err=repr(e); code=-2
        prefix.with_suffix('.jsonl').write_text(out,encoding='utf-8')
        prefix.with_suffix('.stderr.txt').write_text(err,encoding='utf-8')
        meta={'start_utc':start,'end_utc':datetime.now(timezone.utc).isoformat(),'returncode':code,'model':MODEL,'parameters':'not exposed by OpenCode CLI'}
        try:
            events=[json.loads(x) for x in out.splitlines() if x.strip()]
            answer=''.join(e['part']['text'] for e in events if e.get('type')=='text')
            answer=answer.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            result=json.loads(answer)
            ids=[r['record_id'] for r in records]
            assert isinstance(result,list) and len(result)==len(ids)
            assert [x.get('id') for x in result]==ids
            assert all(set(x)=={'id','decision','reason','evidence'} and x['decision'] in {'POSSIBLE_CORE','EXCLUDE','UNCLEAR'} and isinstance(x['reason'],str) and isinstance(x['evidence'],str) and x['reason'] and (x['evidence'] or (not r['title'].strip() and not r['abstract'].strip() and x['decision']=='UNCLEAR')) for x,r in zip(result,records))
            (base/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            meta['valid']=True
            prefix.with_suffix('.meta.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
            return batch,True,''
        except Exception as e:
            meta.update(valid=False, error=str(e))
            prefix.with_suffix('.meta.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    return batch,False,meta['error']

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--batch-size',type=int,default=40); ap.add_argument('--workers',type=int,default=16); ap.add_argument('--retries',type=int,default=2); ap.add_argument('--start',type=int,default=0); ap.add_argument('--end',type=int); ap.add_argument('--abstract-only',action='store_true'); ap.add_argument('--output-dir',default=str(HERE)); ap.add_argument('--input-file',default=str(RECORDS)); ap.add_argument('--expected-sha256',default='f208532691daab6add97eeb13e39322617e1233b0a80a24d4618ae10bb3e09c5'); args=ap.parse_args()
    input_file=Path(args.input_file).resolve()
    with input_file.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    if args.abstract_only: rows=[r for r in rows if r['abstract'].strip()]
    output=Path(args.output_dir).resolve(); output.mkdir(parents=True,exist_ok=True)
    input_hash=hashlib.sha256(input_file.read_bytes()).hexdigest()
    if input_hash != args.expected_sha256: raise ValueError('Input snapshot changed; freeze and review a new protocol run')
    manifest={'input_filename':input_file.name,'input_sha256':input_hash,'protocol_sha256':hashlib.sha256((HERE/'protocol.txt').read_bytes()).hexdigest(),'records':len(rows),'abstract_only':args.abstract_only,'batch_size':args.batch_size,'model':MODEL,'workers':args.workers,'run_start_utc':datetime.now(timezone.utc).isoformat()}
    (output/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    batches=[rows[i:i+args.batch_size] for i in range(0,len(rows),args.batch_size)]
    indices=range(args.start,min(args.end if args.end is not None else len(batches),len(batches)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs=[pool.submit(call,i,batches[i],args.retries,output) for i in indices if not (output/'batches'/f'batch_{i:04d}'/'results.json').exists()]
        for future in concurrent.futures.as_completed(jobs):
            try:
                i,ok,error=future.result(); print(f'batch {i}: {"ok" if ok else "FAILED "+error}',flush=True)
            except Exception as e:
                print(f'batch worker crashed: {e!r}',flush=True)
    print('done',flush=True)
if __name__=='__main__': main()
