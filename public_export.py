#!/usr/bin/env python3
"""Create a separate, metadata-only public export; never alter source files."""
import argparse
import csv
import hashlib
import json
import shutil
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
csv.field_size_limit(min(sys.maxsize, 2147483647))

# Explicit column allowlist: free-text evidence, rationales, abstracts, model
# inputs and outputs are not exported. Abstract *availability flags* are kept.
COLUMNS = set('''record_id candidate_id legacy_record_id historical_score latest_candidate_id
link_status updated_legacy_score updated_legacy_title Paper Title Venue/Journal Component
Sub-category Relevance Year ArticleURL FullTextURL legacy_original_score
legacy_in_220_scored_records source_relation new_candidate_id 相关层级 标题 作者 年份
期刊会议 DOI 文章链接 全文链接 OS组件 检索式ID 证据状态 关键词 相关度评分（0–3）
id theme query source query_id effective_query url timestamp timestamp_utc started_utc
total_results returned limit truncated rank source_id title authors published updated year
doi pdf_url categories arxiv_id abstract_status source_set urls hit_count abstract_source
abstract_source_hit_id hit_id candidate_id_a candidate_id_b title_a title_b doi_a doi_b status
refresh_hit_count existing_record_ids new_record_id query_rank_pairs batch_id year_scope
raw_model_decision decision review_status model batch records priority triggers
conservative_decision first_raw first_adjusted second_raw second_adjusted second_evidence_exact
comparison_status os_target llm_role security_task suggested uncertainty evidence_exact
basis raw_suggested conservative_suggested
bibtex_key search_matches candidate_matches match_status manuscript_sections
provisional_context_role later_search_matches eligibility_status sections verification_status
study search_record_id in_snapshot effective_decision evidence_url assessment
stratum model_raw model_effective audit_proposed same_as_effective sample_frame_decision
current_decision audit_differs_current review_status batch matched_doi supplement_status
openalex_work_id openalex_doi openalex_title request_started_utc
google_scholar_url crossref_csv citation_count type
序号 论文标题 发表 venue OS 组件 任务子类 相关性 阅读状态 本轮复核 证据来源'''.split())
# Multiword source column names are individual fields, not whitespace tokens.
COLUMNS.update({'Paper Title','Venue/Journal','Sub-category','OS 组件','任务子类','发表 venue',
                'venue','snapshot_relation','scope_role'})
COLUMNS.update({'primary_source_url', 'target_title', 'target_doi', 'target_arxiv',
                'source_title', 'source_doi', 'source_arxiv', 'source_url',
                'online_status', 'search_date_utc', 'exact_query_time_utc', 'search_method'})
# Textual evaluations can contain source passages and are excluded entirely.
for unsafe in ('assessment','os_target','llm_role','security_task','uncertainty','triggers','basis','证据来源',
               'Paper','Title','OS','组件','发表'):
    COLUMNS.discard(unsafe)

JSON_KEYS = set('''query_id query url started_utc timestamp_utc timestamp limit status
total_results returned start max_results raw_file http_status retry_after_seconds batch attempt
doi_count input_filename input_sha256 protocol_sha256 records abstract_only batch_size model
workers run_start_utc input_records total_batches batch_status decisions evidence_match year_scope
successful_batches attempted_batches total_batches frozen_missing_records status_counts
original_total original_returned refresh_total_last_page refresh_page_coverage_reached_last_reported_total
refresh_unique_versioned_ids refresh_unique_arxiv_ids new_records_with_abstract
status_counts offset_started next_offset last_reported_total reached_last_reported_total
returned_rows initial tail initial_rows tail_rows frozen_sha256 missing_records record_doi_pairs
unique_dois batch_size seed per_stratum sample_size population_size'''.split())

SAFE_CODE = {
 'public_export.py', 'search/run_crossref_search.py', 'search_protocol/unify.py',
 'search_protocol/search_crossref_100.py', 'search_protocol/search_arxiv.py',
 'arxiv_pagination/compare_frozen.py','arxiv_pagination/combine_refresh.py',
 'arxiv_pagination/fetch_pages.py','arxiv_pagination/fetch_tail.py','arxiv_pagination/incremental.py',
 'openalex/fetch.py','openalex/resume.py','openalex/extract.py',
 'screening/run_triage.py','screening/aggregate.py','screening/postprocess_policy.py',
 'screening/compare_passes.py','screening/run_third_review.py','screening/build_priority_queue.py',
 'inventory/build_inventory.py','audit/draw_screening_sample.py','audit/compare_sample_with_current.py',
 'audit/map_citations.py','audit/build_complete_citation_map.py',
 'revision/citation_audit.py',
 'source_data/quick_select_200.py','source_data/dedup_crossref20.py','source_data/merge_final_literature.py',
}
SAFE_TEXT = {'screening/protocol.txt','screening/third_review_protocol.txt',
             'screening/HUMAN_REVIEW.md','MANUSCRIPT_ALIGNMENT.md','inventory/README.md',
             'search/HISTORICAL_SEARCH_DATE.md','revision/INTEGRITY_NOTES.md',
             'revision/four_study_evidence_20261106.md',
             'search/historical_query_formulations.txt',
             'screening/README.md','search_protocol/README.md',
             'search_protocol/reporting_checklist.md','arxiv_pagination/README.md',
             'audit/README.md','revision/README.md','revision/claim_citation_audit.md',
             'revision/old_reference_number_mapping.md',
             'revision/bibliography_metadata_audit.md',
             'revision/bibliography_metadata_batch_1.md',
             'revision/bibliography_metadata_batch_2.md',
             'revision/bibliography_metadata_batch_3.md',
             'revision/cyber_reports_20261106.md',
             'openalex/README.md','SUBMISSION_STATUS.md'}
