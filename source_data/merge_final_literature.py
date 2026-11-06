#!/usr/bin/env python3
"""Conservative, auditable merge of existing R3/R2 and quick-screened Crossref."""
import html
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import unquote
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'relatedfiles/old/LLM4OSSec_文献整理表.xlsx'
NEW = ROOT / 'relatedfiles/new/Crossref快速筛选_200篇.xlsx'
OUT = ROOT / 'final_result/LLM4OSSec_相关文献合并.xlsx'

# Manually screened based on title and, where present, abstract; not full text.
DIRECT = {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 17}
ADJACENT = {10, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 27, 28, 29,
            31, 41, 42, 45, 48, 49, 50, 52, 54, 64, 66, 67, 69, 70, 71, 73,
            75, 76, 79, 81, 82, 87, 90, 91, 95, 96, 97, 98, 106, 107, 110,
            111, 115, 116, 127, 128, 131, 133, 136, 137, 138, 142, 147, 148,
            151, 154, 155, 156, 157, 160, 161, 162, 164, 165, 166, 169, 170,
            171, 173, 175, 176, 177, 179, 181, 184, 186, 187, 188, 189, 190,
            191, 193, 195, 198}


def norm(s):
    s = html.unescape(str(s or '')).casefold()
    s = unicodedata.normalize('NFKD', s)
    return re.sub(r'[^a-z0-9]+', '', ''.join(x for x in s if not unicodedata.combining(x)))


def doi(s):
    m = re.search(r'10\.\d{4,9}/[^\s"<>?#]+', unquote(str(s or '')), re.I)
    return m.group(0).lower().rstrip('.,;)') if m else ''


def safe(x):
    if x is None:
        return ''
    if isinstance(x, (int, float)):
        return x
    x = str(x)
    return ("'" + x if x.lstrip().startswith(('=', '+', '-', '@')) else x)[:32767]


def make_sheet(wb, name, header, rows):
    s = wb.create_sheet(name)
    s.append(header)
    for row in rows:
        s.append([safe(x) for x in row])
    s.freeze_panes = 'A2'
    s.auto_filter.ref = s.dimensions
    for cell in s[1]:
        cell.fill = PatternFill('solid', fgColor='315A7D')
        cell.font = Font(bold=True, color='FFFFFF')
    for i, heading in enumerate(header, 1):
        s.column_dimensions[get_column_letter(i)].width = min(55, max(16, len(heading) * 2 + 8))


