#!/usr/bin/env python3
"""Reconstruct first-pass invocation ranges from retained attempt metadata."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
groups={'initial_attempts_01_02':[],'retry_attempts_03_plus':[]}
for p in sorted((HERE/'batches').glob('batch_*/attempt_*.meta.json')):
    number=int(p.name.split('_')[1].split('.')[0]); d=json.loads(p.read_text())
    groups['initial_attempts_01_02' if number<=2 else 'retry_attempts_03_plus'].append(d)
out=[]
for name,items in groups.items():
    out.append({'invocation':name,'attempt_metadata_count':len(items),'first_start_utc':min((x['start_utc'] for x in items),default=None),'last_end_utc':max((x['end_utc'] for x in items),default=None),'configured_workers':16 if name.startswith('initial') else 2,'worker_count_basis':'observed command invocation; not inferred from timestamps','note':'time range from saved attempt metadata; attempts within each range may overlap'})
(HERE/'first_pass_invocation_history.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
