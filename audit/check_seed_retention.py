#!/usr/bin/env python3
"""Check a small purposive set of source-verified manuscript citations, not a recall estimate."""
import csv
from pathlib import Path
P=Path(__file__).resolve().parent; root=P.parent
with (root/'screening/screening_results.csv').open(encoding='utf-8-sig',newline='') as f: decisions={r['record_id']:r for r in csv.DictReader(f)}
seeds=[
 ('SyzAgent','syzagent25','R06009','https://arxiv.org/abs/2503.02301','LLM-guided directed Linux kernel fuzzing; candidate direct security testing.'),
 ('CrashFixer/kAgent','mathai2025crashfixer','R06015','https://arxiv.org/abs/2504.20412','Kernel crash repair; direct security outcome remains to be assessed.'),
 ('KEN/Kgent preprint','zheng2023ken','R06061','https://arxiv.org/abs/2312.05531','Preprint of the same study as R00612; eBPF code generation correctness rather than established security evaluation.'),
 ('KEN/Kgent publication','zheng2024kgent','R00612','https://escholarship.org/uc/item/3jg1f0jr','Same study as R06061; title-only snapshot. Evaluate the pair as one study, not two.'),
 ('MigGPT','dang2025miggpt','R06116','https://proceedings.neurips.cc/paper_files/paper/2025/file/3760dbb5835bf0b771c3f83cb27ef2c0-Paper-Conference.pdf','False-negative risk: title/abstract emphasizes general kernel migration, while published paper section 6.1 also assesses a CVE patch-backporting benchmark. The raw model excluded it; the latest conservative guard restores it to UNCLEAR for further study-level eligibility review.'),
 ('Selene','zhang2024selene','','https://aclanthology.org/2024.acl-long.98/','No exact/manually verified match in frozen search snapshot; cited work appears as L040 in legacy candidate inventory.'),
 ('SimpleBPF','gao2025offloading','','https://ratul.org/papers/ebpf2025-simplebpf.pdf','No exact/manually verified match in frozen search snapshot or old 225 candidates; manuscript citation is an independent provenance route.'),
 ('PathSentinel','lee2024static','','https://arxiv.org/abs/2407.11279','No exact/manually verified match in frozen search snapshot; appears as L012 in legacy candidate inventory. LLM generates validation activity after static analysis.')
]
out=[]
for study,key,rid,url,comment in seeds:
    d=decisions.get(rid,{}) if rid else {}
    out.append({'study':study,'bibtex_key':key,'search_record_id':rid,'in_snapshot':'yes' if d else 'no matching record identified',
                'raw_model_decision':d.get('raw_model_decision','not applicable'), 'effective_decision':d.get('decision','not applicable'),
                'model_reason':d.get('reason',''),'evidence_url':url,'assessment':comment,
                'status':'purposive known-work check; not a representative sensitivity estimate'})
with (P/'known_study_retention.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
print('seed rows',len(out),'retrieved rows',sum(x['in_snapshot']=='yes' for x in out))
