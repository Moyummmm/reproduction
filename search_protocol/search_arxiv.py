#!/usr/bin/env python3
"""Reproducible arXiv discovery; does not screen or overwrite prior data."""
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / ('arxiv_rerun_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
NS = {'a': 'http://www.w3.org/2005/Atom', 'o': 'http://a9.com/-/spec/opensearch/1.1/', 'ar': 'http://arxiv.org/schemas/atom'}
LLM = '(all:"large language model" OR all:LLM OR all:GPT)'
TOPICS = [
    ('kernel_fuzzing', '(all:kernel AND (all:fuzzing OR all:fuzzer))'),
    ('kernel_vulnerability', '(all:kernel AND (all:vulnerability OR all:security))'),
    ('kernel_patch', '(all:kernel AND (all:patch OR all:backporting))'),
    ('driver_security', '(all:"device driver" AND (all:security OR all:fuzzing OR all:vulnerability))'),
    ('filesystem_security', '(all:"file system" AND (all:security OR all:fuzzing OR all:vulnerability))'),
    ('operating_system_security', '(all:"operating system" AND (all:security OR all:vulnerability))'),
    ('ebpf_security', '(all:eBPF AND (all:security OR all:fuzzing OR all:verification))'),
    ('protocol_fuzzing', '(all:protocol AND (all:fuzzing OR all:fuzzer))'),
    ('memory_safety', '(all:"memory safety" AND (all:vulnerability OR all:detection))'),
    ('exploit', '(all:exploit AND (all:kernel OR all:system))'),
    ('system_logs', '(all:"system log" AND (all:security OR all:anomaly))'),
    ('virtualization', '((all:hypervisor OR all:enclave OR all:TrustZone) AND all:security)'),
]
FIELDS = ['source','query_id','query','rank','source_id','title','authors','published','updated','year','doi','url','pdf_url','abstract','categories']


def text(node, path):
    item = node.find(path, NS)
    return ' '.join(''.join(item.itertext()).split()) if item is not None else ''


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    rawdir = OUT / 'arxiv_raw'
    rawdir.mkdir(exist_ok=True)
    records, logs = [], []
    for index, (name, topic) in enumerate(TOPICS, 1):
        query = LLM + ' AND ' + topic
        params = {'search_query': query, 'start': 0, 'max_results': 100, 'sortBy': 'relevance', 'sortOrder': 'descending'}
        url = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode(params)
        log = {'query_id': name, 'query': query, 'url': url, 'started_utc': datetime.now(timezone.utc).isoformat(), 'limit': 100}
        for attempt in range(3):
            try:
                request = urllib.request.Request(url, headers={'User-Agent': 'LLM4OSSec-literature-review/1.0'})
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = response.read()
                root = ET.fromstring(body)
                (rawdir / (name + '.xml')).write_bytes(body)
                entries = root.findall('a:entry', NS)
                log.update(status='ok', total_results=text(root, 'o:totalResults'), returned=len(entries))
                for rank, entry in enumerate(entries, 1):
                    published = text(entry, 'a:published')
                    records.append({'source': 'arXiv', 'query_id': name, 'query': query, 'rank': rank,
                        'source_id': text(entry, 'a:id'), 'title': text(entry, 'a:title'),
                        'authors': '; '.join(text(a, 'a:name') for a in entry.findall('a:author', NS)),
                        'published': published, 'updated': text(entry, 'a:updated'), 'year': published[:4],
                        'doi': text(entry, 'ar:doi'), 'url': text(entry, 'a:id'),
                        'pdf_url': next((x.get('href', '') for x in entry.findall('a:link', NS) if x.get('title') == 'pdf'), ''),
                        'abstract': text(entry, 'a:summary'),
                        'categories': '; '.join(x.get('term', '') for x in entry.findall('a:category', NS))})
                break
            except (urllib.error.URLError, TimeoutError, ET.ParseError) as exc:
                log.update(status='error', error=str(exc))
                if attempt < 2:
                    time.sleep(10 * (attempt + 1))
        logs.append(log)
        print(index, name, log['status'], log.get('returned', ''), flush=True)
        time.sleep(3.5)
    with (OUT / 'arxiv_results.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    (OUT / 'arxiv_search_log.json').write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
