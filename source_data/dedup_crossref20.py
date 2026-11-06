#!/usr/bin/env python3
"""Conservative DOI deduplication of the original Crossref top-20 export."""
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import unquote

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parent / 'search_results' / 'all_results.csv'
OUTPUT = BASE / 'Crossref原始20条_去重结果.xlsx'


def title_key(text):
    text = unicodedata.normalize('NFKD', text or '').casefold()
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()


def doi_key(text):
    text = unquote((text or '').strip()).lower()
    text = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', text)
    return text.rstrip(' .,;')


def safe(value):
    value = str(value or '')
    if value.lstrip().startswith(('=', '+', '-', '@')):
        value = "'" + value
    return value[:32767]


def sheet(wb, name, header, rows):
    ws = wb.create_sheet(name)
    ws.append(header)
    for row in rows:
        ws.append([safe(x) for x in row])
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='315A7D')
    for i, col in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = min(58, max(14, len(col) * 2 + 8))


def main():
    with SOURCE.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    groups = {}
    for index, row in enumerate(rows, 1):
        doi = doi_key(row['doi'])
        # Missing DOI is not automatically merged, even if a title matches.
        key = ('doi', doi) if doi else ('row', str(index))
        groups.setdefault(key, []).append((index, row))

    candidates, occurrences, review = [], [], []
    indexed = []
    for number, (key, group) in enumerate(groups.items(), 1):
        gid = f'C{number:04d}'
        best = max(group, key=lambda pair: (bool(pair[1]['title']), bool(pair[1]['abstract']), bool(pair[1]['authors']))) [1]
        titles = {title_key(row['title']) for _, row in group if row['title']}
        conflict = len(titles) > 1
        queryids = sorted({int(row['query_id']) for _, row in group})
        candidates.append([gid, best['title'], best['authors'], best['year'], best['venue'], best['doi'], best['url'],
                           best['type'], best['citation_count'], best['abstract'], len(group),
                           ', '.join(map(str, queryids)), '是' if conflict else '否', '未筛选'])
        indexed.append((gid, best, key))
        if conflict:
            review.append(['同 DOI 不同标题', gid, '', best['doi'], '', ' | '.join(sorted({r['title'] for _, r in group})), '', '人工检查 DOI 与题录'])
        for original, row in group:
            occurrences.append([gid, original] + [row[k] for k in row])

    # Generate candidate pairs via common title tokens, then compare. No fuzzy merges.
    inverted = defaultdict(list)
    seen = set()
    for i, (gid, row, _) in enumerate(indexed):
        norm = title_key(row['title'])
        tokens = {x for x in norm.split() if len(x) >= 4}
        counts = Counter(j for token in tokens for j in inverted[token])
        for j, common in counts.items():
            other_gid, other, _ = indexed[j]
            other_norm = title_key(other['title'])
            if not norm or not other_norm or (common < 2 and norm != other_norm):
                continue
            if abs(len(norm) - len(other_norm)) > max(len(norm), len(other_norm)) * .15:
                continue
            similarity = SequenceMatcher(None, norm, other_norm).ratio()
            if similarity >= .90:
                pair = (other_gid, gid)
                if pair not in seen:
                    seen.add(pair)
                    review.append(['标题完全一致' if norm == other_norm else f'标题近似 {similarity:.3f}',
                                   other_gid, gid, other['doi'], row['doi'], other['title'], row['title'],
                                   '未自动合并；检查作者、版本及 DOI'])
        for token in tokens:
            inverted[token].append(i)

    wb = Workbook()
    wb.remove(wb.active)
    sheet(wb, '去重候选', ['ID', '标题', '作者', '年份', '来源期刊会议', 'DOI', 'URL', '类型', '引用数', '摘要', '命中数', '检索式ID', '同DOI标题冲突', '筛选状态'], candidates)
    sheet(wb, '原始命中', ['候选ID', '原始行号'] + list(rows[0]), occurrences)
    sheet(wb, '疑似重复待核对', ['原因', '候选ID 1', '候选ID 2', 'DOI 1', 'DOI 2', '标题 1', '标题 2', '处理'], review)
    sheet(wb, '说明统计', ['项目', '值'], [
        ['数据源', str(SOURCE)], ['原始命中条数', len(rows)], ['DOI 去重后候选数', len(groups)],
        ['疑似重复或冲突数', len(review)], ['规则', '同一规范化 DOI 自动合并；缺 DOI 独立保留'],
        ['注意', '标题相同或近似但 DOI 不同，只列为待核对，不自动合并；候选并不等于已纳入论文。'],
        ['范围', '仅此前 Crossref 每条检索前20条；不包含 arXiv 或新执行的前100条。'],
        ['局限', '模糊匹配只生成相似标题候选，可能有漏检；预印本与正式版尚未判定。'],
    ])
    if OUTPUT.exists():
        raise FileExistsError(f'Refusing to overwrite {OUTPUT}')
    wb.save(OUTPUT)
    print('raw', len(rows), 'groups', len(groups), 'review', len(review), 'output', OUTPUT)


if __name__ == '__main__':
    main()
