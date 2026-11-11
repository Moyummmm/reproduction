# Citation audit for the revised manuscript

Current source snapshot: **11 November 2026**, *LLM-Assisted OS Security: A Component-Based Scoping Survey*. `manuscript_snapshot_manifest.json` records the included source paths and SHA-256 hashes. The snapshot includes the current title, abstract, body sections, bibliography and response-letter source for text and citation checks; it is not a standalone PDF build bundle.

`../MANUSCRIPT_ALIGNMENT.md` maps the current methodology and counts to their evidence. `representative_studies.csv` records the 12 Table 3 entries and the ten kernel/driver targets used in the component-coverage explanation. `history/` preserves superseded method-response text and the pre-update screening verification metadata. The dated claim and bibliography audits below remain historical audit reports.

`citation_audit.py` scans the current manuscript's active section files, including `sections/representative_comparison.tex`. It recognizes ordinary `\cite{...}` calls and the revision-highlighted `\revcite{...}` and `\newrevcite{...}` forms. It preserves the original audit's conservative title, DOI, arXiv and source-checked alias matching rules. Use `--manuscript-root "path/to/manuscript"` to select an Overleaf checkout explicitly; otherwise the existing workspace/snapshot selection applies.

From the repository root, run `python -X utf8 revision/citation_audit.py` to regenerate the two CSV mappings from `revision/manuscript_snapshot/`. Pass `--manuscript-root /path/to/manuscript` for another source tree and `--output-dir /path/to/new-output` to keep regenerated mappings outside this directory. The snapshot must be refreshed when the paper changes. The script reads the 225-record candidate inventory and saved discovery snapshot from this repository. Exact matches and manually checked aliases are bibliographic links, not final eligibility decisions. This current-version audit is separate from the earlier frozen files in `audit/` so their screening provenance remains intact.

The file claim_citation_audit.md records the parallel, source-based review of technical claims, corrections made, and evidence boundaries. The file literature_addendum.csv records LLM-CAL, the later-added OpenAI and Anthropic technical reports, and the four recommended studies separately from the frozen candidate inventory counts. The file old_reference_number_mapping.md maps the reviewer-numbered weak references to the current manuscript and records their disposition. The file bibliography_metadata_audit.md records the completed metadata review; its linked batch reports give per-reference source checks and corrections.

The optional metadata-only export omits the manuscript snapshot and some source fields used by the script; use the full research directory for the standalone regeneration described above.

Run `python -X utf8 ../verify_alignment.py` from this directory, or `python -X utf8 verify_alignment.py` from the repository root, for a read-only check of the source hashes, mappings, counts and frozen evidence. Adding `--manuscript-root /path/to/manuscript` compares the snapshot with the live source files. `INTEGRITY_NOTES.md` documents byte-preservation and the checksum migration.

`cyber_reports_20261106.md` records the source basis and evidence boundaries for the two later-added provider reports on LLM-assisted kernel exploitation.

`pre_compression_20261106/` preserves the four sections as they stood before the page-reduction edit. The current citation-audit source snapshot is `manuscript_snapshot/`.

`four_study_screening_20261106.csv` records the source-assisted inclusion decisions for KnitFuzz, K-Repro, SyzHarness and Live-kBench, linked to existing inventory or discovery-audit identifiers. The four studies were initially suggested in GPT-generated feedback shared by the author; matching the saved records was a later traceability step. `four_study_evidence_20261106.md` records the source versions, numerical extraction and limits, including the abstract/artifact-only extraction for KnitFuzz. These files leave the frozen inventories and preliminary model decisions intact.
