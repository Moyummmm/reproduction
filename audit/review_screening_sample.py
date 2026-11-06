#!/usr/bin/env python3
"""Explicit second-model audit decisions for the frozen stratified sample."""
import csv
from pathlib import Path
P=Path(__file__).resolve().parent
notes={
'R01286':('EXCLUDE','Rust/C kernel-module performance and stability; no LLM is described.'),
'R01674':('EXCLUDE','LLM detects generic code vulnerabilities and malware; no OS-component target is identified.'),
'R01978':('EXCLUDE','Evaluates agent self-reports for Contexto search, not OS security.'),
'R02208':('EXCLUDE','LLM screens clinical-review citations, not OS security.'),
'R02217':('EXCLUDE','Modbus/SCADA security architecture; no LLM is described.'),
'R04047':('EXCLUDE','Road-network resilience, not computing-system security.'),
'R04330':('EXCLUDE','CWE ontology modelling; no LLM or OS-security application described.'),
'R05469':('EXCLUDE','Construction safety training, not cybersecurity or OS components.'),
'R05620':('EXCLUDE','Defends LLM-generated database SQL against prompt injection; no OS target.'),
'R06008':('EXCLUDE','Solidity smart-contract benchmark; no LLM or OS target.'),
'R00235':('UNCLEAR','Concrete-structure design appears off-scope; abstract absent, retain under the conservative missing-abstract rule.'),
'R00437':('UNCLEAR','Writing-feedback title appears off-scope; abstract absent, preserve the explicit override.'),
'R00619':('UNCLEAR','Automobile LLM title does not establish the task; abstract absent.'),
'R01463':('UNCLEAR','Title indicates meta-analysis tools; abstract absent and record type not verified.'),
'R01594':('UNCLEAR','Autonomous-driving fuzzing appears adjacent; abstract absent and target details unknown.'),
'R02237':('UNCLEAR','Service-handler title is nonspecific; LLM and security roles unknown.'),
'R02554':('UNCLEAR','LLM personalization title lacks OS/security context; abstract absent.'),
'R02833':('UNCLEAR','VirtualBox performance title indicates an OS-adjacent target but no LLM; abstract absent.'),
'R03958':('UNCLEAR','Title describes review of a behavioral-science tutorial; abstract unavailable.'),
'R04005':('UNCLEAR','Android taint-analysis title concerns security but does not establish LLM usage; abstract absent.'),
'R03368':('UNCLEAR','Uses a pretrained BERT model for generic system-log anomaly detection; generative LLM scope and OS security targets are not demonstrated.'),
'R04168':('POSSIBLE_CORE','Abstract explicitly reports LLM vulnerability detection on Linux kernel bugs with CVEs; compare duplicate R06033.'),
'R06009':('POSSIBLE_CORE','Abstract describes LLM-guided Syzkaller kernel fuzzing; eligible for further checking.'),
'R06013':('UNCLEAR','Abstract discusses kernel crash repair but does not establish which crashes are security vulnerabilities.'),
'R06021':('POSSIBLE_CORE','Abstract evaluates coding agents on real Linux-kernel vulnerabilities.'),
'R06033':('POSSIBLE_CORE','Abstract reports Linux kernel vulnerability detection with CVEs; likely same study as R04168.'),
'R06088':('POSSIBLE_CORE','Abstract reports LLM-guided warning analysis on Android kernel drivers and a confirmed vulnerability.'),
'R06155':('POSSIBLE_CORE','Abstract explicitly evaluates an LLM agent auditing Windows password-policy compliance.'),
'R06181':('POSSIBLE_CORE','Abstract describes system-provenance intrusion investigation across OSs using an LLM; verify interface and dataset details.'),
'R06183':('UNCLEAR','Abstract mentions heterogeneous telemetry and multiple OSs; it does not explicitly establish OS-component telemetry or privileged-interface target.'),
'R00857':('POSSIBLE_CORE','Title explicitly combines LLM vulnerability detection and Linux kernel; abstract and publication need retrieval.'),
'R01144':('POSSIBLE_CORE','Title explicitly combines LLM, ransomware detection and kernel-level behavior; abstract still needed.'),
'R01782':('POSSIBLE_CORE','Title explicitly describes empirical evaluation of LLMs on Linux security tasks; details remain unverified.'),
'R01786':('UNCLEAR','Linux-based embedded firmware and library functions are named, but OS-component scope is not explicit in title alone.'),
'R01818':('POSSIBLE_CORE','Title explicitly identifies LLM-generated Linux password policy and its evaluation; retrieve abstract.'),
'R01835':('UNCLEAR','Embedded Linux firmware and backdoors are stated but an OS-component or privileged-interface target is not explicit.'),
'R03411':('UNCLEAR','Container misconfigurations and LLM are explicit, but a security-specific repair target is not explicit in title.'),
'R03847':('POSSIBLE_CORE','Title identifies LLM classification of Windows security logs; application and source details still need verification.'),
'R04355':('POSSIBLE_CORE','Title explicitly connects LLM-based corpus generation with embedded OS fuzzing; inspect task and evaluation.'),
'R04873':('UNCLEAR','OS command injection exploit generation can target application input handling; OS-component target not established by title.'),
'R00878':('UNCLEAR','LLM-guided directed fuzzing and bugs are present, but OS target is unspecified.'),
'R01074':('UNCLEAR','Linux configuration and LLM are present; abstract emphasizes performance, not a security-specific evaluation.'),
'R02778':('UNCLEAR','LLM-guided binary fuzzing is clear, but OS-component target is unspecified.'),
'R03335':('UNCLEAR','LLM-assisted cloud security is clear; direct OS-component target is unspecified.'),
'R03973':('UNCLEAR','LLM binary taint analysis includes firmware vulnerabilities, but OS-component target is unspecified.'),
'R04282':('UNCLEAR','LLM-enhanced critical-function identification in binaries lacks an explicit OS-component target.'),
'R04792':('UNCLEAR','CVE exploit generation targets network services; OS-component scope is not established.'),
'R06049':('UNCLEAR','Secure mobile agent OS is described, but the LLM appears protected rather than performing the security task.'),
'R06248':('UNCLEAR','LLM repairs C/C++ vulnerabilities, but OS component or privileged interface is unspecified.'),
'R06307':('UNCLEAR','LLM post-breach attack simulation is described; an OS component target is not established.'),
'R00474':('UNCLEAR','Neither title nor abstract is available.'),
'R00718':('UNCLEAR','LLM vulnerability scoring title lacks a defined OS target; no abstract.'),
'R01607':('UNCLEAR','LLM vulnerability explanation title lacks a defined OS target; no abstract.'),
'R02926':('UNCLEAR','TEE and AI execution appear in title; whether LLM assists security is unknown without abstract.'),
'R03047':('UNCLEAR','Virtualization security is stated, but LLM involvement is unknown without abstract.'),
'R03288':('UNCLEAR','System-log anomaly detection is stated, but LLM and security roles are unknown without abstract.'),
'R04204':('UNCLEAR','Decompilation/RAG title lacks an explicit security task and OS target.'),
'R04268':('UNCLEAR','Binary vulnerability detection is stated, but LLM and OS targets are unknown without abstract.'),
'R04605':('UNCLEAR','LLM-guided hardware security verification is explicit; OS/privileged interface connection is not.'),
'R05785':('UNCLEAR','LLM code security guard is named, but task and OS target are unspecified.'),
}
with (P/'screening_audit_sample.csv').open(encoding='utf-8-sig',newline='') as f: sample=list(csv.DictReader(f))
assert len(sample)==len(notes)==60 and set(notes)=={r['record_id'] for r in sample}, 'sample differs; do not attach these judgments'
out=[]
for r in sample:
    proposed,reason=notes[r['record_id']]
    out.append({'record_id':r['record_id'],'stratum':r['stratum'],'model_raw':r['model_decision'],
                'model_effective':r['effective_decision'],'audit_proposed':proposed,
                'same_as_effective':'yes' if proposed==r['effective_decision'] else 'no',
                'rationale':reason,'basis':'Codex review of supplied title and abstract with prior model decision and reason visible; non-blinded',
                'status':'provisional; not a human screen, independent screening, or final eligibility judgment'})
with (P/'screening_audit_review.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0]); w.writeheader(); w.writerows(out)
from collections import Counter
print('reviewed',len(out),'same-as-effective',Counter(r['same_as_effective'] for r in out))
