# Search reporting audit

This is a reporting aid for the saved 5 November 2026 exploratory snapshot, guided by [PRISMA-S](https://doi.org/10.1186/s13643-020-01542-z) and the selection-reporting items in [PRISMA 2020](https://doi.org/10.1136/bmj.n71). It does not claim that the snapshot is an exhaustive systematic review or that all checklist items have been met. The historical search is separately described as unrecoverable in the manuscript.

| Search-reporting item | Evidence or limitation for this snapshot |
|---|---|
| 1. Sources and interfaces | Crossref REST API and arXiv export API; see `README.md`, query logs and raw responses. These are two distinct services. |
| 2. Combined platform | No simultaneous multi-database platform was used in this snapshot. |
| 3. Study registries | None documented for this snapshot. |
| 4. Sites and browsing | No additional structured browsing is recorded as part of this two-source search. The original historical collection used other material, but its complete sources cannot be reconstructed. |
| 5. Citation searches | No backward or forward citation search is recorded as part of the two-source snapshot. Mapping citations already in the manuscript is an audit, not a citation-search procedure. |
| 6. Contacts | No contact with authors or experts is recorded for this snapshot. |
| 7. Other discovery methods | Historical records and the manuscript are a separate source; they are not part of the counts for this snapshot. |
| 8. Exact strategies | `crossref/search_log.csv` gives original and effective queries and URLs; `arxiv_search_log.json` gives arXiv queries and URLs. |
| 9. Limits | Crossref: 2022-01-01 onward, no upper date limit, at most 100 relevance-ranked records per query. arXiv: no date filter, at most 100 per query. No language restriction is recorded. Intended manuscript coverage is 2020–2026; source dates and the manuscript window are different. All Crossref queries and two arXiv queries were truncated. |
| 10. Published search filters | No published search filter is documented for this snapshot. |
| 11. Reuse of prior strategies | The 100 Crossref queries were derived from the project's earlier query list and transformed for `query.bibliographic`. The 12 arXiv queries were separately formulated from topical themes. Their relationship to older historical search formulations is not a verified reconstruction. |
| 12. Updates | This was a separately documented exploratory search, not a documented rerun of the unrecoverable historical search. Future reruns create new timestamped result directories. |
| 13. Search dates | Crossref 2026-11-05 05:43:38–05:50:07 UTC; arXiv 2026-11-05 05:39:14–05:40:15 UTC. The historical search dates remain unknown. |
| 14. Search peer review | A formal independent peer review of the search strategy is not documented. |
| 15. Retrieved records | Crossref 10,000 hit rows; arXiv 467 hit rows. Query-level totals and truncation appear in the logs. |
| 16. Record linkage | `unify.py` groups exact normalized DOI and version-stripped arXiv identifiers. `hit_to_record.csv` traces each hit. The resulting 6,408 groups are provisional records, not a verified count of unique studies; different identifiers for the same work can remain separate. |

## Selection-reporting boundaries

The snapshot itself does not identify a final included-study set. Any later title/abstract triage must separately disclose the screener or automated tool, input version, protocol, record-level decisions, failures, and any unresolved records. AI-assisted screening must not be reported as independent human review. An eventual flow diagram must be computed from the actual decision file and show missing or pending decisions rather than treating them as exclusions.

The snapshot's source limits, ranking caps, missing abstracts and version ambiguity constrain retrieval and selection. Search reporting improves auditability but cannot establish exhaustive coverage. A persistent public archive and the final public URL or DOI must be supplied when the authors release the materials.
