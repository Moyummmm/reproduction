# Bibliography metadata audit — completion record

**Completed:** 2026-11-05  
**Scope:** all 116 unique citation keys in the active manuscript at the start of this audit, checked against publisher, conference, official repository, arXiv, or author-maintained records where available.

## Result

- Checked title, ordered authors, publication type and venue, year, DOI or canonical URL, volume/issue/page or article-number fields, and likely preprint/final-version duplication.
- Applied metadata corrections to 101 reference entries, including complete author lists, official venue and publication records, DOI/URL fields, canonical title casing, and article-number/page-range corrections. The detailed, source-linked findings and per-key recommendations are in [batch 1](bibliography_metadata_batch_1.md), [batch 2](bibliography_metadata_batch_2.md), and [batch 3](bibliography_metadata_batch_3.md).
- Consolidated `zheng2023ken` (the earlier arXiv version) into the final `zheng2024kgent` citation. That review concluded with **115 active citation keys**, with no missing BibTeX records. Two provider reports on kernel exploitability were subsequently added on 2026-11-06; see [the targeted addendum](cyber_reports_20261106.md).
- Corrected `wang2025absint`: the cited 2025 paper identifies itself as an ICLR conference paper, not a VerifAI workshop paper. A later ICML 2026 version has a revised title; the current citation remains associated with the 2025 paper described in the manuscript.
- Where no archival publication was located in the checked records, the verified arXiv version remains cited. These cases and the source basis are recorded in the batch reports.

## Validation

At the end of that review, `python3 reproduct/revision/citation_audit.py` reported **115 cited keys and 0 missing BibTeX entries**. The accompanying inventory match counts (33 candidate matches and 82 without a candidate-inventory match) describe that snapshot and are linkage data, not metadata errors. Run the script for the current manuscript after later additions. DOI/version and source URLs were manually checked against the linked records. The separate [reviewer reference-number crosswalk](old_reference_number_mapping.md) maps the cited old manuscript numbers to the current disposition.

The `\smy{...}` wrappers on changed bibliography titles preserve the manuscript's yellow revision marking. Citation-label replacements for the KEN/Kgent consolidation use `\revcite{...}`.
