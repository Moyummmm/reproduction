# Reproducibility status for resubmission

This is an audit status, not a claim that the historical review has been converted into a completed systematic review. The manuscript's historical search and screening decisions cannot be fully reconstructed from the retained files. The later searches and model triage are separate discovery and audit activities.

## What is recorded

- The historical archive has 485 records; 220 have original scores 1–3. A 485-row crosswalk and the later 225-candidate inventory are included. Agreement of the old counts with the prior manuscript does not prove identity with the unavailable historical supplementary file.
- The two-source audit has 10,467 retrieved hit rows, 6,408 exact-identifier record groups and a hit-level source map. Crossref queries were all capped at 100; two arXiv queries were later paginated in a separate run. Two different identifiers can still represent one study.
- Automated title/abstract triage preserves the inputs, prompts, model responses, schema checks and conservative flags. A separate call to the same model covers the 2,311 frozen records with saved abstracts. A targeted third model review and a separate 60-record Codex audit are also documented. Neither is independent human screening or final eligibility adjudication.
- The citation audit maps current manuscript citations to the available inventories where possible and records source-checked title/version aliases and known errors. Citation-role labels remain provisional.

## Items that remain open

1. **Final eligible studies and study-level counts.** No fully adjudicated study/version list or final inclusion/exclusion flow exists. Review the high-priority queue, missing evidence and known seed failures before using model labels as selection decisions. Match decisions to manuscript claims and citations, then compute all reported selection counts from the frozen final log.
2. **Independent review.** No independent human screening or adjudication is documented. Model agreement and the separate Codex sample do not substitute for it. Record actual reviewers, decisions, disagreements and resolution if such a review is performed.
3. **Missing abstracts.** The frozen search snapshot has 4,097 records without a saved abstract. An OpenAlex enrichment attempt received HTTP 429 on four attempts for the first batch of 50 DOI records; 4,047 further record lookups were not attempted. No abstract was obtained by that run. See `openalex/README.md` and the cross-source audit for recovery status.
4. **Search completeness.** The 100 Crossref searches were all truncated, and the refreshed arXiv pages span different request times and a rate-limit interruption. Searches are reproducible as saved snapshots, but coverage is bounded and cannot be called exhaustive.
5. **Public access and data rights.** The repository is available at https://github.com/Moyummmm/reproduction. Full raw data and model prompts include third-party abstract text. `PUBLIC_EXPORT.md` describes an optional metadata-only export that preserves hashes and decisions but cannot fully replay model screening without access to omitted inputs and responses.

Useful starting files: `search_protocol/README.md`, `search_protocol/reporting_checklist.md`, `screening/README.md`, `screening/high_priority_review_queue.csv`, `audit/README.md`, and `openalex/README.md`.
