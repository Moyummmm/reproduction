# OpenAlex abstract enrichment attempt

The frozen `../search_protocol/records.csv` contains 4,097 records with no abstract in the stored Crossref/arXiv responses; each has a DOI. The intent is to fetch metadata in batches of at most 50 DOI values, reconstruct any `abstract_inverted_index`, and maintain a record-level result for all inputs. Source records remain unchanged. `fetch.py`, `resume.py`, and `extract.py` use Python's standard library and require the frozen input SHA-256 recorded in the run manifest.

## Saved attempt and current status

In `run_20261105T081119Z/`, the first batch was attempted four times on 5 November 2026 and each request received HTTP 429. The provider's saved response reports that the anonymous IP's daily budget was exhausted, with reset at midnight UTC. Subsequent batches were not requested. `request_log.jsonl` records exact URLs, UTC timestamps, response status and saved error bodies; `input_doi_map.csv` records the record-to-DOI input and `input_manifest.json` freezes the source hash. The initial fetch script has since been updated to stop at the first HTTP 429 and capture the provider's cooldown instead of retrying during it.

`supplement.csv` has 4,097 rows: 50 `request_error` and 4,047 `not_attempted`; zero abstracts were retrieved. These statuses do **not** mean that OpenAlex lacks an abstract. The provider's response and failure must not be counted as title/abstract screening decisions. `summary.json` reports the same counts.

## Resuming and extraction

After the provider's cooldown, `python -X utf8 openalex/resume.py reproduct/openalex/run_20261105T081119Z` copies the original run to a new timestamped directory and resumes there without repeating successful batches. It checks the saved 429 cooldown, writes each request URL, response/error, UTC timestamp and retry information, waits two seconds between successful batches, and stops at the first error. It writes response bodies to `raw/`. The optional `LLM4OSSEC_OPENALEX_API_KEY` environment variable is sent only in the HTTP authorization header and is not written to the URLs or logs; do not put credentials into files in this directory. Merely setting a key does not authorize publishing it.

After fetching (or stopping), run `python -X utf8 openalex/extract.py <the-new-run-directory>` using the output path printed by `resume.py`. It reconstructs each available inverted index in position order, maps each exact DOI to the frozen `record_id`, and replaces `supplement.csv` and `summary.json` in that new directory. Statuses distinguish `available`, `openalex_no_abstract`, `not_found`, `invalid_index`, `response_truncated`, `request_error`, `not_attempted` and `no_doi`. Retain raw responses as the evidence for extracted text. DOI matches and available abstracts still require study-level screening and do not establish eligibility.
