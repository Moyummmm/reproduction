#!/usr/bin/env python3
"""Combine saved initial and resumed response exports; preserve each source hit."""
import csv
import json
import sys
from pathlib import Path

initial, tail, output = (Path(x).resolve() for x in sys.argv[1:4])
output.mkdir(exist_ok=False)
def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
old, more = read(initial/'results.csv'), read(tail/'results.csv')
with (output/'results.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f,fieldnames=list((old or more)[0]))
    writer.writeheader()
    writer.writerows(old + more)
(output/'provenance.json').write_text(json.dumps({'initial':initial.name,'tail':tail.name,
    'initial_rows':len(old),'tail_rows':len(more),
    'limitation':'These pages were fetched at different times and relevance ordering can shift; reaching the last reported page does not prove a stable exhaustive snapshot.'},indent=2),encoding='utf-8')
print('initial',len(old),'tail',len(more),'total',len(old)+len(more),'output',output)
