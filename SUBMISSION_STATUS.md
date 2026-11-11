# Reproducibility status for the current manuscript

Status date: **11 November 2026**. Manuscript: **LLM-Assisted OS Security: A Component-Based Scoping Survey**.

## Documented and aligned

- The initial Google Scholar search date is 10 March 2026, supplied during revision; 18 query formulations survive. The dated November 5 Crossref update, separate Crossref/arXiv discovery audit and arXiv pagination retain their own logs and counting units.
- The historical archive has 485 records. Its 220 scored records include 59 score-3 in-depth candidates. The separately assembled updated inventory has 225 = 130 retained historical + 95 additional records, including 23 provisional direct candidates.
- The author confirmed the manual relevance procedure: three reviewers read each study under consideration and voted; at least two positive votes were required, and 2--1 disagreements were resolved by majority vote. Individual study-level voting records were not retained. See `screening/HUMAN_REVIEW.md`.
- Automated title/abstract assessments used `deepseek/deepseek-flash`, with a separate call using the same model for records with abstracts. Model labels, later model rechecks and the Codex audit retain their automated status and are distinct from human votes.
- KnitFuzz, K-Repro, SyzHarness and Live-kBench were added to the synthesis after the November 6 source checks. Their existing-record links are C0194, R06024, R06010 and R06013. The inventory counts remain fixed.
- Table 3 contains 12 representative comparisons, including ten kernel/driver workflows. The manuscript explains the kernel emphasis and the scope of the other two targets.
- The current manuscript source snapshot, response-letter source and 125 citation-key mappings are under `revision/`. The mapping reports no missing bibliography entries; it does not certify every technical claim.

## Evidence limits retained

1. **Individual votes and final eligible-study count.** The reported procedure is author-confirmed, but the exact manually reviewed set and per-study outcomes cannot be reconstructed. No final deduplicated eligible-study count or fully logged selection flow is asserted. Candidate scores and model agreement do not substitute for votes.
2. **Historical search execution.** Original query execution logs and complete result lists are unavailable. The supplied search date is distinguished from the later executable logs.
3. **Retrieval coverage and missing abstracts.** The discovery snapshot contains 6,408 identifier groups, including 4,097 without a saved abstract. Search caps, separate pagination times and unresolved versions limit coverage. Missing evidence is not a verified exclusion.
4. **Publication/preprint versions.** The manuscript's version policy is documented, while unresolved links remain visible in the inventory and possible-duplicate files.

The public repository is https://github.com/Moyummmm/reproduction. [MANUSCRIPT_ALIGNMENT.md](MANUSCRIPT_ALIGNMENT.md) gives the statement-to-evidence mapping. Run `python -X utf8 verify_alignment.py` for offline checks; add `--manuscript-root /path/to/manuscript` to compare the source snapshot with a live checkout. `PUBLIC_EXPORT.md` describes the optional metadata-only export and its reduced replay scope.