SAFE_JSON_NAMES = {'arxiv_search_log.json','pages.json','summary.json','compare_summary.json',
                   'comparison_summary.json','run_manifest.json','input_manifest.json','manifest.json',
                   'screening_audit_sample_manifest.json','screening_audit_current_comparison_manifest.json',
                   'provenance.json'}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def safe_url(value):
    try:
        parts=urllib.parse.urlsplit(value)
        if parts.scheme not in ('http','https'): return value
        qs=urllib.parse.parse_qsl(parts.query,keep_blank_values=True)
        qs=[(k,v) for k,v in qs if k.casefold() not in {'api_key','apikey','key','token','access_token','mailto','email'}]
        return urllib.parse.urlunsplit((parts.scheme,parts.netloc,parts.path,urllib.parse.urlencode(qs),parts.fragment))
    except ValueError: return ''

def clean_value(value):
    # Metadata only; prevent unexpected giant records or embedded multiline prose.
    if not isinstance(value,str): return value
    if len(value)>2000 or '\n' in value or '\r' in value: return '[omitted: non-metadata value]'
    return safe_url(value) if value.startswith(('https://','http://')) else value

def filter_json(obj):
    if isinstance(obj,list): return [filter_json(x) for x in obj]
    if not isinstance(obj,dict): return clean_value(obj)
    out={}
    for k,v in obj.items():
        if k not in JSON_KEYS: continue
        if isinstance(v,dict):
            # Aggregate tables use arbitrary category labels but only numeric values.
            out[k]={a:b for a,b in v.items() if isinstance(b,(int,float)) and not isinstance(b,bool)}
        else: out[k]=filter_json(v)
    return out