def main():
    oldwb = load_workbook(OLD, read_only=True, data_only=True)
    oldrows = list(oldwb['总表'].values)[1:]
    newwb = load_workbook(NEW, read_only=True, data_only=True)
    newrows = list(newwb['快速候选200'].values)[1:]
    old_titles, old_dois = defaultdict(list), defaultdict(list)
    for row in oldrows:
        if norm(row[1]):
            old_titles[norm(row[1])].append(row)
        for value in row[13:15]:
            if doi(value):
                old_dois[doi(value)].append(row)
    merged, by_old, audit, review = [], {}, [], []
    for row in oldrows:
        number, title, year, venue, component, task, rel, _, status, _, source, evidence, memo, url, full, abstract = row
        if rel not in (2, 3) or number in (31, 223):
            continue
        entry = {'id': f'L{int(number):03d}', 'level': '直接候选(R3)' if rel == 3 else '相邻候选(R2)',
                 'title': title, 'authors': '', 'year': year, 'venue': venue, 'doi': doi(url) or doi(full),
                 'url': url, 'full': full, 'component': component, 'task': task, 'old': str(number),
                 'new': '', 'query': '', 'evidence': status, 'reason': memo, 'abstract': abstract,
                 'warning': '旧分类待复核' + ('；旧行223同一研究' if number == 222 else '；旧行31同一研究' if number == 45 else '')}
        merged.append(entry)
        by_old[int(number)] = entry
    new_index = defaultdict(list)
    for row in newrows:
        rank, score, hits, has_abs, _, cid, title, authors, year, venue, newdoi, url, typ, citations, abstract, hits_count, query, conflict, status = row
        rank = int(rank)
        old_matches = {int(r[0]): r for r in (old_dois.get(doi(newdoi), []) + old_titles.get(norm(title), []))}
        old_ids = sorted(old_matches)
        selected = rank in DIRECT or rank in ADJACENT
        if old_ids:
            targetids = sorted({45 if i == 31 else 222 if i == 223 else i for i in old_ids})
            targets = [by_old[i] for i in targetids if i in by_old]
            if targets:
                for entry in targets:
                    entry['new'] = ';'.join(filter(None, [entry['new'], str(cid)]))
                    entry['query'] = '; '.join(filter(None, [entry['query'], str(query or '')]))
                    if not entry['doi']:
                        entry['doi'] = doi(newdoi)
                    if not entry['authors']:
                        entry['authors'] = authors
                    if not entry['abstract']:
                        entry['abstract'] = abstract
                decision = '匹配旧R3/R2，已合并来源'
            else:
                decision = '匹配旧R0/R1，未加入；如需可重新判断'
            audit.append([rank, cid, title, decision, ','.join(map(str, old_ids)), newdoi])
            continue
        if not selected:
            audit.append([rank, cid, title, '未选入：偏离主题或仅标题摘要不足以确认', '', newdoi])
            continue
        tnorm = norm(title)
        near = []
        if len(tnorm) >= 20:
            for old in oldrows:
                other = norm(old[1])
                if len(other) >= 20 and abs(len(other)-len(tnorm)) <= max(len(other),len(tnorm))*.15:
                    ratio = SequenceMatcher(None, tnorm, other).ratio()
                    if ratio >= .88:
                        near.append((ratio, old))
        near.sort(key=lambda x: -x[0])
        warning = '标题/摘要快速判断，未逐篇全文核验'
        if near:
            warning += '；疑似旧表版本/重复，见待核对'
            for ratio, other in near[:3]:
                review.append([cid, title, f'旧表 {other[0]}', other[1], round(ratio, 3), '仅标题相近，未自动合并'])
        entry = {'id': str(cid), 'level': '直接候选(新)' if rank in DIRECT else '相邻候选(新)',
                 'title': title, 'authors': authors, 'year': year, 'venue': venue, 'doi': doi(newdoi),
                 'url': url, 'full': '', 'component': '', 'task': '', 'old': '', 'new': str(cid),
                 'query': query, 'evidence': '仅标题/摘要' if abstract else '仅标题',
                 'reason': '快速人工初筛；需确认系统对象、LLM作用与安全任务', 'abstract': abstract, 'warning': warning}
        merged.append(entry)
        if tnorm and tnorm in new_index:
            for prev in new_index[tnorm]:
                review.append([cid, title, prev['id'], prev['title'], 1, '不同DOI相同标题，未自动合并'])
        new_index[tnorm].append(entry)
        audit.append([rank, cid, title, '已作为新候选纳入', '', newdoi])
    header = ['ID', '相关层级', '标题', '作者', '年份', '期刊会议', 'DOI', '文章链接', '全文链接', 'OS组件', '任务', '旧表行号', '新候选ID', '检索式ID', '证据状态', '判断说明或旧Memo', '摘要', '待核验说明']
    keys = ['id','level','title','authors','year','venue','doi','url','full','component','task','old','new','query','evidence','reason','abstract','warning']
    wb = Workbook()
    wb.remove(wb.active)
    make_sheet(wb, '合并候选', header, [[e[k] for k in keys] for e in merged])
    make_sheet(wb, '新200条筛选记录', ['排序', '候选ID', '标题', '处理决定', '匹配旧表行', 'DOI'], audit)
    make_sheet(wb, '疑似重复待核对', ['新候选ID', '新候选标题', '疑似对应', '对应标题', '相似度', '说明'], review)
    counts = defaultdict(int)
    for e in merged:
        counts[e['level']] += 1
    make_sheet(wb, '说明统计', ['项目', '说明或数量'], [
        ['总候选', len(merged)], *sorted(counts.items()), ['新200条中人工挑选', len(DIRECT | ADJACENT)],
        ['说明', '旧表保留R3和R2，按已记录关系合并31→45和223→222；旧R1/R0未系统纳入。'],
        ['新文献筛选', '快速按标题/摘要筛选；直接候选与相邻候选均待全文复核，不代表最终纳入或已核实。'],
        ['匹配与去重', '与旧表按DOI（仅链接中提取）或规范化标题精确匹配合并；近似项不自动合并。不同DOI预印本/正式版仍可能重复。'],
        ['原数据', str(OLD)], ['新数据', str(NEW)],
        ['限制', '原Crossref按检索式前20条，无法视为完整检索；新文献未逐篇核实真实性、出版信息或结论。'],
    ])
    OUT.parent.mkdir(exist_ok=True)
    if OUT.exists():
        raise FileExistsError(OUT)
    wb.save(OUT)
    print('total', len(merged), 'levels', dict(counts), 'audit', len(audit), 'review', len(review))
    print('decisions', dict(__import__('collections').Counter(x[3] for x in audit)))
    print('output', OUT)


if __name__ == '__main__':
    main()
