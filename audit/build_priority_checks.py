#!/usr/bin/env python3
"""Produce source-backed proposed corrections without changing the frozen input."""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
with (HERE.parent/'supplementary_candidate_inventory.csv').open(encoding='utf-8-sig',newline='') as f:
    candidates={x['candidate_id']:x for x in csv.DictReader(f)}
checks=[
 ('L038','dang2025miggpt','arXiv:2504.09474; NeurIPS 2025','existing memo vs summary contradiction','Published NeurIPS paper section 6.1 reports a 350-instance CVE patch-backporting benchmark, in addition to general out-of-tree kernel migration; Table 5 reports semantic match. Reassess relevance and check exact benchmark scope; retain version-specific results.','https://proceedings.neurips.cc/paper_files/paper/2025/file/3760dbb5835bf0b771c3f83cb27ef2c0-Paper-Conference.pdf'),
 ('L041','zheng2023ken;zheng2024kgent','arXiv:2312.05531; DOI:10.1145/3672197.3673434','confirmed same study as C0130','KEN is the earlier arXiv version of Kgent, identified by the authors repository. L041 and C0130 should share one study ID. Evaluate generated eBPF correctness separately from security outcomes.','https://github.com/eunomia-bpf/KEN'),
 ('C0130','zheng2023ken;zheng2024kgent','arXiv:2312.05531; DOI:10.1145/3672197.3673434','confirmed same study as L041','Published Kgent version of KEN; preserve both record IDs but assign a single study ID. The primary evaluation concerns eBPF generation and correctness.','https://escholarship.org/uc/item/3jg1f0jr'),
 ('L035','mathai2025crashfixer','arXiv:2504.20412','confirmed title/version alias','CrashFixer and kAgent share arXiv ID 2504.20412; the current version studies execution-guided kernel crash resolution. The security significance of individual crashes requires separate checking.','https://arxiv.org/abs/2504.20412'),
 ('L040','zhang2024selene','arXiv:2401.07663; DOI:10.18653/v1/2024.acl-long.98','confirmed title alias','L040 names the same published ACL Selene study with a descriptive title. The study benchmarks LLM proof generation using seL4; distinguish functional correctness from independently demonstrated security properties.','https://aclanthology.org/2024.acl-long.98/'),
 ('L012','lee2024static','arXiv:2407.11279','confirmed same title and LLM role','PathSentinel uses static program and access-control analysis to detect Android filesystem vulnerabilities; it uses an LLM downstream to generate exploit/test activities from payloads. Do not attribute all 51 detections to the LLM; assess whether the Android apps and policy target meets the explicit OS scope.','https://arxiv.org/abs/2407.11279'),
 ('','syzagent25','arXiv:2503.02301; DOI:10.1007/978-3-031-90900-9_2','absent from 225; search snapshot R06009','SyzAgent is already cited in the manuscript and is present as R06009 in the later arXiv search snapshot. Add both provenance links; decide eligibility using security-testing criteria.','https://link.springer.com/chapter/10.1007/978-3-031-90900-9_2'),
 ('','gao2025offloading','DOI:10.1145/3748355.3748369','absent from 225; not located in later snapshot by exact title or identifier','SimpleBPF generates and optimizes eBPF programs using LLMs; its reported evaluation focuses on validity, equivalence and performance. Retain citation-led origin unless a retrieval hit is documented.','https://ratul.org/papers/ebpf2025-simplebpf.pdf'),
]
rows=[]
for candidate_id,key,ident,status,proposal,url in checks:
    c=candidates.get(candidate_id,{})
    rows.append({'candidate_id':candidate_id,'bibtex_key':key,'verified_identifiers':ident,'status':status,
                 'old_title':c.get('标题',''),'old_score':c.get('相关度评分（0–3）',''),
                 'old_abstract_summary':c.get('摘要概述',''),'old_conclusion_summary':c.get('结论概述（可访问时）',''),
                 'old_score_rationale':c.get('评分依据',''),'proposed_correction_or_check':proposal,'primary_evidence_url':url,
                 'decision_status':'proposed; eligibility decision pending','check_date':'2026-11-05'})
with (HERE/'verified_priority_checks.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
print('source-backed checks:',len(rows))
