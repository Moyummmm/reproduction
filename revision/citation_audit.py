#!/usr/bin/env python3
"""Audit the revised manuscript's citations without changing the frozen prior audit."""
import csv
import html
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
REPRODUCT = AUDIT.parent
workspace = REPRODUCT.parent
ROOT = workspace if (workspace / 'reproduct' == REPRODUCT and (workspace / 'refs.bib').is_file() and (workspace / 'sections').is_dir()) else AUDIT / 'manuscript_snapshot'
sections = ['introduction', 'background', 'methodology', 'llm_os_security', 'representative_comparison', 'future', 'conclusion']

def norm(s):
    s = html.unescape(html.unescape(s or ''))
    s = re.sub(r'\\[a-zA-Z]+\s*', '', s)
    return ''.join(c for c in unicodedata.normalize('NFKD', s).casefold() if c.isalnum())

def doi(s):
    m = re.search(r'10\.\d{4,9}/[^\s{}<>";,]+', s or '', re.I)
    return m.group(0).lower().rstrip('.)') if m else ''

def extract_field(block, field):
    m = re.search(r'(?im)^\s*' + re.escape(field) + r'\s*=\s*([{"])', block)
    if not m:
        return ''
    delim = m.group(1); start = m.end(); i = start
    if delim == '"':
        while i < len(block) and (block[i] != '"' or block[i-1] == '\\'): i += 1
        return block[start:i]
    level = 1
    while i < len(block) and level:
        if block[i] == '{' and block[i-1] != '\\': level += 1
        if block[i] == '}' and block[i-1] != '\\': level -= 1
        i += 1
    return block[start:i-1]

bib = (ROOT / 'refs.bib').read_text(encoding='utf-8')
starts = list(re.finditer(r'(?m)^\s*@\w+\s*\{\s*([^,\s]+)\s*,', bib))
records = {}
for n, m in enumerate(starts):
    block = bib[m.end():starts[n+1].start() if n + 1 < len(starts) else len(bib)]
    records[m.group(1)] = {f: extract_field(block, f) for f in ('title','doi','url','eprint','journal','year')}

used = defaultdict(set)
for section in sections:
    text = (ROOT / 'sections' / (section + '.tex')).read_text(encoding='utf-8')
    text = re.sub(r'\\begin\{comment\}.*?\\end\{comment\}', '', text, flags=re.S)
    text = re.sub(r'(?<!\\)%[^\n]*', '', text)
    for m in re.finditer(r'\\(?:rev)?cite\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}', text):
        for key in m.group(1).split(','):
            if key.strip(): used[key.strip()].add(section)

with (REPRODUCT/'supplementary_candidate_inventory.csv').open(encoding='utf-8-sig', newline='') as f:
    candidates = list(csv.DictReader(f))
bytitle = defaultdict(list); bydoi = defaultdict(list); byarxiv = defaultdict(list)
for c in candidates:
    if norm(c['标题']): bytitle[norm(c['标题'])].append(c)
    for s in (c['DOI'], c['文章链接'], c['全文链接'], c['摘要来源'], c['结论来源']):
        if doi(s): bydoi[doi(s)].append(c)
        for x in re.findall(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?', s or '', re.I): byarxiv[x].append(c)
aliases = {
    'dang2025miggpt': [('L038', 'verified title variant: NeurIPS official paper https://proceedings.neurips.cc/paper_files/paper/2025/file/3760dbb5835bf0b771c3f83cb27ef2c0-Paper-Conference.pdf')],
    'zhang2024selene': [('L040', 'verified title variant: official ACL page https://aclanthology.org/2024.acl-long.98/')],
    'zheng2023ken': [('L041', 'verified preprint/version: authors repository https://github.com/eunomia-bpf/KEN'), ('C0130', 'verified preprint/version: authors repository https://github.com/eunomia-bpf/KEN')],
    'zheng2024kgent': [('L041', 'verified alternate title: published paper https://escholarship.org/uc/item/3jg1f0jr')],
}
out = []
for key in sorted(used):
    b = records.get(key, {}); matches = defaultdict(set)
    for c in bytitle.get(norm(b.get('title','')),[]): matches[c['candidate_id']].add('exact normalized title')
    for d in set(filter(None, (doi(b.get('doi','')), doi(b.get('url',''))))):
        for c in bydoi.get(d,[]): matches[c['candidate_id']].add('DOI')
    ids = set(re.findall(r'\d{4}\.\d{4,5}', b.get('eprint','') + ' ' + b.get('url','') + ' ' + b.get('journal','')))
    for arx in ids:
        for c in byarxiv.get(arx,[]): matches[c['candidate_id']].add('arXiv ID')
    for candidate_id, evidence in aliases.get(key, []): matches[candidate_id].add(evidence)
    out.append({'bibtex_key':key, 'title':b.get('title',''), 'doi':b.get('doi',''), 'year':b.get('year',''), 'sections':'; '.join(sorted(used[key])), 'candidate_matches':'; '.join(f'{i} ({", ".join(sorted(v))})' for i,v in sorted(matches.items())), 'match_status':'candidate match; verify study role' if matches else ('no candidate match found' if b else 'missing BibTeX entry')})
with (AUDIT/'citation_candidate_mapping.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
print('cited keys:',len(out),'candidate match:',sum(bool(r['candidate_matches']) for r in out),'no match found:',sum(r['match_status']=='no candidate match found' for r in out),'missing BibTeX:',sum(r['match_status']=='missing BibTeX entry' for r in out))

searchfile = REPRODUCT/'search_protocol/records.csv'
if searchfile.exists():
    with searchfile.open(encoding='utf-8-sig',newline='') as f: search_rows=list(csv.DictReader(f))
    titles=defaultdict(list); dois=defaultdict(list); arxivs=defaultdict(list)
    for r in search_rows:
        if norm(r['title']): titles[norm(r['title'])].append(r)
        if doi(r['doi']): dois[doi(r['doi'])].append(r)
        if r['arxiv_id']: arxivs[re.sub(r'v\d+$','',r['arxiv_id'])].append(r)
    search_aliases={
        'zheng2023ken':[('R00612','KEN earlier version of Kgent; https://github.com/eunomia-bpf/KEN')],
        'zheng2024kgent':[('R06061','KEN earlier version of Kgent; https://github.com/eunomia-bpf/KEN')],
    }
    linked=[]
    for row in out:
        key=row['bibtex_key']; b=records.get(key,{}); matches=defaultdict(set)
        for r in titles.get(norm(b.get('title','')),[]): matches[r['record_id']].add('exact normalized title')
        for d in set(filter(None,(doi(b.get('doi','')),doi(b.get('url',''))))):
            for r in dois.get(d,[]): matches[r['record_id']].add('DOI')
        for arx in set(re.findall(r'\d{4}\.\d{4,5}', b.get('eprint','')+' '+b.get('url','')+' '+b.get('journal',''))):
            for r in arxivs.get(arx,[]): matches[r['record_id']].add('arXiv ID')
        for record_id,evidence in search_aliases.get(key,[]): matches[record_id].add(evidence)
        linked.append({'bibtex_key':key,'title':row['title'],'search_matches':'; '.join(f'{i} ({", ".join(sorted(v))})' for i,v in sorted(matches.items())),
                       'status':'retrieval-snapshot match; verify eligibility and versions' if matches else 'no exact or manually confirmed snapshot match'})
    with (AUDIT/'citation_search_mapping.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=linked[0].keys());w.writeheader();w.writerows(linked)
    print('search snapshot linked keys:',sum(bool(r['search_matches']) for r in linked),'of',len(linked))
