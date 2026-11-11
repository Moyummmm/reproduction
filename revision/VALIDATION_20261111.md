# Alignment verification record

Validation date: **11 November 2026**. Source baseline: repository commit `98a3a41b04b18638ba6897603151b9c0e98fa61a`, followed by the manuscript-alignment changes in this working branch. Checks ran on Windows with Python 3.12.14.

Command from the repository root:

```sh
python -X utf8 verify_alignment.py --manuscript-root /path/to/current/manuscript
```

Result: **passed**, with no reported errors.

| Check | Observed result |
|---|---|
| Historical inventory | 485 rows; the scored subset contains 220 rows, with scores 1/2/3 distributed as 45/116/59. |
| Updated inventory | 225 rows = 130 retained historical + 95 additional records; score distribution 0/1/2/3 is 1/37/164/23. |
| Inventory regeneration | All four derived inventory/crosswalk CSVs reproduce the same rows from the saved local sources. |
| Figure 2 denominator | 225 candidates; 27 missing venues, 20 arXiv-only venues and three book-series-only venues. |
| Search quantities | 18 historical formulations; 100 update queries and 2,000 top-20 hit rows; 10,467 discovery hit rows, 6,408 groups and 2,311 groups with abstracts; 1,168 extension records. |
| Later additions | All four citation keys link to the documented C0194/R06024/R06010/R06013 records and are present in the current citations. |
| Representative table | All 12 entries match the manuscript; ten have kernel/driver targets. |
| Source snapshot | All 11 pinned files match both their hashes and the live manuscript source, including the response-letter source. |
| Current citation audit | 125 keys; zero missing BibTeX entries; 34 candidate-inventory links and 28 discovery-snapshot links. Both mapping files regenerate byte for byte. |
| Frozen/current hashes | All 119 search-manifest entries, all 1,371 current screening-manifest entries, and all 1,370 historical screening-manifest entries pass. The three updated documentation/tool entries in the historical manifest are checked against their archived originals. |
| Pagination/enrichment hashes | All 36 arXiv-pagination entries and all 13 OpenAlex entries pass in both current and original manifests; original READMEs are checked from the historical copies. |
| Saved model responses | 260 successful response files match their saved event streams: 161 first pass, 58 second pass, 30 arXiv extension, ten third pass and one cross-source batch. |
| Screening replay | Seven derived screening/comparison/queue CSVs regenerate byte for byte in a temporary copy. |
| Metadata-only export | Export validation passes; human-review and alignment documentation are included; S1/S2 retain 225/220 rows; Git metadata and Python caches are excluded; source files remain unchanged. |
| Edited Python utilities | Syntax checks pass. |

The initial working-tree hash failures and the 31 CSV restorations are documented in [INTEGRITY_NOTES.md](INTEGRITY_NOTES.md). The larger CSV diff reflects recovery of frozen serialization, not newly supplied screening outcomes.

Human relevance review is documented from the author's confirmation of three readers and majority voting. Individual study-level voting records were not retained, so the checks above do not verify individual human decisions or compute a final eligible-study count.
