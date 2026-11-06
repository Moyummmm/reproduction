#!/usr/bin/env python3
"""Manually seeded, provisional citation-scope triage; not an eligibility determination."""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
os_target = set('syzagent25 mathai2025crashfixer zhang2024selene dang2025miggpt gao2025offloading zheng2023ken'.split())
adjacent = set('Wang2025SparSamp amusuo2025unit chaudhuri25 chen2025gpass chu2025spada egersdoerfer2025stellar gim2024confidential guan2024logllm guitton2024honest lin2024fvel miranda2025veribench mondal2025llm nong2025appatch park2025principles schwarz2025countermind tan2025pipellm tao2026knowledge tu2025agentic wang2025absint wang25boofuzz wen2024automatically wu2022autoformalization xue2025pagent xuerecord yang2023leandojo yang2024whitefox yang2025hybrid yang2025rust zheng25 zhou2025qimeng wang2025qlcoder'.split())
background = set('Alves2004TrustZoneI Cloosters2020TeeRexDA anderson1972computer arnold2009ksplice baezner2017stuxnet ball2006thorough barham2003xen bessey2010few boehme16 brown20 bulekov2024hyperpill cadar2008klee chen2011linux chen2020koobe chen2021evaluating chipounov2011s2e corbato1965introduction corina2017difuze costan2017secure guo2009linux hoffmann22 kafl17 kaplan2020scaling kerrisk2010linux klein2009sel4 lampson1974protection li2019research li22alphacode loscocco01selinux lu2019detecting luAAL14 lyu2025ebpf machiry2017dr mu2025silent optee ouyang22 popek1974formal redini2017bootstomp renzelmann2012symdrive saltzer1975protection schumilo2021nyx serebryany2012addresssanitizer shoshitaishvili2015firmalice spencer99flask swift2003improving szekeres13 vaswani17 wen2025teedfuzzer wu2025flow xu2015collision zhang2019pex zhao2019breaking'.split())
background.update(('page2021prisma', 'rethlefsen2021prismas'))
assert not (os_target & adjacent or os_target & background or adjacent & background)
with (HERE/'citation_candidate_mapping.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
out=[]
for r in rows:
    if r['candidate_matches']: continue
    k=r['bibtex_key']
    if k in os_target:
        group='OS-target LLM: priority primary-source eligibility review'
        reason='Manuscript describes an LLM method with OS kernel/eBPF target; verify security outcome and exact work/version.'
    elif k in adjacent:
        group='Adjacent or transferable: verify cited role'
        reason='Manuscript discusses generic or adjacent method, or protecting LLMs; determine whether a direct OS-security result is actually evaluated.'
    elif k in background:
        group='Foundational/background: not presumed eligible'
        reason='Cited as context, prior non-LLM method, or general foundation; not automatically a core candidate.'
    else:
        group='Unresolved: manually inspect context and source'
        reason='Insufficient basis for grouping from the audit.'
    out.append(dict(r,provisional_group=group,triage_reason=reason,verification_status='pending primary-source confirmation; not an inclusion or exclusion decision'))
with (HERE/'unmatched_citation_scope_triage.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
from collections import Counter
print(Counter(r['provisional_group'] for r in out))
