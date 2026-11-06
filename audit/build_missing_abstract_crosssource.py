#!/usr/bin/env python3
"""Conservative local cross-source linkage for high-priority records missing abstracts.

No external API calls. Abstracts copied only from saved source text; summaries are
explicitly labelled as summaries, not represented as an original abstract.
"""
import collections,csv,hashlib,html,json,re,unicodedata
from pathlib import Path
from urllib.parse import unquote

P=Path(__file__).resolve().parent; R=P.parent
paths={'queue':R/'screening/high_priority_review_queue.csv',
       'search':R/'search_protocol/records.csv',
       'arxiv_refresh':R/'arxiv_pagination/combined_20261105/new_records.csv',
       'arxiv_results':R/'arxiv_pagination/combined_20261105/results.csv',
       'legacy_candidates':R/'supplementary_candidate_inventory.csv'}
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(s):
    s=html.unescape(html.unescape(s or ''));s=re.sub(r'<[^>]+>',' ',s)
    return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())
def getdoi(s):
    s=unquote(s or ''); m=re.search(r'10\.\d{4,9}/[^\s<>";]+',s,re.I)
    return m.group(0).casefold().rstrip('.,)') if m else ''
def getarxiv(s):
    m=re.search(r'(?:arxiv\.org/(?:abs|pdf)/|arxiv:)(\d{4}\.\d{4,5})(?:v\d+)?',s or '',re.I)
    return m.group(1) if m else ''
def first_author(s):
    first=(s or '').split(';')[0].strip()
    if not first:return ''
    if ',' in first: first=first.split(',')[0]
    else: first=first.split()[-1]
    return norm(first)

queue=[x for x in read(paths['queue']) if x['abstract_status']=='missing']
search=read(paths['search']); base={x['record_id']:x for x in search}
sources=[]
for x in search:
    sources.append({'dataset':'search_protocol/records.csv','id':x['record_id'],'title':x['title'],'authors':x['authors'],'doi':getdoi(x['doi']),'arxiv':x['arxiv_id'],'url':x['urls'],'abstract':x['abstract'],'kind':'saved_source_abstract' if x['abstract'].strip() else 'no_abstract'})
for x in read(paths['arxiv_refresh']):
    sources.append({'dataset':'arxiv_pagination/combined_20261105/new_records.csv','id':x['record_id'],'title':x['title'],'authors':x['authors'],'doi':getdoi(x['doi']),'arxiv':x['arxiv_id'],'url':x['urls'],'abstract':x['abstract'],'kind':'saved_arxiv_abstract' if x['abstract'].strip() else 'no_abstract'})
for x in read(paths['arxiv_results']):
    sources.append({'dataset':'arxiv_pagination/combined_20261105/results.csv','id':x['id'],'title':x['title'],'authors':x['authors'],'doi':getdoi(x['doi']),'arxiv':getarxiv(x['id']),'url':x['id'],'abstract':x['abstract'],'kind':'saved_arxiv_abstract' if x['abstract'].strip() else 'no_abstract'})
for x in read(paths['legacy_candidates']):
    text=x['摘要']; summary=x['摘要概述']
    kind='candidate_abstract_fragment_unverified' if text.strip() else ('candidate_paraphrase_not_abstract' if summary.strip() else 'no_abstract')
    sources.append({'dataset':'supplementary_candidate_inventory.csv','id':x['candidate_id'],'title':x['标题'],'authors':x['作者'],'doi':getdoi(x['DOI'] or x['文章链接']),'arxiv':next((getarxiv(x[k]) for k in ['文章链接','全文链接','摘要来源','结论来源'] if getarxiv(x[k])),''),'url':x['摘要来源'] or x['文章链接'] or x['全文链接'],'abstract':text if text.strip() else summary,'kind':kind})

title_index=collections.defaultdict(list); doi_index=collections.defaultdict(list); arxiv_index=collections.defaultdict(list)
for x in sources:
    if norm(x['title']):title_index[norm(x['title'])].append(x)
    if x['doi']:doi_index[x['doi']].append(x)
    if x['arxiv']:arxiv_index[x['arxiv']].append(x)
