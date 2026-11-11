#!/usr/bin/env python3
"""Verify saved events and replay derived exports in an isolated temporary copy."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(script, *args):
    result = subprocess.run(
        [sys.executable, '-X', 'utf8', str(script), *map(str, args)],
        capture_output=True, text=True, encoding='utf-8',
    )
    if result.returncode:
        raise RuntimeError(f'{script.name}: {result.stdout}\n{result.stderr}')
    return result.stdout


def main():
    checks = {}
    with tempfile.TemporaryDirectory(prefix='reproduction-replay-') as tmp:
        archive = Path(tmp) / 'archive'
        shutil.copytree(ROOT.parent, archive,
                        ignore=shutil.ignore_patterns('.git', '__pycache__'))
        work = archive / 'screening'
        saved = json.loads(run(work / 'verify_saved_responses.py'))
        sources = [
            (Path('.'), archive / 'search_protocol/records.csv'),
            (Path('arxiv_extension'), archive / 'arxiv_pagination/combined_20261105/new_records.csv'),
            (Path('crosssource/triage'), work / 'crosssource/supplemented_records.csv'),
        ]
        for folder, source in sources:
            run(work / 'aggregate.py', '--input-file', source, '--output-dir', work / folder)
            output = folder / 'screening_results.csv'
            checks[output.as_posix()] = digest(work / output) == digest(ROOT / output)
        for script in ['compare_passes.py', 'finalize_third_review.py', 'build_priority_queue.py']:
            run(work / script)
        for name in ['second_pass/comparison.csv', 'third_pass/third_review.csv',
                     'priority_review_queue.csv', 'high_priority_review_queue.csv']:
            checks[name] = digest(work / name) == digest(ROOT / name)
    report = {'byte_identical': checks, 'saved_response_verification': saved,
              'note': 'Offline replay in a temporary copy; source archive unchanged. '
                      'This checks consistency, not model accuracy or human votes.'}
    print(json.dumps(report, indent=2))
    return 0 if all(checks.values()) and not saved['errors'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
