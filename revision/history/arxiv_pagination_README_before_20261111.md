# Pagination refresh for two truncated arXiv searches

The frozen `../search_protocol/` snapshot showed truncation for `kernel_vulnerability` and `exploit`. A new refresh repeated both queries from offset zero on 5 November 2026; it did not modify the frozen 6,408-record inventory. `fetch_pages.py` records the query, request URL, UTC timestamp, status, returned count and each raw Atom response in a new timestamped directory.

The initial refresh `run_20261105T075850Z/` returned kernel offsets 0 and 100 (112 records total), and exploit offsets 0 through 900 (1,000 records). The exploit request at offset 1,000 received HTTP 429 at 08:00:49 UTC; this failure remains in `pages.json`. `tail_20261105T080327Z/` records the resumed requests at offsets 1,000, 1,100 and 1,200 (284 records), ending at 08:03:56 UTC. `fetch_tail.py` logs all attempts, including any rate-limit errors, and writes a new output directory. Both queries reached their last reported totals: 112 and 1,284 respectively. These are live relevance-ranked requests made at different times; records may move between offsets, so the retrieved pages cannot prove a stable exhaustive set despite reaching the reported last page.

`combined_20261105/results.csv` contains all 1,396 returned hit rows. `combine_refresh.py` records which saved directories were combined. `compare_frozen.py` groups those hits by version-stripped arXiv ID and compares them to the frozen inventory using exact arXiv ID, then exact DOI. The result is 1,383 distinct arXiv IDs: 211 match an existing arXiv ID, four match only an existing DOI, and 1,168 have neither match. The latter are *new identifiers for screening*, not confirmed new unique studies; other version and title matches may exist. All 1,168 carry a retrieved abstract.

`combined_20261105/new_records.csv` contains the full new-identifier set. `refresh_links.csv` records all grouped identifiers, their source query and rank pairs, and matching frozen record IDs where found. The stable `record_id` for an unmatched record is `arxiv:` plus its version-stripped arXiv identifier. `abstract_source_hit_id` records the query and rank supplying the chosen (longest) abstract. The `published` and `updated` fields preserve the source timestamps; they do not establish the final publication version.

The earlier 888-record `run_20261105T075850Z/new_records.csv` was already sent for screening. `combined_20261105/incremental_new_records.csv` contains the 280 additional identifiers not in that earlier batch, so the two screening files do not overlap. To reconstruct this incremental file:

```
python3 reproduct/arxiv_pagination/incremental.py reproduct/arxiv_pagination/run_20261105T075850Z/new_records.csv reproduct/arxiv_pagination/combined_20261105/new_records.csv /tmp/arxiv_incremental.csv
```

The raw pages, results, logs and mapping outputs can be checked using `shasum -a 256 -c SHA256SUMS` from this directory. The reported matching counts are provisional and do not constitute eligibility decisions.
