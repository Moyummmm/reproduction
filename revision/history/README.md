# Historical documentation

These files preserve superseded documentation and verification metadata. They are not the current account of the manuscript's methodology.

- `REVIEWER_RESPONSE_METHODS_DRAFT_before_20261107.md` predates the supplied historical search date and the three-person voting clarification. The current response-letter source is in `../manuscript_snapshot/docs/response_letter.tex`.
- `screening_README_before_20261111.md`, `screening_build_checksums_before_20261111.py`, and `screening_verify_replay_before_20261111.py` preserve the documentation and tools covered by `screening_SHA256SUMS_before_20261111` before the alignment update.
- The old manifest still verifies the unchanged search and model evidence. `../../verify_alignment.py` checks its updated-tool/documentation entries against the preserved copies listed above and all other entries against their original paths.
- The original arXiv-pagination and OpenAlex READMEs and `SHA256SUMS` files are preserved with the same `_before_20261111` naming convention. Their current READMEs correct commands for the standalone repository; their original evidence hashes remain checked.

The current human-review procedure and its missing per-study records are documented in `../../screening/HUMAN_REVIEW.md`. See `../INTEGRITY_NOTES.md` for byte-level recovery and the current verification commands.
