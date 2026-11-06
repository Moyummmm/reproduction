#!/usr/bin/env python3
"""Unify saved Crossref and arXiv hits by exact identifier, without screening."""
import collections
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

def read(name):
    with (BASE / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

hits = []
for r in read('crossref/results.csv'):
    hits.append(dict(source='Crossref', query_id=r['query_id'], rank=r['rank'],
                     title=r['title'], authors=r['authors'], year=r['year'],
                     doi=r['doi'], url=r['url'], abstract=r['abstract'], arxiv_id=''))
for r in read('arxiv_results.csv'):
    m = re.search(r'arxiv\.org/(?:abs|pdf)/([^/?#]+)', r['url'], re.I)
    arxiv = re.sub(r'v\d+$', '', m.group(1), flags=re.I) if m else ''
    hits.append(dict(source='arXiv', query_id=r['query_id'], rank=r['rank'],
                     title=r['title'], authors=r['authors'], year=r['year'],
                     doi=r['doi'], url=r['url'], abstract=r['abstract'], arxiv_id=arxiv))

def doi_key(x):
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', x.strip(), flags=re.I).lower()

parent = list(range(len(hits)))
def find(i):
    while i != parent[i]:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
def union(a, b):
    a, b = find(a), find(b)
    if a != b:
        parent[max(a, b)] = min(a, b)

seen = {}
for i, r in enumerate(hits):
    for kind, key in [('doi', doi_key(r['doi'])), ('arxiv', r['arxiv_id'].lower())]:
        if key:
            k = (kind, key)
            if k in seen:
                union(i, seen[k])
            else:
                seen[k] = i

groups = collections.defaultdict(list)
for i, r in enumerate(hits):
    groups[find(i)].append((i, r))

records, mapping = [], []
for num, (_, group) in enumerate(sorted(groups.items()), 1):
    rid = f'R{num:05d}'
    rows = [r for _, r in group]
    # Select longest nonempty abstract from the retrieved records; retain all raw hits.
    best_index, best = max(group, key=lambda item: len(item[1]['abstract'].strip()))
    first = rows[0]
    def unique(field):
        return '; '.join(sorted({r[field].strip() for r in rows if r[field].strip()}))
    records.append(dict(record_id=rid, title=best['title'] or first['title'],
                        authors=best['authors'] or first['authors'], year=best['year'] or first['year'],
                        doi=unique('doi'), arxiv_id=unique('arxiv_id'), abstract=best['abstract'],
                        abstract_status='available' if best['abstract'].strip() else 'missing',
                        source_set=unique('source'), urls=unique('url'), hit_count=len(rows),
                        abstract_source=best['source'] if best['abstract'].strip() else '',
                        abstract_source_hit_id=f'H{best_index+1:06d}' if best['abstract'].strip() else ''))
    for index, r in group:
        mapping.append(dict(hit_id=f'H{index+1:06d}', record_id=rid, source=r['source'],
                            query_id=r['query_id'], rank=r['rank'], doi=r['doi'],
                            arxiv_id=r['arxiv_id'], url=r['url'], title=r['title']))

def write(name, data):
    with (BASE / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)

write('records.csv', records)
write('hit_to_record.csv', mapping)
print('hits:', len(hits), 'records:', len(records))
print('sources:', collections.Counter(r['source'] for r in hits))
print('abstract status:', collections.Counter(r['abstract_status'] for r in records))
