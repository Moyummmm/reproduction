"""Conservative guard applied after, never represented as a model response.

Keywords are deliberately broad and do not guarantee recall. Every automated
exclusion remains preliminary even if no keyword matches.
"""
import re
PATTERNS = [r'\bkernel\b',r'\blinux\b',r'\boperating\s+systems?\b',r'\bos\b',r'\bdrivers?\b',r'\bsyscalls?\b',r'\bsystem\s+calls?\b',r'\bebpf\b',r'\bfile\s*systems?\b',r'\bwindows\b',r'\bandroid\b',r'\btees?\b',r'\btrusted\s+execution\b',r'\bhypervisors?\b',r'\bfirmware\b',r'\bmacos\b',r'\bios\b',r'\bvirtual\s+machine\b',r'\benclaves?\b']
KNOWN_SEED_IDS = {'R00612','R06009','R06015','R06061','R06116'}
def os_target(record):
    text=record.get('title','')+' '+record.get('abstract','')
    hits=[p for p in PATTERNS if re.search(p,text,re.IGNORECASE)]
    if record.get('record_id') in KNOWN_SEED_IDS: hits.append('known_seed')
    return hits
