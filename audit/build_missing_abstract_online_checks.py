#!/usr/bin/env python3
"""Record source-checked paraphrases; no externally sourced abstract is represented as verbatim."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parent
source=P/'missing_abstract_crosssource.csv'
with source.open(encoding='utf-8-sig',newline='') as f:
    rows=[r for r in csv.DictReader(f) if r['match_status'] in ('missing','ambiguous')]

# Checks performed with Web search/open on 2026-11-05 UTC. The tool did not
# expose exact per-query wall times. All summaries below are our paraphrases.
verified={
 'R00937':('https://lingming.cs.illinois.edu/publications/icse2024a.pdf','author-hosted paper: exact title, authors, and DOI on p. 1','Fuzz4All uses LLM-generated and mutated inputs to fuzz several programming/formal languages; its evaluated systems include compilers and solvers, not an explicit OS component.'),
 'R01029':('https://ieeexplore.ieee.org/abstract/document/11640588/','publisher page: exact title and DOI','TaintUM combines static taint analysis with an LLM filtering stage for privileged UEFI and management-module boundary reports; firmware-to-OS scope requires explicit eligibility adjudication.'),
 'R01067':('https://www.cs.ucr.edu/~zhiyunq/pub/ase25_buglens.pdf','author-hosted paper: exact title and author list; previously saved record also links publisher DOI','BUGLENS uses structured LLM reasoning to refine static-analysis warnings in Linux-kernel code; the authors evaluate precision and previously unreported vulnerabilities.'),
 'R01113':('https://aclanthology.org/2024.findings-emnlp.217/','ACL publisher page: exact DOI, title, and authors','LLMSAN asks LLMs for data-flow paths and checks associated properties to reduce false positives; its reported application includes Android malware rather than OS-component analysis.'),
 'R01365':('https://doi.org/10.1109/MSN69125.2025.00028','IEEE Xplore publisher abstract returned via DOI: exact title and DOI','LLM-RD combines kernel-event-derived features with a frozen language model for ransomware detection and classification; system-scope details require further assessment.'),
 'R01818':('https://link.springer.com/chapter/10.1007/978-3-032-33260-8_16','Springer publisher abstract: exact DOI, title, and authors','The paper evaluates functional risks in LLM-generated Linux PAM password-policy configurations and proposes criteria for assessing configuration correctness.'),
 'R01983':('https://ieeexplore.ieee.org/document/11029741/','IEEE publisher search result: exact DOI and title; candidate L088 has same title and publisher link','The method uses LLMs and staged transformations to derive symbolic security-protocol models from natural-language descriptions; explicit OS-component evaluation is not established by the abstract.'),
 'R03038':('https://digitalcollection.zhaw.ch/bitstreams/fb081907-ad18-481e-98bc-cd496afb355a/download','author-institution repository paper: matching title, authors, and DOI','CubeMig combines Kubernetes container migration with kernel-event monitoring and LLM-assisted post-incident recommendations; distinguish the LLM analysis from the separate detection mechanism.'),
 'R03411':('https://doi.org/10.1109/MSR66628.2025.00099','IEEE Xplore publisher abstract returned via DOI: exact title and DOI','LLMSecConfig combines static analysis, retrieval and LLM prompting to repair Kubernetes security misconfigurations; whether orchestration qualifies as an OS interface depends on the declared scope.'),
 'R03847':('https://link.springer.com/chapter/10.1007/978-3-032-23712-5_29','Springer publisher abstract: exact DOI, title, and authors','The paper evaluates LLM classification of Windows security log events under structured-output controls and compares against a random-forest baseline.'),
 'R04355':('https://www.sigbed.org/emsoft-info/confs/emsoft2024.html','conference program identifies matching title, authors and DOI; previously indexed FIU paper text matched title and authors but original direct link currently returns 502','ECG uses LLMs to produce input specifications and fuzzing payloads for embedded operating systems; the previously indexed paper text reports findings on several OS targets.'),
 'R04537':('https://discovery.ucl.ac.uk/id/eprint/10222953/','author-institution repository: exact DOI, title, and authors','LWDIFF extracts specification knowledge with an LLM and uses it in differential testing of WebAssembly runtimes; distinguish runtime testing from a demonstrated OS-specific target.'),
 'R05193':('https://arxiv.org/abs/2406.14408','author preprint: exact title and author list; publication DOI identity not independently resolved','FVEL translates verification problems into Isabelle and applies LLM-assisted theorem proving, evaluated on general verification benchmarks; security/OS use needs separate confirmation.'),
 'R05220':('https://arxiv.org/abs/2306.15626','author preprint: exact title and author list; publication DOI identity not independently resolved','LeanDojo provides tooling and data for retrieval-augmented theorem proving in Lean; the abstract does not establish an OS-specific security application.'),
}
attempted={
 'R00693':'Exact IEEE DOI searched; publisher page returned a robot/JavaScript verification screen. Third-party listing was found but not used to assert the abstract.',
 'R00885':'Exact title and ACM DOI searched; direct publisher DOI returned HTTP 403. No primary abstract was obtained in this check.',
 'R00933':'Exact DOI searched; no matching accessible primary abstract was obtained in this check.',
 'R00976':'Exact ACM DOI searched; third-party bibliographic listing appeared but no accessible primary abstract was obtained.',
 'R01062':'Exact DOI searched; no matching accessible primary abstract was obtained in this check.',
 'R01144':'Exact DOI searched; IEEE page could not be accessed. A third-party summary was not treated as the primary abstract.',
 'R01412':'Exact DOI searched; no matching accessible primary abstract was obtained in this check.',
 'R01835':'Exact DOI searched; IEEE page could not be accessed. A third-party bibliographic listing did not establish the full abstract.',
 'R03868':'Exact DOI searched; only third-party listings were found in this check.',
 'R03968':'Exact DOI searched; no matching accessible primary abstract was obtained in this check.',
 'R04873':'Exact DOI searched; only a third-party bibliographic listing was found in this check.',
}
assert set(verified)|set(attempted)=={r['record_id'] for r in rows}
blocked_ieee={'R01029','R01365','R01983','R03411'}
out=[]
for r in rows:
    rid=r['record_id']; entry=verified.get(rid)
    if rid=='R04355':
        status='primary_abstract_previously_seen_direct_pdf_currently_unavailable'
        note=('Direct recheck on 2026-11-05: previously indexed FIU paper '
              'https://web.eng.fiu.edu/gaquan/Papers/ESWEEK24Papers/EMSOFT/EMSOFT_45_Zhang '
              'returned 502. Adding .pdf did not yield a verified accessible document. '
              'The conference program identifies the paper and points to an author PDF that also returned 502. '
              'The paraphrase records the earlier indexed text, not newly accessible content.')
    elif rid in blocked_ieee:
        status='primary_abstract_seen_in_index_direct_publisher_blocked'
        note=('Publisher abstract was available through an indexed publisher search result on 2026-11-05; '
              'direct recheck on that date encountered anti-robot/JavaScript gating or HTTP 418. '
              'Access can differ by reader or institution.')
    elif entry:
        status='primary_source_abstract_live_accessible_at_recheck'
        note='Direct source recheck on 2026-11-05 reached the matched paper and abstract.'
    else:
        status='primary_abstract_not_obtained'
        note=attempted[rid]+' Search failure does not prove nonexistence.'
    out.append({'record_id':rid,'target_title':r['target_title'],'target_doi':r['target_doi'],
                'local_crosssource_status':r['match_status'],'local_match_id':r['source_record_id'],
                'online_status':status,
                'primary_source_url':entry[0] if entry else '', 'identity_basis':entry[1] if entry else '',
                'paraphrased_findings_not_original_abstract':entry[2] if entry else '',
                'search_date_utc':'2026-11-05','exact_query_time_utc':'not recorded by web tool',
                'search_method':'exact DOI/title web search and/or opening publisher/author page',
                'notes':note+(' Source check only; eligibility pending. Paraphrase, not a verbatim abstract.' if entry else '')})
with (P/'missing_abstract_online_checks.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
from collections import Counter
print(json.dumps({'records':len(out),'status':dict(Counter(r['online_status'] for r in out))},indent=2))
