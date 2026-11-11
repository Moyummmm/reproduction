#!/usr/bin/env python3
"""Check manuscript alignment and replay saved evidence without network or archive writes."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script, *args):
    result = subprocess.run([sys.executable, '-X', 'utf8', str(script), *map(str, args)],
                            capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{script.name}: {result.stdout}\n{result.stderr}')
    return result.stdout


def active_tex(text):
    text = re.sub(r'\\begin\{comment\}.*?\\end\{comment\}', '', text, flags=re.S)
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manuscript-root', type=Path,
                        help='Optional live manuscript to compare with the pinned snapshot')
    args = parser.parse_args()
    facts = json.loads((ROOT / 'revision/alignment_facts.json').read_text(encoding='utf-8'))
    errors, checked = [], {}

    def equal(name, actual, expected):
        checked[name] = actual
        if actual != expected:
            errors.append(f'{name}: expected {expected!r}, got {actual!r}')

    historical = rows(ROOT / 'inventory/sources/legacy_original.csv')
    legacy = rows(ROOT / 'supplementary_legacy_inventory.csv')
    candidates = rows(ROOT / 'supplementary_candidate_inventory.csv')
    crosswalk = rows(ROOT / 'legacy_to_candidate_crosswalk.csv')
    equal('historical_records', len(historical), facts['historical_records'])
    equal('historical_scored_records', len(legacy), facts['historical_scored_records'])
    equal('historical_score_counts', dict(Counter(r['historical_score'] for r in legacy)),
          facts['historical_score_counts'])
    historical_scored_ids = {str(i) for i, r in enumerate(historical, 1) if r['Relevance'] in {'1', '2', '3'}}
    equal('legacy_is_original_scored_subset', {r['legacy_record_id'] for r in legacy} == historical_scored_ids, True)
    equal('crosswalk_covers_historical_ids', {r['legacy_record_id'] for r in crosswalk} ==
          {str(i) for i in range(1, len(historical) + 1)}, True)
    equal('updated_candidate_records', len(candidates), facts['updated_candidate_records'])
    equal('retained_historical_records', sum(bool(r['legacy_record_id']) for r in candidates),
          facts['retained_historical_records'])
    equal('additional_candidate_records', sum(not r['legacy_record_id'] for r in candidates),
          facts['additional_candidate_records'])
    equal('updated_score_counts', dict(Counter(r['相关度评分（0–3）'] for r in candidates)),
          facts['updated_score_counts'])
    equal('candidate_source_relations', all(r['source_relation'] ==
          ('retained legacy record' if r['legacy_record_id'] else 'new candidate') for r in candidates), True)
    venues = [r['期刊会议'].strip() for r in candidates]
    equal('undetermined_venues', {
        'missing': sum(not v for v in venues),
        'arxiv_only': sum(v.casefold() == 'arxiv' for v in venues),
        'book_series_only': sum(v in facts['book_series_only_venue_names'] for v in venues),
    }, facts['undetermined_venues'])

    formulations = (ROOT / 'search/historical_query_formulations.txt').read_text(encoding='utf-8')
    equal('historical_query_formulations', sum(line.startswith('(') for line in formulations.splitlines()),
          facts['historical_query_formulations'])
    equal('update_queries', len(rows(ROOT / 'google_scholar_queries.csv')), facts['update_queries'])
    equal('top20_hit_rows', len(rows(ROOT / 'search/all_results.csv')), facts['top20_hit_rows'])
    discovery = rows(ROOT / 'search_protocol/records.csv')
    equal('discovery_record_groups', len(discovery), facts['discovery_record_groups'])
    equal('discovery_hit_rows', len(rows(ROOT / 'search_protocol/hit_to_record.csv')), facts['discovery_hit_rows'])
    equal('discovery_records_with_abstract', sum(bool(r['abstract'].strip()) for r in discovery),
          facts['discovery_records_with_abstract'])
    equal('arxiv_extension_records', len(rows(ROOT / 'arxiv_pagination/combined_20261105/new_records.csv')),
          facts['arxiv_extension_records'])
    model = json.loads((ROOT / 'screening/run_manifest.json').read_text(encoding='utf-8'))
    second = json.loads((ROOT / 'screening/second_pass/run_manifest.json').read_text(encoding='utf-8'))
    equal('preliminary_model', model['model'], 'deepseek/deepseek-flash')
    equal('second_pass_same_model', second['model'], model['model'])

    additions = {r['bibtex_key']: r for r in rows(ROOT / 'revision/four_study_screening_20261106.csv')}
    candidate_ids = {r['candidate_id'] for r in candidates}
    discovery_ids = {r['record_id'] for r in discovery}
    equal('four_addition_keys', sorted(additions), sorted(facts['later_synthesis_additions']))
    for key, expected in facts['later_synthesis_additions'].items():
        equal(key + '_prior_record', additions[key]['prior_record_id'], expected['record_id'])
        record_ids = candidate_ids if expected['record_set'] == 'updated_candidate_inventory' else discovery_ids
        equal(key + '_record_exists', expected['record_id'] in record_ids, True)

    snapshot = ROOT / 'revision/manuscript_snapshot'
    manifest = json.loads((ROOT / 'revision/manuscript_snapshot_manifest.json').read_text(encoding='utf-8'))
    equal('snapshot_title', manifest['manuscript_title'], facts['manuscript_title'])
    for rel, expected in manifest['files'].items():
        path = snapshot / rel
        if not path.is_file() or digest(path) != expected:
            errors.append('Snapshot hash mismatch: ' + rel)
        if args.manuscript_root:
            live = args.manuscript_root / rel
            if not live.is_file() or digest(live) != expected:
                errors.append('Live manuscript differs: ' + rel)
    checked['snapshot_files_verified'] = len(manifest['files'])
    checked['live_manuscript_compared'] = args.manuscript_root is not None
    table = active_tex((snapshot / 'sections/representative_comparison.tex').read_text(encoding='utf-8')).split('\\paragraph')[0]
    table_keys = re.findall(r'\\(?:newrev|rev)?cite\{([^}]+)\}', table)
    representative = rows(ROOT / 'revision/representative_studies.csv')
    equal('representative_studies', len(representative), facts['representative_studies'])
    equal('representative_table_keys', sorted(r['bibtex_key'] for r in representative), sorted(table_keys))
    equal('representative_kernel_or_driver_studies', sum(r['primary_target_group'] == 'kernel_or_driver' for r in representative),
          facts['representative_kernel_or_driver_studies'])

    # Regenerate outputs in temporary directories so checking cannot overwrite edited exports.
    with tempfile.TemporaryDirectory(prefix='manuscript-alignment-') as tmp:
        temp = Path(tmp)
        out = temp / 'citations'
        run(ROOT / 'revision/citation_audit.py', '--manuscript-root', snapshot, '--output-dir', out)
        for name in ['citation_candidate_mapping.csv', 'citation_search_mapping.csv']:
            equal(name + '_regenerates', (out / name).read_bytes() == (ROOT / 'revision' / name).read_bytes(), True)
        citation_rows = rows(out / 'citation_candidate_mapping.csv')
        equal('active_citation_keys', len(citation_rows), facts['active_citation_keys'])
        equal('missing_bibtex_entries', sum(r['match_status'] == 'missing BibTeX entry' for r in citation_rows), 0)
        equal('additions_in_current_citations', set(additions).issubset({r['bibtex_key'] for r in citation_rows}), True)
        checked['candidate_linked_citation_keys'] = sum(bool(r['candidate_matches']) for r in citation_rows)
        checked['discovery_linked_citation_keys'] = sum(bool(r['search_matches']) for r in rows(out / 'citation_search_mapping.csv'))
        inventory = temp / 'inventory'
        shutil.copytree(ROOT / 'inventory', inventory)
        run(inventory / 'build_inventory.py')
        for name in ['supplementary_candidate_inventory.csv', 'supplementary_legacy_inventory.csv',
                     'legacy_to_candidate_crosswalk.csv', 'potential_duplicate_pairs.csv']:
            equal(name + '_rows_regenerate', rows(temp / name) == rows(ROOT / name), True)

    manifests = [
        ('search_protocol/SHA256SUMS', ROOT / 'search_protocol', {}),
        ('screening/SHA256SUMS', ROOT, {}),
        ('revision/history/screening_SHA256SUMS_before_20261111', ROOT,
         facts['frozen_screening_updated_file_archives']),
    ]
    for item in facts['additional_frozen_manifests']:
        manifests.append((item['current'], ROOT / item['base'], {}))
        manifests.append((item['original'], ROOT / item['base'], item['updated_file_archives']))
    for rel, base, overrides in manifests:
        count = 0
        for line in (ROOT / rel).read_text(encoding='utf-8').splitlines():
            expected, name = line.split(maxsplit=1)
            name = name.lstrip('* ')
            path = ROOT / overrides[name] if name in overrides else base / name
            if not path.is_file() or digest(path) != expected:
                errors.append(f'{rel}: hash mismatch for {name}')
            count += 1
        checked[rel + '_entries'] = count

    if not errors:
        checked['screening_replay'] = json.loads(run(ROOT / 'screening/verify_replay.py'))
    report = {'alignment_date': facts['alignment_date'], 'passed': not errors,
              'checks': checked, 'errors': errors,
              'human_review_evidence': 'Author-confirmed procedure; individual voting records not retained.'}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
