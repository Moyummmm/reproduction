#!/usr/bin/env python3
"""Verify each successful saved result against its raw OpenCode event stream."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
summary={}; errors=[]
for name in ['batches','second_pass/batches','arxiv_extension/batches','third_pass/batches','crosssource/triage/batches']:
    folder=ROOT/name; results=sorted(folder.glob('batch_*/results.json')); checked=0
    for result in results:
        d=result.parent; expected=json.loads(result.read_text())
        metas=sorted(d.glob('attempt_*.meta.json'),key=lambda x:int(re.search(r'attempt_(\d+)',x.name).group(1)))
        success=[p for p in metas if json.loads(p.read_text()).get('valid') is True]
        if not success: errors.append(str(result.relative_to(ROOT))+': no successful metadata');continue
        meta=success[-1]; stem=meta.name.replace('.meta.json',''); raw=d/(stem+'.jsonl')
        try:
            events=[json.loads(line) for line in raw.read_text().splitlines() if line.strip()]
            text=''.join(e['part']['text'] for e in events if e.get('type')=='text').strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
            actual=json.loads(text)
            if actual!=expected: errors.append(str(result.relative_to(ROOT))+': parsed response mismatch')
            else: checked+=1
        except Exception as e: errors.append(str(result.relative_to(ROOT))+': '+repr(e))
    summary[name]={'result_files':len(results),'verified':checked}
report={'groups':summary,'errors':errors,'note':'Equality of parsed saved events with results; does not establish factual correctness.'}
(ROOT/'saved_response_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
if errors: raise SystemExit(1)
