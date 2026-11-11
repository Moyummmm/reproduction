# Manuscript and repository alignment

Alignment date: **11 November 2026**. Manuscript: **LLM-Assisted OS Security: A Component-Based Scoping Survey**.

The current account is based on the manuscript source snapshot under `revision/manuscript_snapshot/`, the saved inventories and search logs, and the author's clarification of the human voting procedure. `revision/manuscript_snapshot_manifest.json` records source-file hashes. Earlier dated audit reports describe earlier manuscript versions.

| Manuscript statement | Repository evidence and interpretation |
|---|---|
| Retrospective component-based scoping survey, covering 2020--2026 | `revision/manuscript_snapshot/sections/methodology.tex`, Introduction and title in `main.tex`. PRISMA-S and PRISMA 2020 guide reporting; the files do not establish an exhaustive systematic review. |
| Initial Google Scholar search on 10 March 2026 with 18 query formulations | `search/HISTORICAL_SEARCH_DATE.md` and `search/historical_query_formulations.txt`. The date was supplied during revision; original execution logs and result lists were not retained. The older query file's date-unknown wording is historical. |
| Exploratory update on 5 November 2026 using 100 transformed Crossref queries | `google_scholar_queries.csv`, `search/search_metadata.csv`, `search/all_results.csv`, and `search/run_crossref_search.py`. This top-20 search uses a 2022 publication-date lower bound. |
| Separate Crossref/arXiv discovery audit and arXiv pagination | `search_protocol/` and `arxiv_pagination/`. The discovery audit has 10,467 hit rows and 6,408 exact-identifier groups; the later extension adds 1,168 records under the documented linkage rules. These are separate from the 225-record candidate inventory. |
| 485 historical records, including 220 scored records and 59 in-depth candidates | `inventory/sources/legacy_original.csv` has 485 rows; `supplementary_legacy_inventory.csv` (S2) contains the 220 rows scored 1--3, including the 59 scored 3. The other rows are not verified exclusions. |
| Updated inventory of 225 = 130 retained + 95 additional records | `supplementary_candidate_inventory.csv` (S1), `legacy_record_id`, `source_relation`, and `legacy_to_candidate_crosswalk.csv`. The 130 retained records are drawn from the historical archive; they are not all members of the earlier 220 scored subset. |
| 23 provisional direct OS-security candidates | The 23 score-3 rows of the 225-record updated inventory. Scores describe topical relevance, not final eligibility or quality. The 59 and 23 belong to different snapshots. |
| Figure 2 uses 225 candidates, with 50 undetermined venue fields | The `期刊会议` field in the candidate inventory: 20 arXiv-only records, 27 without a venue, and three book-series-only records. This is a record-level venue summary, not a study-selection flow. |
| Model-assisted preliminary assessment | `screening/run_manifest.json`, `protocol.txt`, saved batches and `second_pass/`. The model alias is `deepseek/deepseek-flash`; the second call uses the same model. |
| Three human reviewers; at least two positive votes required; 2--1 disagreement resolved by majority | `screening/HUMAN_REVIEW.md`, recorded from the author's 11 November clarification. Individual study-level voting records were not retained. The procedure is reported, but per-study decisions and agreement statistics cannot be reconstructed. |
| Publication/preprint version handling | Section III describes treating versions of the same contribution as one study, preferring a published version within the search period, and considering distinct extended contributions separately when justified. `inventory/README.md` and `potential_duplicate_pairs.csv` preserve unresolved version links; the policy does not imply that all version reconciliation is complete. |
| Four additions to the synthesis on 6 November | `revision/four_study_screening_20261106.csv`, `four_study_evidence_20261106.md`, and `literature_addendum.csv`. KnitFuzz links to C0194; K-Repro, SyzHarness and Live-kBench link to R06024, R06010 and R06013. Recommendations and source checks prompted incorporation; the existing-record links establish traceability. The snapshot counts remain fixed. |
| Table 3 compares 12 representative studies, including ten kernel/driver workflows | `revision/representative_studies.csv` and the current `sections/representative_comparison.tex` snapshot. PathSentinel and LLM-CAL provide the other two targets. The distribution describes this representative selection, not the numerical distribution or relative importance of all OS-security research. |
| Current citation-to-record links | `revision/citation_candidate_mapping.csv` and `citation_search_mapping.csv`, regenerated from the current snapshot. These have 125 active citation keys and no missing bibliography entries; bibliographic matches do not establish eligibility or verify every technical claim. |

## Limits that remain explicit

The individual voting records, original query execution logs, and a final deduplicated eligible-study list are unavailable. Documentation of the confirmed procedure improves agreement between the manuscript and repository; it does not recover those missing records. Historical model labels, candidate scores and old audit reports remain attributed to their original snapshots.

The current response-letter source is included at `revision/manuscript_snapshot/docs/response_letter.tex`. `REVIEWER_RESPONSE_METHODS_DRAFT.md` points to it; the earlier draft is archived under `revision/history/`.

Run `python -X utf8 verify_alignment.py` from the repository root to validate the stored facts, source snapshot, citation mappings and frozen evidence without network calls. An optional `--manuscript-root /path/to/manuscript` additionally checks that the snapshot matches a live checkout byte for byte.