def write_csv(src,dst):
    with src.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames: return []
        fields=[k for k in reader.fieldnames if k in COLUMNS]
        if not fields: return []
        dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('w',encoding='utf-8-sig',newline='') as out:
            w=csv.DictWriter(out,fieldnames=fields); w.writeheader()
            for row in reader: w.writerow({k:clean_value(row.get(k,'')) for k in fields})
        return fields

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_directory',help='New directory outside this repository; must not already exist')
    args=parser.parse_args()
    target=Path(args.output_directory).expanduser().resolve()
    if target==ROOT or ROOT in target.parents:
        parser.error('output directory must be outside this repository')
    if target.exists(): parser.error('output directory already exists; choose a new path')
    # Freeze manifest source list before creating output; never overwrite anything.
    def source_files():
        return sorted(p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink()
                      and not {'.git', '__pycache__'}.intersection(p.relative_to(ROOT).parts))
    paths=source_files()
    target.mkdir(parents=True,exist_ok=False)
    manifest=[]
    for src in paths:
        rel=src.relative_to(ROOT).as_posix()
        dst=target/rel
        original_hash=digest(src)
        action='omitted'; columns=[]
        if src.suffix.lower()=='.csv':
            columns=write_csv(src,dst)
            if columns: action='metadata_csv'
        elif rel in SAFE_CODE or rel in SAFE_TEXT:
            dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
            action='code' if rel in SAFE_CODE else ('documentation' if src.suffix.lower()=='.md' else 'protocol_template')
        elif src.name in SAFE_JSON_NAMES and 'raw/' not in rel and '/batches/' not in rel:
            try:
                data=filter_json(json.loads(src.read_text(encoding='utf-8')))
                dst.parent.mkdir(parents=True,exist_ok=True)
                dst.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                action='filtered_json'
            except (ValueError,UnicodeError): pass
        elif rel.startswith('openalex/') and src.name=='request_log.jsonl':
            entries=[filter_json(json.loads(s)) for s in src.read_text(encoding='utf-8').splitlines() if s]
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in entries),encoding='utf-8')
            action='filtered_request_log'
        manifest.append({'original_path':rel,'original_sha256':original_hash,'original_size':src.stat().st_size,
                         'action':action,'exported_path':rel if dst.exists() else '',
                         'exported_sha256':digest(dst) if dst.exists() else '',
                         'exported_columns':' | '.join(columns)})
    final_paths={p.relative_to(ROOT).as_posix():p for p in source_files()}
    prior_paths={r['original_path'] for r in manifest}
    changed=[]
    for row in manifest:
        p=final_paths.get(row['original_path'])
        after=digest(p) if p else ''
        row['original_sha256_after']=after
        if after!=row['original_sha256']: changed.append(row['original_path'])
    added=sorted(set(final_paths)-prior_paths)
    with (target/'export_state.json').open('w',encoding='utf-8') as f:
        json.dump({'source_files_changed_or_removed':changed,'source_files_added_during_export':added,
                   'stable':not changed and not added},f,ensure_ascii=False,indent=2)
    with (target/'original_file_manifest.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(manifest[0]));w.writeheader();w.writerows(manifest)
    invalid_columns=[]; integrity_errors=[]; forbidden_files=[]
    for row in manifest:
        if not row['exported_path']: continue
        p=target/row['exported_path']
        if digest(p)!=row['exported_sha256']: integrity_errors.append(row['exported_path'])
        if row['action']=='metadata_csv':
            with p.open(encoding='utf-8-sig',newline='') as f: columns=next(csv.reader(f),[])
            bad=[c for c in columns if c not in COLUMNS]
            if bad: invalid_columns.append({'path':row['exported_path'],'columns':bad})
        rel=row['exported_path']
        if '/raw/' in '/'+rel or '/batches/' in '/'+rel or p.suffix.lower() in {'.xml','.xlsx'} or p.name=='prompt.txt':
            forbidden_files.append(rel)
    validation={'source_stable':not changed and not added,'disallowed_csv_columns':invalid_columns,
                'output_integrity_errors':integrity_errors,'forbidden_raw_or_batch_files':forbidden_files,
                'limits':'Field-level and file-level checks only; this is not a licensing decision or a guarantee that all possible short quotations are absent.'}
    (target/'export_validation.json').write_text(json.dumps(validation,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (target/'README.md').write_text('''# Metadata-only review archive\n\nThis export contains selected search queries, request metadata, bibliographic metadata, decision labels and processing code. Supplementary Table S1 is `supplementary_candidate_inventory.csv`; Supplementary Table S2 is `supplementary_legacy_inventory.csv`. It omits abstracts, source excerpts, raw provider responses, individual model prompts and model event/output files. `original_file_manifest.csv` records original paths, SHA-256 hashes, sizes, export actions, output hashes and retained CSV columns. It may include hashes of omitted files; hashes do not provide their contents. `export_state.json` and `export_validation.json` report source consistency and file/field checks.\n\nThe export is not a substitute for access to the underlying abstracts or full texts. Without the withheld inputs and model responses, readers cannot fully reproduce the offline screening or verify every model decision; they may retrieve the sources independently or obtain appropriate authorization. Some code requires omitted source files and does not execute end to end from this archive alone.\n\nPRISMA-S recommends removing abstracts from search result files before public sharing: https://jmla.pitt.edu/ojs/jmla/article/view/962/1274 . This technical export is not a rights or licensing determination. Review all exported materials, data-source terms and licensing before release.\n''',encoding='utf-8')
    with (target/'README.md').open('a',encoding='utf-8',newline='\n') as f:
        f.write('\n## Current manuscript method\n\n'
                'The manuscript is LLM-Assisted OS Security: A Component-Based Scoping Survey. '
                'The historical 59 in-depth candidates are a subset of 220 scored records within 485 archived records. '
                'The updated inventory contains 225 = 130 retained + 95 additional records, including 23 provisional direct candidates. '
                'Later synthesis additions leave those snapshot counts unchanged.\n\n'
                'Three human reviewers read and voted on relevance; selection required at least two positive votes. '
                'The author confirmed this procedure and that individual study-level voting records were not retained. '
                'See [screening/HUMAN_REVIEW.md](screening/HUMAN_REVIEW.md). '
                'The manuscript snapshot and full verification inputs are available in the full research repository; '
                'this metadata-only export does not support the complete verification workflow.\n')
    counts={}
    for r in manifest: counts[r['action']]=counts.get(r['action'],0)+1
    print('OUTPUT',target,'actions',json.dumps(counts,ensure_ascii=False),'source_stable',not changed and not added)
    if changed or added or invalid_columns or integrity_errors or forbidden_files:
        print('Export validation failed; inspect export_state.json and export_validation.json before sharing.',file=sys.stderr)
        sys.exit(2)

if __name__=='__main__': main()
