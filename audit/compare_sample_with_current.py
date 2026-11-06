#!/usr/bin/env python3
"""Compare frozen model audit decisions to the latest conservative guard output."""
import csv,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
review=read(P/'screening_audit_review.csv')
currentfile=P.parent/'screening/screening_results.csv'
current={r['record_id']:r for r in read(currentfile)}
rows=[]
for r in review:
    c=current[r['record_id']]
    rows.append({'record_id':r['record_id'],'stratum':r['stratum'],'sample_frame_decision':r['model_effective'],
                 'current_decision':c['decision'],'audit_proposed':r['audit_proposed'],
                 'audit_differs_current':'yes' if r['audit_proposed']!=c['decision'] else 'no',
                 'rationale':r['rationale'],'review_status':'Codex audit; adjudication pending'})
with (P/'screening_audit_current_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
priority=[r for r in rows if r['audit_proposed']=='UNCLEAR' and r['current_decision']=='POSSIBLE_CORE']
with (P/'screening_audit_manual_review_queue.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(priority)
(P/'screening_audit_current_comparison_manifest.json').write_text(json.dumps({'current_results_sha256':hashlib.sha256(currentfile.read_bytes()).hexdigest(),'sample_rows':len(rows),'priority_pending':len(priority),'note':'Small purposive audit; disagreements are not verified errors or a representative error rate.'},indent=2)+'\n')
print('sample rows',len(rows),'priority pending',len(priority),'changed since frozen frame',sum(r['sample_frame_decision']!=r['current_decision'] for r in rows))
