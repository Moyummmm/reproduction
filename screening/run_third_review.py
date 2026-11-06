#!/usr/bin/env python3
import concurrent.futures,csv,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
model='deepseek/deepseek-flash'; protocol=(HERE/'third_review_protocol.txt').read_text()
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
inputs=[HERE.parent/'search_protocol/records.csv',HERE.parent/'arxiv_pagination/combined_20261105/new_records.csv']
sources={r['record_id']:r for p in inputs for r in read(p)}
queue=read(HERE/'high_priority_review_queue.csv')
selected=[sources[x['record_id']] for x in queue if sources[x['record_id']]['abstract'].strip()]
out=HERE/'third_pass';out.mkdir(exist_ok=True)
manifest={'inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'queue_sha256':hashlib.sha256((HERE/'high_priority_review_queue.csv').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((HERE/'third_review_protocol.txt').read_bytes()).hexdigest(),'records':len(selected),'model':model,'client':'opencode v2.2.5','model_snapshot':'unknown','generation_parameters':'unknown','started_utc':datetime.now(timezone.utc).isoformat(),'batch_size':20}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
def run(i,rows):
    d=out/'batches'/f'batch_{i:03d}';d.mkdir(parents=True,exist_ok=True)
    payload=[{'id':r['record_id'],'title':r['title'],'abstract':r['abstract']} for r in rows]
    prompt=protocol+'\nINPUT:\n'+json.dumps(payload,ensure_ascii=False);(d/'prompt.txt').write_text(prompt)
    for attempt in range(1,4):
        start=datetime.now(timezone.utc).isoformat()
        try:
            p=subprocess.run(['opencode','run','-m',model,'--format','json',prompt],capture_output=True,text=True,timeout=600,cwd=HERE)
            stdout,stderr,code=p.stdout,p.stderr,p.returncode
        except Exception as e: stdout='';stderr=repr(e);code=-1
        (d/f'attempt_{attempt}.jsonl').write_text(stdout);(d/f'attempt_{attempt}.stderr.txt').write_text(stderr)
        meta={'start_utc':start,'end_utc':datetime.now(timezone.utc).isoformat(),'exit_code':code}
        try:
            events=[json.loads(x) for x in stdout.splitlines() if x.strip()]
            text=''.join(e['part']['text'] for e in events if e.get('type')=='text').strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            data=json.loads(text); assert len(data)==len(rows) and [x['id'] for x in data]==[r['record_id'] for r in rows]
            assert all(set(x)=={'id','os_target','llm_role','security_task','evidence','suggested','uncertainty'} and x['suggested'] in {'possible_core','adjacent','unclear'} for x in data)
            (d/'results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));meta['valid']=True
            (d/f'attempt_{attempt}.meta.json').write_text(json.dumps(meta,indent=2));return (i,True)
        except Exception as e:
            meta.update(valid=False,error=repr(e));(d/f'attempt_{attempt}.meta.json').write_text(json.dumps(meta,indent=2))
    return i,False
batches=[selected[i:i+20] for i in range(0,len(selected),20)]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    for f in concurrent.futures.as_completed([pool.submit(run,i,b) for i,b in enumerate(batches)]): print(f.result(),flush=True)
results=[]
for i,batch in enumerate(batches):
    p=out/'batches'/f'batch_{i:03d}'/'results.json'
    data=json.loads(p.read_text()) if p.exists() else []
    if len(data)!=len(batch):
        data=[{'id':r['record_id'],'os_target':'unknown','llm_role':'unknown','security_task':'unknown','evidence':'','suggested':'unclear','uncertainty':'batch failed'} for r in batch]
    for x,r in zip(data,batch):
        x['evidence_exact']=str(bool(x['evidence'] and x['evidence'].casefold() in (r['title']+' '+r['abstract']).casefold())).lower()
        x['raw_suggested']=x.pop('suggested')
        x['conservative_suggested']=x['raw_suggested'] if x['evidence_exact']=='true' else 'unclear'
        x['review_status']='model recheck only; independent final eligibility review pending'
        results.append(x)
with (out/'third_review.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
print('completed',len(results))
