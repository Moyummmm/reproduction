#!/usr/bin/env python3
"""Heuristic title/abstract ranking, not a scholarly inclusion decision."""
import re
from pathlib import Path
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parent
SOURCE = BASE / 'Crossref原始20条_去重结果.xlsx'
OUTPUT = BASE / 'Crossref快速筛选_200篇.xlsx'
RULES = {
    'LLM': [(r'\blarge language models?\b', 8, 'large language model'), (r'\bllms?\b', 8, 'LLM'),
            (r'\b(?:chatgpt|gpt-?\d|gpt|codex|llama|deepseek)\b', 7, 'GPT/LLM名称'),
            (r'\blanguage models?\b', 4, 'language model'), (r'\b(?:generative ai|foundation models?)\b', 3, '生成式AI/基础模型')],
    'OS': [(r'\b(?:linux|kernel|operating systems?|os security|system calls?|syscalls?)\b', 8, '操作系统/内核'),
           (r'\b(?:file ?systems?|device drivers?|ebpf|hypervisors?|trustzone|enclaves?)\b', 6, '系统组件'),
           (r'\b(?:android|firmware|embedded systems?|containers?|system logs?|network protocols?)\b', 3, '相关系统')],
    '安全': [(r'\b(?:vulnerabilit\w*|exploit\w*|fuzz(?:ing|er|ers)?|security|cybersecurity)\b', 6, '安全/漏洞/fuzzing'),
             (r'\b(?:memory safety|taint analysis|static analysis|bug detection|bug finding|patch(?:ing|es)?|backport\w*)\b', 4, '分析/补丁'),
             (r'\b(?:attack\w*|defen[cs]e|threat\w*|malware|anomal\w*|verification)\b', 2, '攻击/防御/验证')],
}


def score(title, abstract):
    fields = [(str(title or ''), 1.0), (str(abstract or ''), .55)]
    points, details = 0.0, []
    for category, rules in RULES.items():
        matches = []
        for pattern, weight, label in rules:
            best = max((factor for text, factor in fields if re.search(pattern, text, re.I)), default=0)
            if best:
                matches.append((weight * best, label))
        matches.sort(reverse=True)
        if matches:
            points += matches[0][0] + sum(x[0] * .15 for x in matches[1:])
            details.append(category + ':' + '/'.join(x[1] for x in matches))
    if all(any(x.startswith(category + ':') for x in details) for category in RULES):
        points += 4
    return round(points, 2), '; '.join(details)


def main():
    wb = load_workbook(SOURCE, read_only=True, data_only=True)
    source = list(wb['去重候选'].values)
    header, rows = source[0], source[1:]
    ranked = []
    for row in rows:
        points, reason = score(row[1], row[9])
        ranked.append((points, reason, row))
    ranked.sort(key=lambda x: (-x[0], str(x[2][0])))
    out = Workbook()
    ws = out.active
    ws.title = '快速候选200'
    ws.append(['排序', '关键词分数', '命中依据', '摘要状态', '注意'] + list(header))
    for rank, (points, reason, row) in enumerate(ranked[:200], 1):
        ws.append([rank, points, reason, '有摘要' if row[9] else '无摘要', '机器排序，未逐篇核验'] + list(row))
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.fill = PatternFill('solid', fgColor='315A7D')
        cell.font = Font(bold=True, color='FFFFFF')
    for col in range(1, len(header) + 6):
        ws.column_dimensions[get_column_letter(col)].width = 24 if col not in (3, 7, 15) else 52
    note = out.create_sheet('说明')
    for row in [
        ('目标', '快速选出200条供后续查看，不是最终纳入综述的200篇。'),
        ('来源', 'Crossref原始20条_去重结果.xlsx 的1454条候选，不含新的每条100条结果或arXiv新结果。'),
        ('方法', '标题与摘要分别匹配LLM、系统对象、安全任务关键词，标题权重更高；三类均命中另加分，按分数降序取前200。'),
        ('限制', '仅机械关键词排序，未逐篇阅读，不判断是否真的使用LLM或直接评估OS安全；分数不代表相关性概率。'),
        ('缺摘要', '缺摘要的记录按标题排序，不等于无关；有摘要也不等于已全文阅读。'),
        ('重复', '源表同 DOI 已合并；不同 DOI 的近似标题/版本尚待核验，200条不保证均为独立研究。'),
        ('追溯', '候选ID及检索式ID可在原去重工作簿中追溯到原始命中。'),
    ]:
        note.append(row)
    note.column_dimensions['A'].width = 18
    note.column_dimensions['B'].width = 110
    note.freeze_panes = 'A2'
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    out.save(OUTPUT)
    print('selected', min(200, len(ranked)), 'with_abstract', sum(bool(x[2][9]) for x in ranked[:200]))
    print('range', ranked[0][0], ranked[199][0])
    for points, reason, row in ranked[:10]:
        print(points, row[1])


if __name__ == '__main__':
    main()