out=[]; alternatives=[]
for q in queue:
    t=base[q['record_id']]; td=getdoi(t['doi']); ta=t['arxiv_id']; tt=norm(t['title']); author=first_author(t['authors']); found={}
    for rule, seq in [('exact DOI',doi_index.get(td,[]) if td else []),('exact arXiv ID',arxiv_index.get(ta,[]) if ta else []),('exact normalized title',title_index.get(tt,[]) if tt else [])]:
        for x in seq:
            if x['dataset']=='search_protocol/records.csv' and x['id']==t['record_id']:continue
            identity=(x['dataset'],x['id']); entry=found.setdefault(identity,{'source':x,'rules':set()});entry['rules'].add(rule)
    ranked=[]
    for ent in found.values():
        x=ent['source'];rules=ent['rules']; sa=first_author(x['authors']); titleeq=tt==norm(x['title']); author_match=bool(author and sa and author==sa)
        identifier=bool({'exact DOI','exact arXiv ID'}&rules)
        contradiction=bool(identifier and author and sa and author!=sa and not titleeq)
        confidence='matched' if not contradiction and (identifier or (titleeq and author_match)) else 'ambiguous'
        rank=(confidence=='matched',x['kind'] in ('saved_source_abstract','saved_arxiv_abstract'),bool(x['abstract']),x['dataset']!='supplementary_candidate_inventory.csv')
        ranked.append((rank,x,rules,confidence,author_match))
    ranked.sort(key=lambda v:(v[0],v[1]['dataset'],v[1]['id']),reverse=True)
    for _,x,rules,confidence,am in ranked:
        alternatives.append({'target_record_id':t['record_id'],'source_dataset':x['dataset'],'source_record_id':x['id'],'match_status':confidence,'rules':'; '.join(sorted(rules)),'first_author_match':str(am).lower(),'source_title':x['title'],'source_authors':x['authors'],'source_doi':x['doi'],'source_arxiv':x['arxiv'],'source_url':x['url'],'text_kind':x['kind'],'saved_text':x['abstract']})
    confident=[v for v in ranked if v[3]=='matched']; ambiguous=[v for v in ranked if v[3]=='ambiguous']
    best=(confident or ambiguous)[0] if ranked else None
    if best:
        _,x,rules,status,am=best
        out.append({'record_id':t['record_id'],'target_title':t['title'],'target_authors':t['authors'],'target_doi':t['doi'],'target_arxiv':t['arxiv_id'],'match_status':status,'source_dataset':x['dataset'],'source_record_id':x['id'],'match_rules':'; '.join(sorted(rules)),'source_title':x['title'],'source_authors':x['authors'],'source_doi':x['doi'],'source_arxiv':x['arxiv'],'source_url':x['url'],'text_kind':x['kind'],'saved_text':x['abstract'],'possible_source_count':len(ranked),'disposition':'candidate paraphrase/fragment is not a verified abstract' if x['kind'].startswith('candidate_') else ('saved source text; title/ID linkage remains auditable' if x['abstract'] else 'linked record; no abstract recovered')})
    else:
        out.append({'record_id':t['record_id'],'target_title':t['title'],'target_authors':t['authors'],'target_doi':t['doi'],'target_arxiv':t['arxiv_id'],'match_status':'missing','source_dataset':'','source_record_id':'','match_rules':'','source_title':'','source_authors':'','source_doi':'','source_arxiv':'','source_url':'','text_kind':'none','saved_text':'','possible_source_count':0,'disposition':'no local cross-source match found; not proof paper or abstract is unavailable'})
def write(name,rows):
    with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
write('missing_abstract_crosssource.csv',out)
if alternatives:write('missing_abstract_crosssource_alternatives.csv',alternatives)
summary={'targets':len(out),'status':dict(collections.Counter(r['match_status'] for r in out)),'best_text_kind':dict(collections.Counter(r['text_kind'] for r in out)), 'input_sha256':{k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in paths.items()},'notice':'matching is record linkage, not eligibility, and saved paraphrases are not original abstracts'}
(P/'missing_abstract_crosssource_manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
