#!/usr/bin/env python3
"""Write combined new identifiers not present in an earlier new-record batch."""
import csv
import sys
from pathlib import Path

def read(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

before, combined = read(sys.argv[1]), read(sys.argv[2])
existing = {r['record_id'] for r in before}
extra = [r for r in combined if r['record_id'] not in existing]
with Path(sys.argv[3]).open('w',encoding='utf-8-sig',newline='') as f:
    writer = csv.DictWriter(f,fieldnames=list(combined[0]))
    writer.writeheader()
    writer.writerows(extra)
print('previous',len(before),'combined',len(combined),'incremental',len(extra))
