# Citation audit for the revised manuscript

`citation_audit.py` scans the current manuscript's active section files, including `sections/representative_comparison.tex`. It recognizes both ordinary `\cite{...}` calls and the revision-highlighted `\revcite{...}` form. It preserves the original audit's conservative title, DOI, arXiv and source-checked alias matching rules.

From the project root, run `python3 reproduct/revision/citation_audit.py` to regenerate the two CSV mappings in this directory. When this directory is copied independently, run `python3 revision/citation_audit.py` from its root; the script uses `revision/manuscript_snapshot/` for the manuscript sections and `refs.bib`. In the full manuscript workspace it uses the live manuscript sources. The snapshot represents the manuscript at the time it was copied and must be refreshed if the paper changes. Both modes read the 225-record candidate inventory and saved discovery snapshot from this directory. Exact matches and manually checked aliases are bibliographic links, not final eligibility decisions. This current-version audit is separate from the earlier frozen files in `audit/` so their screening provenance remains intact.

The file claim_citation_audit.md records the parallel, source-based review of technical claims, corrections made, and evidence boundaries. The file literature_addendum.csv records LLM-CAL and the later-added OpenAI and Anthropic technical reports separately from the frozen candidate inventory. The file old_reference_number_mapping.md maps the reviewer-numbered weak references to the current manuscript and records their disposition. The file bibliography_metadata_audit.md records the completed metadata review; its linked batch reports give per-reference source checks and corrections.

The optional metadata-only export omits the manuscript snapshot and some source fields used by the script; use the full research directory for the standalone regeneration described above.

`cyber_reports_20261106.md` records the source basis and evidence boundaries for the two later-added provider reports on LLM-assisted kernel exploitation.

`pre_compression_20261106/` preserves the four sections as they stood before the page-reduction edit. The current citation-audit source snapshot is `manuscript_snapshot/`.
