#!/usr/bin/env python3
"""Derive transparent review queues without changing saved model outputs."""
import csv,json,re
from pathlib import Path
from collections import defaultdict,Counter
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent/'audit'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
results=read(HERE/'screening_results.csv')+read(HERE/'arxiv_extension/screening_results.csv')
byid={r['record_id']:r for r in results}
reasons=defaultdict(set)
for r in results:
    if r['raw_model_decision']=='POSSIBLE_CORE': reasons[r['record_id']].add('first-pass possible core')
    if r.get('os_target_hits') and r['raw_model_decision']=='EXCLUDE': reasons[r['record_id']].add('OS target or seed despite model exclusion')
for r in read(HERE/'second_pass/comparison.csv'):
    if r['comparison_status']=='pending_disagreement': reasons[r['record_id']].add('two model passes disagree')
    if r['second_raw']=='POSSIBLE_CORE': reasons[r['record_id']].add('second-pass possible core')
for r in read(AUDIT/'screening_audit_review.csv'):
    if r['same_as_effective'].strip().lower()!='yes': reasons[r['record_id']].add('audit-sample disagreement')
for r in read(AUDIT/'known_study_retention.csv'):
    if r['search_record_id'] in byid: reasons[r['search_record_id']].add('known cited-work seed')
for r in read(AUDIT/'citation_search_mapping.csv'):
    for rid in re.findall(r'R\d{5}',r['search_matches']):
        if rid in byid: reasons[rid].add('matches manuscript citation')
rows=[]
for rid,rs in sorted(reasons.items()):
    if rid not in byid: continue
    r=byid[rid]; high=bool(rs-{'OS target or seed despite model exclusion'})
    rows.append({'record_id':rid,'priority':'high' if high else 'standard','triggers':'; '.join(sorted(rs)), 'title':r['title'],'abstract_status':r['abstract_status'],'source_set':r['source_set'],'raw_model_decision':r['raw_model_decision'],'conservative_decision':r['decision'],'override_reason':r['override_reason'],'status':'pending independent review; not an eligibility decision'})
def write(path,records):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(records)
write(HERE/'priority_review_queue.csv',rows)
high=[r for r in rows if r['priority']=='high']; write(HERE/'high_priority_review_queue.csv',high)
print(json.dumps({'all':len(rows),'high':len(high),'triggers':dict(Counter(x for r in rows for x in r['triggers'].split('; ')))},ensure_ascii=False))
