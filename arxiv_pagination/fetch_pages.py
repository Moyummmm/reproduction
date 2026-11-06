#!/usr/bin/env python3
"""Fetch full paginated refreshes of two truncated arXiv queries.

Writes a new timestamped folder; the frozen 2026-11-05 snapshot is untouched.
"""
import csv
import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE.parent / 'search_protocol' / 'arxiv_search_log.json'
NS = {'a': 'http://www.w3.org/2005/Atom', 'o': 'http://a9.com/-/spec/opensearch/1.1/', 'ar': 'http://arxiv.org/schemas/atom'}
QUERIES = {'kernel_vulnerability', 'exploit'}
LIMIT = 100

def node_text(element, path):
    node = element.find(path, NS)
    return ' '.join(''.join(node.itertext()).split()) if node is not None else ''

def main():
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = HERE / ('run_' + now)
    out.mkdir(exist_ok=False)
    original = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    queries = [q for q in original if q['query_id'] in QUERIES]
    logs, rows = [], []
    summaries = []
    for q in queries:
        start = 0
        seen_ids = set()
        last_total = None
        complete = False
        while True:
            params = {'search_query': q['query'], 'start': start, 'max_results': LIMIT,
                      'sortBy': 'relevance', 'sortOrder': 'descending'}
            url = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode(params)
            page = {'query_id': q['query_id'], 'start': start, 'max_results': LIMIT,
                    'url': url, 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                    'status': 'error', 'error': '', 'returned': 0, 'total_results': None,
                    'raw_file': ''}
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'LLM4OSSec-literature-review/1.0'})
                with urllib.request.urlopen(req, timeout=45) as response:
                    body = response.read()
                name = f"{q['query_id']}_{start:05d}.xml"
                (out / name).write_bytes(body)
                page['raw_file'] = name
                root = ET.fromstring(body)
                total = int(node_text(root, 'o:totalResults'))
                entries = root.findall('a:entry', NS)
                page.update(status='ok', total_results=total, returned=len(entries))
                last_total = total
                for offset, entry in enumerate(entries):
                    arxiv_url = node_text(entry, 'a:id')
                    seen_ids.add(arxiv_url)
                    rows.append({'query_id': q['query_id'], 'rank': start + offset + 1,
                        'id': arxiv_url, 'title': node_text(entry, 'a:title'),
                        'authors': '; '.join(node_text(x, 'a:name') for x in entry.findall('a:author', NS)),
                        'published': node_text(entry, 'a:published'), 'updated': node_text(entry, 'a:updated'),
                        'doi': node_text(entry, 'ar:doi'), 'abstract': node_text(entry, 'a:summary')})
            except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError) as exc:
                page['error'] = str(exc)
            logs.append(page)
            (out / 'pages.json').write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding='utf-8')
            print(q['query_id'], start, page['status'], page['returned'], page['error'], flush=True)
            if page['status'] != 'ok':
                break
            if page['returned'] == 0:
                complete = start >= last_total
                break
            start += page['returned']
            if start >= last_total:
                complete = True
                break
            time.sleep(3.5)
        summaries.append({'query_id': q['query_id'], 'original_total': q['total_results'],
                          'original_returned': q['returned'], 'refresh_total_last_page': last_total,
                          'refresh_page_coverage_reached_last_reported_total': complete,
                          'refresh_unique_versioned_ids': len(seen_ids),
                          'limitation': 'Relevance ranking and results may shift between pages and between snapshots; reaching the last total does not prove a stable exhaustive set.'})
        time.sleep(3.5)
    fields = ['query_id','rank','id','title','authors','published','updated','doi','abstract']
    with (out / 'results.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    (out / 'summary.json').write_text(json.dumps(summaries, indent=2, ensure_ascii=False), encoding='utf-8')
    print('OUTPUT', out, flush=True)

if __name__ == '__main__':
    main()
