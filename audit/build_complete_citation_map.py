#!/usr/bin/env python3
"""Join citation roles and retrieval matches; roles are provisional, not eligibility."""
import csv,re
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
def read(name):
    with (HERE/name).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
candidate=read('citation_candidate_mapping.csv')
search={r['bibtex_key']:r for r in read('citation_search_mapping.csv')}
unmatched={r['bibtex_key']:r for r in read('unmatched_citation_scope_triage.csv')}
priority={}
for r in read('verified_priority_checks.csv'):
    for key in r['bibtex_key'].split(';'):
        priority.setdefault(key,[]).append((r['candidate_id'],r['primary_evidence_url']))
direct=set('dang2025miggpt lee2024static li2024enhancing li2025portgpt li2025towards mathai2025crashfixer syzagent25 wu2025one yang2025kernelgpt yang2025knighter zhang2024selene'.split())
contexts={}
sections=['introduction','background','methodology','llm_os_security','future','conclusion','appendix_inventory']
for section in sections:
    text=(ROOT/'sections'/f'{section}.tex').read_text(encoding='utf-8')
    text=re.sub(r'\\begin\{comment\}.*?\\end\{comment\}','',text,flags=re.S)
    text=re.sub(r'(?<!\\)%[^\n]*','',text)
    for lineno,line in enumerate(text.splitlines(),1):
        for m in re.finditer(r'\\cite\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}',line):
            for key in m.group(1).split(','):
                contexts.setdefault(key.strip(),[]).append(f'{section}: '+line.strip()[:350])
out=[]
for c in candidate:
    key=c['bibtex_key']; s=search[key]; u=unmatched.get(key)
    if key in direct:
        role='direct candidate claimed or suggested by manuscript; verify scope'
    elif u:
        role=('adjacent or transferable' if u['provisional_group'].startswith('Adjacent') else
              'background' if u['provisional_group'].startswith('Foundational') else
              'direct candidate claimed or suggested by manuscript; verify scope' if u['provisional_group'].startswith('OS-target') else 'unknown')
    elif c['candidate_matches']:
        role='adjacent or transferable; provisional context grouping'
    else:
        role='unknown'
    locations=[]
    if c['candidate_matches']: locations.append('225-candidate inventory')
    if s['search_matches']: locations.append('later search snapshot')
    if not locations: locations.append('manuscript citation only; no match found')
    checks=priority.get(key,[])
    out.append({'bibtex_key':key,'title':c['title'],'manuscript_sections':c['sections'],
                'provisional_context_role':role,'context_examples':' || '.join(contexts.get(key,[])[:2]),
                'candidate_matches':c['candidate_matches'],'later_search_matches':s['search_matches'],
                'source_links_found':'; '.join(locations),
                'source_checked_cases':'; '.join((i+': ' if i else '')+u for i,u in checks),
                'eligibility_status':'unconfirmed; role and string match are not final eligibility'})
with (HERE/'complete_citation_scope_map.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
from collections import Counter
print('citations',len(out),'roles',dict(Counter(x['provisional_context_role'] for x in out)))
