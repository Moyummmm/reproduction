#!/usr/bin/env python3
"""Freeze screening artifacts and the documented external input snapshots."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPRODUCT=ROOT.parent
files=[p for p in ROOT.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts]
for path in ['search_protocol/records.csv','arxiv_pagination/combined_20261105/new_records.csv',
             'audit/screening_results_sample_frame.csv','audit/screening_audit_review.csv',
             'audit/known_study_retention.csv','audit/citation_search_mapping.csv','audit/missing_abstract_crosssource.csv']:
    files.append(REPRODUCT/path)
files=sorted(set(files),key=lambda p:str(p.relative_to(REPRODUCT)))
lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(REPRODUCT)) for p in files]
(ROOT/'SHA256SUMS').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('checksummed',len(lines),'files; SHA256SUMS excludes itself')
