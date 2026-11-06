#!/usr/bin/env python3
"""Prepare separate records from manually documented saved-abstract matches."""
import csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent; audit=HERE.parent/'audit/missing_abstract_crosssource.csv'; raw=HERE.parent/'search_protocol/records.csv'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
orig={r['record_id']:r for r in read(raw)}
items=[]
for m in read(audit):
    if m['text_kind']!='saved_source_abstract' or not m['saved_text'].strip():continue
    r=orig[m['record_id']].copy(); r['abstract']=m['saved_text'];r['abstract_status']='available_via_crosssource';r['crosssource_record_id']=m['source_record_id'];r['crosssource_match_rules']=m['match_rules'];r['crosssource_url']=m['source_url'];r['crosssource_disposition']=m['disposition'];items.append(r)
out=HERE/'crosssource';out.mkdir(exist_ok=True)
with (out/'supplemented_records.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
meta={'audit_mapping_sha256':sha(audit),'original_records_sha256':sha(raw),'supplemented_records_sha256':sha(out/'supplemented_records.csv'),'record_ids':[x['record_id'] for x in items],'prepared_utc':datetime.now(timezone.utc).isoformat(),'note':'Abstracts originate from linked source records in original snapshot; cross-source title/author matching does not alter original search hits or frozen decisions.'}
(out/'source_manifest.json').write_text(json.dumps(meta,indent=2))
print(json.dumps(meta))
