#!/usr/bin/env python3
"""Repeat prior Crossref discovery at 100 results/query in a new run directory."""
import csv
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
QUERIES = BASE.parent / 'google_scholar_queries.csv'
FIELDS = ['query_id', 'theme', 'query', 'effective_query', 'source', 'rank',
          'title', 'authors', 'year', 'venue', 'doi', 'url', 'type',
          'citation_count', 'abstract']
META = ['query_id', 'query', 'effective_query', 'url', 'timestamp_utc',
        'status', 'total_results', 'returned', 'limit', 'truncated', 'error']


def clean_query(query):
    query = query.replace('"', ' ').replace('(', ' ').replace(')', ' ')
    query = re.sub(r'\b(AND|OR|NOT)\b', ' ', query, flags=re.I)
    return re.sub(r'\s+', ' ', query).strip()


def main():
    out = BASE / ('crossref_top100_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir(exist_ok=False)
    rawdir = out / 'raw'
    rawdir.mkdir()
    with QUERIES.open(encoding='utf-8-sig', newline='') as f:
        queries = list(csv.DictReader(f))
    with (out / 'results.csv').open('w', encoding='utf-8-sig', newline='') as results, (out / 'search_log.csv').open('w', encoding='utf-8-sig', newline='') as log:
        writer, logger = csv.DictWriter(results, fieldnames=FIELDS), csv.DictWriter(log, fieldnames=META)
        writer.writeheader()
        logger.writeheader()
        for item in queries:
            q = clean_query(item['query'])
            params = {'query.bibliographic': q, 'rows': 100, 'filter': 'from-pub-date:2022-01-01',
                      'select': 'title,author,issued,container-title,DOI,URL,abstract,type,publisher,is-referenced-by-count'}
            url = 'https://api.crossref.org/works?' + urllib.parse.urlencode(params)
            record = {'query_id': item['id'], 'query': item['query'], 'effective_query': q, 'url': url,
                      'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'limit': 100}
            for attempt in range(3):
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'LLM4OSSec-literature-review/1.0'})
                    with urllib.request.urlopen(req, timeout=45) as response:
                        body = response.read()
                    message = json.loads(body)['message']
                    (rawdir / f"q{int(item['id']):03d}.json").write_bytes(body)
                    items = message.get('items', [])
                    for rank, it in enumerate(items, 1):
                        issued = it.get('issued', {}).get('date-parts', [[]])
                        year = issued[0][0] if issued and issued[0] else ''
                        authors = [' '.join(filter(None, [a.get('given'), a.get('family')])) for a in it.get('author', [])]
                        writer.writerow({'query_id': item['id'], 'theme': item['theme'], 'query': item['query'],
                            'effective_query': q, 'source': 'Crossref', 'rank': rank,
                            'title': (it.get('title') or [''])[0], 'authors': '; '.join(authors),
                            'year': year, 'venue': (it.get('container-title') or [''])[0],
                            'doi': it.get('DOI', ''), 'url': it.get('URL', ''), 'type': it.get('type', ''),
                            'citation_count': it.get('is-referenced-by-count', ''),
                            'abstract': html.unescape(re.sub(r'<[^>]+>', ' ', it.get('abstract', ''))).strip()})
                    total = message.get('total-results', 0)
                    record.update(status='ok', total_results=total, returned=len(items), truncated=total > len(items))
                    break
                except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                    record.update(status='error', error=str(exc))
                    if attempt < 2:
                        time.sleep(5 * (attempt + 1))
            logger.writerow(record)
            results.flush()
            log.flush()
            print(item['id'], record['status'], record.get('returned', ''), flush=True)
            time.sleep(1.3)
    (out / 'README.md').write_text(
        '# Crossref 扩展检索\n\n'
        '- 每条检索返回最多 100 条，结果按 Crossref 默认相关性排序，未分页。\n'
        '- 使用此前 100 条查询及相同的去引号/布尔词转换，以 query.bibliographic 搜索；不等价于 Google Scholar 原表达式。\n'
        '- 过滤 from-pub-date:2022-01-01；未设结束日期，与此前 Crossref 查询口径一致。\n'
        '- results.csv 保留各查询全部返回结果，不去重；search_log.csv 记录实际表达式、URL、状态、总数、截断和时间。\n'
        '- raw/ 是每条成功请求的原始 JSON；数据库变化可能导致与此前前 20 条的排序不一致。\n'
        '- 结果为未筛选候选，不能作为已纳入论文或完整系统检索。\n', encoding='utf-8')
    print('OUTPUT', out, flush=True)


if __name__ == '__main__':
    main()
