#!/usr/bin/env python3
"""Recompute derived exports and compare byte-level checksums."""
import hashlib,json,subprocess,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for folder,source in [(ROOT,ROOT.parent/'search_protocol/records.csv'),(ROOT/'arxiv_extension',ROOT.parent/'arxiv_pagination/combined_20261105/new_records.csv'),(ROOT/'crosssource/triage',ROOT/'crosssource/supplemented_records.csv')]:
    with tempfile.TemporaryDirectory() as tmp:
        out=Path(tmp); shutil.copy2(folder/'run_manifest.json',out/'run_manifest.json'); (out/'batches').symlink_to((folder/'batches').resolve(),target_is_directory=True)
        subprocess.run(['python3',str(ROOT/'aggregate.py'),'--input-file',str(source),'--output-dir',str(out)],check=True,capture_output=True)
        checks[str(folder.relative_to(ROOT))+'/screening_results.csv']=digest(out/'screening_results.csv')==digest(folder/'screening_results.csv')
names=['second_pass/comparison.csv','third_pass/third_review.csv','priority_review_queue.csv','high_priority_review_queue.csv']
before={n:digest(ROOT/n) for n in names}
for script in ['compare_passes.py','finalize_third_review.py','build_priority_queue.py']:
    subprocess.run(['python3',str(ROOT/script)],check=True,capture_output=True)
checks.update({n:before[n]==digest(ROOT/n) for n in names})
report={'byte_identical':checks,'note':'Derived outputs replay saved model events; no claim of model factual accuracy.'}
(ROOT/'replay_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
if not all(checks.values()): raise SystemExit(1)
