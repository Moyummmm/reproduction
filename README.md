# Literature collection and reproducibility materials

This repository contains the available reproducibility materials for **LLM-Assisted OS Security: A Component-Based Scoping Survey**, including search queries, saved results, inventories, screening records, audit notes and supporting scripts. The public repository is https://github.com/Moyummmm/reproduction.

This directory records the available evidence for the retrospective survey and the subsequent exploratory update. The historical search and screening records are incomplete. These files support inspection and partial reproduction; they do not establish an exhaustive search, an independently screened study set, or a final count of unique eligible studies.

## Alignment with the 11 November 2026 manuscript

The current account is mapped to the manuscript in [MANUSCRIPT_ALIGNMENT.md](MANUSCRIPT_ALIGNMENT.md). The source snapshot, its file hashes and the current citation mappings are under [revision/](revision/README.md). Earlier dated audits retain their historical scope.

| Manuscript quantity | Meaning and relationship |
|---|---|
| 485 historical records | All rows in the surviving historical archive. |
| 220 scored records | The subset of the 485 records with original relevance scores 1--3. |
| 59 in-depth candidates | The score-3 subset of those 220 scored records. |
| 225 updated candidates | A separately assembled snapshot: 130 retained historical records plus 95 additional records. |
| 23 provisional direct candidates | The score-3 subset of the 225-record updated inventory. |
| Four later synthesis additions | KnitFuzz already occurs as C0194 in the updated inventory; K-Repro, SyzHarness and Live-kBench occur as R06024, R06010 and R06013 in the separate discovery audit. The frozen inventory denominators remain unchanged. |

These record sets are not a consecutive selection flow. The 12 studies in the representative comparison table are illustrative evaluations, not the total number of eligible studies. Ten concern kernel or driver workflows; the component-coverage paragraph explains the kernel's central security role and the different workflows represented.

### Manual relevance review

As confirmed by the author on **11 November 2026**, three reviewers read each study considered at the manual review stage and then voted on its relevance to the survey scope. Selection required **at least two of the three votes in favor**; a 2--1 disagreement was resolved by the majority vote. The author confirmed that **individual study-level voting records were not retained**. [screening/HUMAN_REVIEW.md](screening/HUMAN_REVIEW.md) records the procedure, its provenance and the available evidence. It does not claim independent or blinded screening, agreement statistics, or that every retrieved record received a manual vote.

## New discovery audit and preliminary screening

- `search_protocol/README.md` describes a separate Crossref top-100 and arXiv search snapshot, exact query logs, hit-to-record mapping, SHA-256 checks and deterministic offline reconstruction. `search_protocol/reporting_checklist.md` maps the documented process and its gaps to PRISMA-S search-reporting topics.
- `arxiv_pagination/README.md` describes a later paginated refresh of two previously truncated arXiv searches, including the requests, rate-limit interruption and comparison to the frozen snapshot. It is a separate run, with its own time and possible ranking changes.
- `screening/` holds the frozen automated protocol, inputs, prompts, raw model outputs, preliminary record-level decisions and review queues, alongside the separately documented human procedure. The two calls for records with available abstracts used separate sessions of `deepseek/deepseek-flash`. Their saved labels remain preliminary model assessments; the three-person majority vote describes the subsequent manual relevance review.
- `audit/` contains mappings from manuscript citations, targeted source checks, known-study retention checks, and a separately documented Codex review of a stratified sample. This automated audit is not human independent screening.
- `revision/` contains the citation-to-inventory and citation-to-search mappings for the revised manuscript, source-checked bibliography reports and a manuscript source snapshot for running the current citation audit when this directory is copied independently. The four studies recommended in GPT-generated feedback and added after source checks are documented in `revision/four_study_evidence_20261106.md` and `revision/four_study_screening_20261106.csv`. These records do not overwrite the earlier frozen citation audit. The former appendix source is kept here for reference only and is not part of the current manuscript.
- `openalex/README.md` records an attempted DOI-based abstract enrichment. The service returned HTTP 429 and reported its anonymous daily allowance exhausted. The attempt retrieved no new abstracts; failed and unattempted requests are not exclusions.

These later search and screening materials are separate from the earlier 225-row candidate workbook described below. Their results do not retroactively reconstruct the historical survey's selection decisions. Raw responses and prompts contain source-provided abstracts; the optional metadata-only export described in `PUBLIC_EXPORT.md` omits those texts and individual model inputs and outputs.

## How studies were identified

1. **Historical collection.** The initial Google Scholar search is dated 10 March 2026, as supplied during the 7 November 2026 manuscript revision. Eighteen saved query formulations describe the earlier search themes. The surviving archive has 485 rows; 220 were scored, including 59 designated for in-depth review. The original query execution logs, result lists and complete screening decisions were not retained; see `search/HISTORICAL_SEARCH_DATE.md`.
2. **Exploratory update on 5 November 2026.** One search used 100 transformed free-text Crossref queries, with up to 20 results per query. Its later candidate workbook has 225 records, including 23 provisional direct OS-security candidates. A separate discovery audit used Crossref and arXiv, followed by pagination of two arXiv queries. The saved logs, linkage rules and preliminary model-assisted screening are documented under `search/`, `search_protocol/`, `arxiv_pagination/` and `screening/`.
3. **Targeted additions on 6 November 2026.** KnitFuzz, K-Repro, SyzHarness and Live-kBench were suggested in GPT-generated feedback shared by the author, then examined using Codex-assisted checks of accessible sources. Matching records were also identified in the previously saved candidate inventory or discovery audit; those matches are traceability links and do not replace the recommendation as the immediate source of these additions. See the four-study evidence and decision files under `revision/` for source versions, locators, inclusion rationale and extraction scope. The frozen inventory counts remain unchanged.

