# Saved two-source search snapshot and record preparation

These files preserve exploratory searches executed on 5 November 2026, not a prospective or exhaustive systematic search. `records.csv` is an unscreened identifier-level inventory. No eligibility, quality, publication-status, language, or date-window decision is implied by appearing here.

## Sources and execution

Crossref: 100 bibliographic queries ran from 05:43:38 to 05:50:07 UTC, all returned 100 records (10,000 hits); all 100 were truncated because their reported total exceeded 100. Queries used `query.bibliographic`, `rows=100`, and `from-pub-date:2022-01-01`, with no upper publication-date bound. The original query expressions were transformed by removing quotes, parentheses and Boolean words. These are relevance-ranked free-text queries, not Boolean queries. `crossref/search_log.csv` gives the exact effective expression, request URL, UTC timestamp, total, returned count and status; `crossref/raw/qNNN.json` preserves each response, and `crossref/results.csv` is the corresponding structured hit export.

arXiv: 12 separate topic queries ran from 05:39:14 to 05:40:15 UTC and returned 467 hits, capped at 100 per query, sorted by relevance, without a date filter. The `kernel_vulnerability` and `exploit` searches were truncated (reported totals 112 and 1,284; 100 returned each). `arxiv_search_log.json` records exact expressions, request URLs, timestamps, total and returned counts; `arxiv_raw/` contains the Atom responses, and `arxiv_results.csv` is the structured hit export. OpenAlex, Semantic Scholar and Google Scholar were unavailable to the prior automated search; IEEE Xplore, ACM DL, Scopus and Web of Science were not searched for this snapshot. Database coverage and the caps limit recall.

The two sources have different date limits, ranking and indexing; the manuscript's 2020–2026 intended scope must be applied during documented screening rather than inferred from retrieval. Publication and preprint dates may differ. Search-result counts and ordering can change over time, so the saved snapshots are the basis for the reported counts.

## Conservative record linkage

Run `python3 reproduct/search_protocol/unify.py` from the project root (Python standard library only). It reads the two saved hit exports and deterministically regenerates `records.csv` and `hit_to_record.csv`, overwriting these derived files. It groups hits only when normalized DOI or version-stripped arXiv ID matches exactly, using transitive links. A hit with neither identifier remains separate. Identical titles alone are not merged. These groups are provisional records, not verified unique publications or studies; version relations with different identifiers, metadata errors and title conflicts require manual review. The process produces 10,467 hit rows, 6,408 groups, 2,311 groups with an abstract supplied in at least one saved hit and 4,097 without one. Missing abstracts may be available from other sources; missing is not an exclusion decision.

`SHA256SUMS` freezes the two derived files, their script and inputs, the search logs and the saved provider responses. From this directory run `shasum -a 256 -c SHA256SUMS` to check them. A separate temporary-directory regeneration was checked to reproduce the derived files byte for byte.

For a new network search, run `python3 reproduct/search_protocol/search_crossref_100.py` and `python3 reproduct/search_protocol/search_arxiv.py`. The copies change the original scripts only to locate `reproduct/google_scholar_queries.csv` and to create a separate timestamped arXiv output directory, respectively. Both create new timestamped directories; they do not modify the saved search snapshot. A subsequent run has a new search date and must retain its own log and results.

## Data dictionary

`records.csv` has one row per provisional identifier group:

| Field | Meaning |
|---|---|
| `record_id` | Deterministic identifier within this snapshot; assigned in order of the first hit. A different snapshot can produce different IDs. |
| `title`, `authors`, `year` | Metadata from the hit having the longest nonempty retrieved abstract, or the first hit if all abstracts are missing. Years are source metadata, not an adjudicated study publication date. |
| `doi`, `arxiv_id` | Distinct nonempty identifiers in the group, separated by semicolons. |
| `abstract`, `abstract_status` | Longest abstract returned by either source in the group, or empty with status `missing`. This does not certify abstract accuracy or access elsewhere. |
| `source_set`, `urls`, `hit_count` | Distinct source names, source URLs and number of hit rows linked to the group. |
| `abstract_source`, `abstract_source_hit_id` | Source and `hit_id` supplying the selected abstract; blank when unavailable. |

`hit_to_record.csv` maps every individual source hit to its group. `hit_id` identifies the hit in the saved input order (Crossref, then arXiv); `source`, `query_id` and `rank` locate it in the relevant source result; DOI, arXiv ID, URL and title preserve the matching evidence. The source exports contain additional fields and the raw files preserve the provider responses.
