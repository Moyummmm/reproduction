#!/usr/bin/env python3
"""Export auditable record-level inventories from the retained source files."""
import collections
import csv
import html
import itertools
import re
import unicodedata
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
SOURCE = Path(__file__).resolve().parent / 'sources'
CURRENT = SOURCE / 'candidate_source.csv'
LEGACY = SOURCE / 'legacy_original.csv'
REVISED = SOURCE / 'legacy_reclassified_source.csv'

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def export(name, records):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]), extrasaction='raise')
        writer.writeheader()
        writer.writerows(records)

def normalized_title(s):
    s = unicodedata.normalize('NFKC', html.unescape(str(s or ''))).casefold()
    return ''.join(ch for ch in s if ch.isalnum())

with LEGACY.open(encoding='utf-8-sig', newline='') as f:
    legacy = list(csv.DictReader(f))
current = rows(CURRENT)
revised = rows(REVISED)
assert len(legacy) == 485 and len(current) == 225 and len(revised) == 485
assert all(str(r['序号']) == str(i) for i, r in enumerate(revised, 1))
by_old = {int(r['旧表行号']): r for r in current if str(r['旧表行号']).isdigit()}
# These two relations are documented in the source workbook's statistics sheet.
# Row 31's identity is inferred from contextual evidence, so never treat it as certain.
aliases = {31: (45, 'possible same study; row 31 identity inferred'),
           223: (222, 'possible version pair; verify publication history')}

candidate_export = []
for r in current:
    raw = r['旧表行号']
    n = int(raw) if str(raw).isdigit() else None
    x = {'candidate_id': r['ID'], 'legacy_record_id': n or '',
         'legacy_original_score': legacy[n-1]['Relevance'] if n else '',
         'legacy_in_220_scored_records': ('yes' if legacy[n-1]['Relevance'] in ('1','2','3') else 'no') if n else 'not applicable',
         'source_relation': 'retained legacy record' if n else 'new candidate',
         'new_candidate_id': r['新候选ID'] or ''}
    x.update({k: (v if v is not None else '') for k, v in r.items() if k not in ('ID', '旧表行号', '新候选ID')})
    candidate_export.append(x)
export('supplementary_candidate_inventory.csv', candidate_export)

legacy_export = []
crosswalk = []
for i, r in enumerate(legacy, 1):
    target = by_old.get(i)
    match = 'direct source-row link' if target else 'not retained as direct source row'
    if not target and i in aliases:
        target_id, note = aliases[i]
        target = by_old.get(target_id)
        if target:
            match = 'provisional alias: ' + note
    updated = revised[i-1]
    x = {'legacy_record_id': i, 'historical_score': r['Relevance'],
         'latest_candidate_id': target['ID'] if target else '',
         'link_status': match, 'updated_legacy_score': updated['相关性'],
         'updated_legacy_title': updated['论文标题'] or ''}
    x.update(r)
    crosswalk.append(x)
    if r['Relevance'] in ('1','2','3'):
        legacy_export.append(x)
assert len(legacy_export) == 220
export('supplementary_legacy_inventory.csv', legacy_export)
export('legacy_to_candidate_crosswalk.csv', crosswalk)

groups = collections.defaultdict(list)
for r in current:
    title = normalized_title(r['标题'])
    if len(title) >= 12:
        groups[('normalized title', title)].append(r)
    doi = str(r['DOI'] or '').lower().strip().removeprefix('https://doi.org/')
    if doi.startswith('10.'):
        groups[('provided DOI', doi)].append(r)
    for url in (r['文章链接'],):
        m = re.search(r'arxiv\.org/(?:abs|pdf)/((?:\d{4}\.\d{4,5}|[a-z-]+/\d+))(?:v\d+)?', str(url or ''), re.I)
        if m:
            groups[('article-link arXiv ID', m.group(1).lower())].append(r)
pair_reasons = collections.defaultdict(set)
for (kind, key), matches in groups.items():
    for a, b in itertools.combinations(matches, 2):
        if a['ID'] != b['ID']:
            pair_reasons[tuple(sorted((a['ID'], b['ID'])))].add(kind + ': ' + key)
index = {r['ID']: r for r in current}
verified = {
    ('L094', 'L130'): ('same study: matching cited arXiv paper', 'https://arxiv.org/abs/2411.11532'),
    ('L103', 'L116'): ('same study: matching cited arXiv paper', 'https://arxiv.org/abs/2405.17238'),
    ('C0631', 'C0632'): ('same preprint: Research Square v1 and v2', 'https://assets-eu.researchsquare.com/files/rs-4341401/v1_covered_59acb6fd-68d0-425e-8041-666108000204.pdf; https://assets-eu.researchsquare.com/files/rs-4341401/v2_covered_e7de9cc1-af41-4f3d-b1d6-b6279f3c3038.pdf'),
}
pairs = []
for (a, b), reasons in sorted(pair_reasons.items()):
    x, y = index[a], index[b]
    status, evidence = verified.get((a, b), ('unresolved; titles match but DOI relationship needs verification', ''))
    pairs.append({'candidate_id_a': a, 'candidate_id_b': b,
                  'title_a': x['标题'], 'title_b': y['标题'],
                  'doi_a': x['DOI'] or '', 'doi_b': y['DOI'] or '',
                  'reason': '; '.join(sorted(reasons)),
                  'status': status, 'evidence': evidence})
if pairs:
    export('potential_duplicate_pairs.csv', pairs)

print('legacy score distribution:', collections.Counter(r['Relevance'] for r in legacy))
print('current source rows:', len(by_old), 'new:', sum(not str(r['旧表行号']).isdigit() for r in current))
print('legacy links:', collections.Counter(r['link_status'] for r in legacy_export))
print('potential duplicate pairs:', len(pairs))