LLM-assisted source checks and the human voting procedure have separate provenance. The saved November 6 checks do not contain individual human votes; the manual procedure is documented from the author's November 11 clarification. For KnitFuzz, the publisher abstract and the authors' artifact documentation were available, but the full paper was not retrieved during the documented source check.

## Inventories

- `supplementary_legacy_inventory.csv` (Supplementary Table S2): the 220 records with scores 1–3 (45, 116 and 59 respectively) in the surviving historical archive. These counts match the earlier manuscript, but the submitted supplementary file is unavailable for a record-by-record comparison. The archive has 485 rows; the other 265 rows cannot be treated as verified exclusions.
- `supplementary_candidate_inventory.csv` (Supplementary Table S1): the later 225-row merged candidate inventory. It contains 130 retained legacy records and 95 additional records. Six further new records were matched to retained records during the original merge. Scores 0, 1, 2 and 3 have 1, 37, 164 and 23 records respectively. Scores indicate preliminary topical fit, not verified eligibility or study quality.
- `legacy_to_candidate_crosswalk.csv`: all 485 historical rows, their old and revised scores, and documented or provisional links to the later inventory. Absence of a link does not establish an exclusion decision.
- `potential_duplicate_pairs.csv`: flagged candidate pairs. Consult its status and evidence before treating records as one study.
- `inventory/build_inventory.py` and `inventory/sources/`: inputs and script used to export the inventories and crosswalk. These reproduce record-level exports from the saved snapshots, not the historical screening decisions.
- `source_data/`: the 200-record quick-screen input and archived selection/merge scripts. Those scripts preserve their original workspace paths and should be read as provenance, not run directly against this directory.

The 220 and 225 inventories are different record sets, not sequential stages. Their scores use different assessments. A candidate or an old score of 3 does not establish a unique eligible study. Abstract and conclusion summaries have different evidence scopes; see the `证据范围` and source columns for each current record.

## Search snapshot

`search/historical_query_formulations.txt` preserves the 18 historical formulations formerly displayed in the manuscript. These are separate from the 100 later search queries. A date for the initial search was supplied during revision, but the original query execution logs and results were not retained; see `search/HISTORICAL_SEARCH_DATE.md`.

`google_scholar_queries.csv` contains the 100 original query formulations. Automated Google Scholar requests encountered HTTP 429/CAPTCHA, and were not bypassed. On 5 November 2026, an exploratory Crossref bibliographic search was run instead. Each query requested up to 20 results, with a publication-date lower bound of 2022-01-01. The script removes quotation marks, Boolean operators and parentheses before passing the query to Crossref; its search is not an exact implementation of the original Boolean expressions.

`search/search_metadata.csv` records each original query, timestamp (China Standard Time), outcome and returned count. `search/q001.csv` through `q100.csv` and `search/all_results.csv` preserve the 2,000 returned result rows with query identifiers and ranks. Search results may contain the same work under multiple queries. The top-20 limit, Crossref coverage and ranking, and subsequent quick selection limit recall. Later top-100 Crossref and arXiv searches in the working project were not incorporated into this 225-record inventory.

`search/run_crossref_search.py` records the request parameters and query transformation. To rerun it without overwriting the snapshot, copy `google_scholar_queries.csv` and the `search/` directory into a separate working directory preserving their relative paths, then run `python3 search/run_crossref_search.py` from that copy. It makes network requests and overwrites its local result files. Crossref metadata and ranking change over time, so future results can differ from the saved snapshot.

The 18 saved historical formulations describe earlier search themes. The initial search date was supplied during revision; original execution logs, database-specific execution details, and returned results for that earlier collection are unavailable. They are not the same logged search as the 100-query update.

## Checking the saved materials

From the repository root, use Python 3.10 or later to run the offline checks:

```sh
python -X utf8 verify_alignment.py
```

This verifies the inventory relationships, later additions, representative-study selection, citation mappings, source-snapshot hashes, current evidence checksums, and the original frozen checksums. It also replays the saved screening outputs in a temporary copy. It makes no network or model calls and does not overwrite the archive. To check against a separate live manuscript checkout as well, pass `--manuscript-root /path/to/manuscript`.

The completed checks and their results are recorded in [revision/VALIDATION_20261111.md](revision/VALIDATION_20261111.md).

`.gitattributes` preserves exact file bytes on Windows and other platforms. [revision/INTEGRITY_NOTES.md](revision/INTEGRITY_NOTES.md) documents the restoration of CSV serialization to the already-recorded hashes and distinguishes updated documentation and verification scripts from frozen search/model evidence. Fresh network searches or model calls can return different results; saved snapshots are the basis of the reported counts.

For publication, `PUBLIC_EXPORT.md` explains how to create a separate metadata-only copy without overwriting this archive. That copy omits abstracts and raw model responses; its hashes identify omitted files but do not enable their content to be checked or replayed without separately obtaining them.

The revision directory also contains `claim_citation_audit.md`, which records the technical-claim/citation review, and `literature_addendum.csv`, which records LLM-CAL, the later-added OpenAI and Anthropic reports, and the four studies identified in the targeted follow-up, separately from the frozen inventory counts.
