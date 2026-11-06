#!/usr/bin/env python3
"""Resume exploit refresh at offset 1000 with recorded 429 retries in a new folder."""
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
NS = {'a': 'http://www.w3.org/2005/Atom', 'o': 'http://a9.com/-/spec/opensearch/1.1/', 'ar': 'http://arxiv.org/schemas/atom'}

def text(e, path):
    x = e.find(path, NS)
    return ' '.join(''.join(x.itertext()).split()) if x is not None else ''

def main():
    log = json.loads((HERE.parent/'search_protocol/arxiv_search_log.json').read_text())
    q = next(x for x in log if x['query_id'] == 'exploit')
    out = HERE / ('tail_' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir(exist_ok=False)
    pages, rows = [], []
    start = 1000
    complete = False
    while True:
        params = {'search_query': q['query'], 'start': start, 'max_results': 100,
                  'sortBy': 'relevance', 'sortOrder': 'descending'}
        url = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode(params)
        page = None
        for attempt in range(4):
            page = {'query_id': 'exploit', 'start': start, 'attempt': attempt + 1, 'url': url,
                    'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'status': 'error', 'error': ''}
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'LLM4OSSec-literature-review/1.0'})
                with urllib.request.urlopen(req, timeout=45) as response:
                    body = response.read()
                name = f'exploit_{start:05d}.xml'
                (out/name).write_bytes(body)
                root = ET.fromstring(body)
                entries = root.findall('a:entry', NS)
                total = int(text(root, 'o:totalResults'))
                page.update(status='ok', returned=len(entries), total_results=total, raw_file=name)
                for i, e in enumerate(entries):
                    rows.append({'query_id': 'exploit', 'rank': start+i+1, 'id': text(e,'a:id'),
                                 'title': text(e,'a:title'), 'authors': '; '.join(text(a,'a:name') for a in e.findall('a:author',NS)),
                                 'published': text(e,'a:published'), 'updated': text(e,'a:updated'),
                                 'doi': text(e,'ar:doi'), 'abstract': text(e,'a:summary')})
            except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError) as e:
                page['error'] = str(e)
            pages.append(page)
            (out/'pages.json').write_text(json.dumps(pages, indent=2), encoding='utf-8')
            print('offset', start, 'attempt', attempt+1, page['status'], page.get('returned',''), page['error'], flush=True)
            if page['status'] == 'ok':
                break
            if attempt < 3:
                time.sleep([15,30,60][attempt])
        if page['status'] != 'ok':
            break
        count = page['returned']
        start += count
        if start >= page['total_results']:
            complete = True
            break
        if count == 0:
            break
        time.sleep(5)
    fields = ['query_id','rank','id','title','authors','published','updated','doi','abstract']
    with (out/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w = csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    (out/'summary.json').write_text(json.dumps({'offset_started':1000,'next_offset':start,
        'last_reported_total':page.get('total_results'), 'reached_last_reported_total':complete,
        'returned_rows':len(rows), 'note':'Ranking may shift between requests and between the initial refresh and this resumed fetch.'},indent=2),encoding='utf-8')
    print('OUTPUT',out,flush=True)

if __name__ == '__main__':
    main()
