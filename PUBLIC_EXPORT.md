# Optional metadata-only export

This repository contains the research materials intended for the repository. A separate filtered export is optional. Once screening and audit files have stopped changing, it can be generated at a **new path outside this directory**:

```sh
python3 public_export.py /path/to/new-public-directory
```

The script refuses existing destinations and destinations inside the repository. It copies selected code and protocol templates, exports only an explicit list of bibliographic metadata, search-log and decision fields, and omits abstracts, source quotations, provider raw responses, and individual model inputs/outputs. Every original file, including omitted files, is represented by its SHA-256 in `original_file_manifest.csv`; included outputs have separate hashes and retained CSV column names.

Inspect `export_state.json` and `export_validation.json` in the new directory. If source files changed during export or a validation check failed, the script exits with a nonzero status: use a fresh destination after inputs are stable. Validation checks file types, field allowlists and output hashes; it does not prove that every possible short quotation is absent and is not a rights or licensing determination.

The public export cannot fully reproduce offline model screening without the withheld abstracts and model responses. Researchers must independently obtain the source material or authorization where necessary. Review the exported metadata, source terms and project license before publication. This script does not upload or publish files.

The export includes the author-confirmed manual-review procedure in `screening/HUMAN_REVIEW.md` and the current methodology/count explanation. Individual voting records are unavailable in both the full archive and this export. Git metadata and Python cache files are excluded from the export manifest. The manuscript snapshot and full verification inputs remain available only in the full research archive.
