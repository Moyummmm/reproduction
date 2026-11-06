#!/usr/bin/env python3
"""Compare one paginated refresh with the frozen identifier-level search inventory."""
import collections
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN = HERE.parent / 'search_protocol' / 'records.csv'
run = Path(sys.argv[1]).resolve()

def load(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def arxiv(url):
    m = re.search(r'arxiv\.org/(?:abs|pdf)/(.+?)(?:v\d+)?(?:\.pdf)?$', url.strip(), re.I)
    return m.group(1).lower() if m else ''

def doi(value):
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value.strip(), flags=re.I).lower()

old = load(FROZEN)
by_arxiv = collections.defaultdict(set)
by_doi = collections.defaultdict(set)
for r in old:
    for x in r['arxiv_id'].split(';'):
        if x.strip():
            by_arxiv[x.strip().lower()].add(r['record_id'])
    for x in r['doi'].split(';'):
        if doi(x):
            by_doi[doi(x)].add(r['record_id'])

groups = collections.defaultdict(list)
for r in load(run / 'results.csv'):
    key = arxiv(r['id'])
    if not key:
        raise ValueError('Unrecognized arXiv identifier: ' + r['id'])
    groups[key].append(r)

new, links = [], []
counts = collections.Counter()
for key, rows in sorted(groups.items()):
    id_matches = by_arxiv.get(key, set())
    doi_matches = set().union(*(by_doi.get(doi(r['doi']), set()) for r in rows if doi(r['doi'])))
    matches = id_matches | doi_matches
    status = 'existing_arxiv_id' if id_matches else ('existing_doi_only' if doi_matches else 'new_identifier')
    counts[status] += 1
    best = max(rows, key=lambda r: len(r['abstract'].strip()))
    rid = 'arxiv:' + key if not matches else ''
    links.append({'arxiv_id': key, 'refresh_hit_count': len(rows), 'status': status,
                  'existing_record_ids': '; '.join(sorted(matches)), 'new_record_id': rid,
                  'query_rank_pairs': '; '.join(f"{r['query_id']}:{r['rank']}" for r in rows),
                  'doi': '; '.join(sorted({r['doi'] for r in rows if r['doi']})), 'title': best['title']})
    if not matches:
        new.append({'record_id': rid, 'title': best['title'], 'authors': best['authors'],
                    'year': best['published'][:4], 'doi': best['doi'], 'arxiv_id': key,
                    'abstract': best['abstract'], 'abstract_status': 'available' if best['abstract'].strip() else 'missing',
                    'source_set': 'arXiv paginated refresh', 'urls': '; '.join(sorted({r['id'] for r in rows})),
                    'hit_count': len(rows), 'abstract_source': 'arXiv paginated refresh',
                    'abstract_source_hit_id': f"{best['query_id']}:{best['rank']}",
                    'published': best['published'], 'updated': best['updated']})

def write(name, data, default_fields):
    with (run / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]) if data else default_fields)
        writer.writeheader()
        writer.writerows(data)

write('new_records.csv', new, ['record_id'])
write('refresh_links.csv', links, ['arxiv_id'])
summary = {'refresh_unique_arxiv_ids': len(groups), 'status_counts': dict(counts),
           'new_records_with_abstract': sum(r['abstract_status'] == 'available' for r in new),
           'note': 'Exact identifier matching only; unpublished/published versions with different identifiers may still duplicate prior records.'}
(run / 'compare_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
