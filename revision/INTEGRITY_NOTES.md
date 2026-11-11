# Evidence integrity and platform portability

Update date: **11 November 2026**.

Cloning the repository on Windows with Git's automatic LF/CRLF conversion changed the working-tree bytes of text files, causing recorded SHA-256 checks to fail. The Git-stored versions of 31 CSV files also had normalized line endings that differed from the original frozen hashes.

The original recorded hashes were retained as the recovery targets. CSV record separators were restored using the original CSV serialization. The Crossref hit export was regenerated from the saved provider JSON with the original extraction rules; `records.csv` was regenerated in a temporary directory by the original `search_protocol/unify.py`. Each recovered file was accepted only when its SHA-256 exactly matched the already-recorded hash. No new searches, model calls, human votes or data values were introduced. `frozen_csv_recovery_20261111.json` lists the affected files.

All entries in the original search and screening manifests passed before documentation and verification-tool edits began. `.gitattributes` now disables automatic line-ending conversion so future checkouts preserve the stored bytes, including CSV record separators and embedded newlines.

## Current and historical manifests

- `search_protocol/SHA256SUMS` is unchanged.
- The current and original `arxiv_pagination/` and `openalex/` manifests are also checked. Their only documentation changes are README command-path corrections; the original READMEs and manifests are preserved under `history/`.
- `history/screening_SHA256SUMS_before_20261111` preserves the previous screening manifest.
- The original screening README, checksum builder and replay verifier are preserved under `history/`. These are the only old-manifest entries whose live documentation/tool versions were updated.
- `screening/SHA256SUMS` covers the current screening files, including the manual-procedure document and updated verification utilities. Paths use forward slashes on every platform.
- `manuscript_snapshot_manifest.json` separately pins the current manuscript source and response-letter snapshot.

`python -X utf8 verify_alignment.py` checks both generations of evidence hashes. For the three updated screening documentation/tool entries and the two updated pagination/enrichment READMEs, it checks the archived original bytes against the old manifests; all other old-manifest entries are checked at their original paths. It also verifies inventory relationships and regenerates citation mappings and screening results in temporary directories. The working archive is not overwritten, and network/model calls are not made.

These checks establish file integrity and agreement between recorded quantities and source files. They do not reconstruct missing individual human votes, establish exhaustive retrieval, or certify every technical claim in the surveyed studies.
