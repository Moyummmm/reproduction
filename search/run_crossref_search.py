#!/usr/bin/env python3
"""Run the 100 literature queries through Crossref and save one CSV per query.

Google Scholar blocks automated access with 429 / CAPTCHA from this IP, so this
script uses Crossref as an automated scholarly-search fallback. The original
Google Scholar query and a clickable Scholar URL are preserved in each row and
in google_scholar_links.csv.
"""
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
QUERIES = BASE.parent / "google_scholar_queries.csv"
OUT = BASE
META = OUT / "search_metadata.csv"
LINKS = OUT / "google_scholar_links.csv"
LOG = OUT / "SEARCH_LOG.md"
MAILTO = "research@example.com"
UA = f"LLM4OSSec-review/1.0 (mailto:{MAILTO})"
FIELDS = [
    "query_id", "query", "source", "rank", "title", "authors", "year", "venue",
    "doi", "url", "type", "citation_count", "abstract", "google_scholar_url",
]
SLEEP = 1.3


def clean_query(q: str) -> str:
    q = q.replace('"', " ")
    q = re.sub(r"\b(AND|OR|NOT)\b", " ", q, flags=re.I)
    q = q.replace("(", " ").replace(")", " ")
    return re.sub(r"\s+", " ", q).strip()


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s or "").replace("\n", " ").strip()


def crossref(q: str, rows: int = 20):
    params = {
        "query.bibliographic": q,
        "rows": str(rows),
        "filter": "from-pub-date:2022-01-01",
        "select": "title,author,issued,container-title,DOI,URL,abstract,type,publisher,is-referenced-by-count",
        "mailto": MAILTO,
    }
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)["message"]
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except Exception as e:
            last = e
            time.sleep(5 * (attempt + 1))
    raise last


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    queries = list(csv.DictReader(open(QUERIES, encoding="utf-8-sig")))
    link_rows = []
    meta_rows = []
    for item in queries:
        qid = int(item["id"])
        raw = item["query"]
        q = clean_query(raw)
        scholar_url = "https://scholar.google.com/scholar?" + urllib.parse.urlencode(
            {"hl": "en", "as_sdt": "0,5", "q": raw}
        )
        link_rows.append({
            "id": qid, "theme": item["theme"], "query": raw,
            "google_scholar_url": scholar_url,
            "crossref_csv": f"q{qid:03d}.csv",
        })
        path = OUT / f"q{qid:03d}.csv"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            msg = crossref(q, rows=20)
            items = msg.get("items", [])
            rows = []
            for rank, it in enumerate(items, 1):
                authors = []
                for a in it.get("author", []) or []:
                    name = " ".join(x for x in [a.get("given"), a.get("family")] if x).strip()
                    if name:
                        authors.append(name)
                issued = it.get("issued", {}).get("date-parts", [[None]])
                year = issued[0][0] if issued and issued[0] else ""
                venue = (it.get("container-title") or [""])[0]
                rows.append({
                    "query_id": qid, "query": raw, "source": "Crossref", "rank": rank,
                    "title": (it.get("title") or [""])[0],
                    "authors": "; ".join(authors), "year": year, "venue": venue,
                    "doi": it.get("DOI", ""), "url": it.get("URL", ""),
                    "type": it.get("type", ""),
                    "citation_count": it.get("is-referenced-by-count", ""),
                    "abstract": strip_tags(it.get("abstract", "")),
                    "google_scholar_url": scholar_url,
                })
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS)
                w.writeheader()
                w.writerows(rows)
            meta_rows.append({
                "query_id": qid, "query": raw, "source": "Crossref",
                "total_results": msg.get("total-results", ""), "returned": len(rows),
                "status": "ok", "timestamp": now,
                "note": "Google Scholar blocked (429/CAPTCHA); Crossref fallback with from-pub-date 2022-01-01",
            })
            print(f"q{qid:03d}: {len(rows)} rows", flush=True)
        except Exception as e:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                csv.DictWriter(f, fieldnames=FIELDS).writeheader()
            meta_rows.append({
                "query_id": qid, "query": raw, "source": "Crossref",
                "total_results": "", "returned": 0, "status": f"error: {e}",
                "timestamp": now,
                "note": "Google Scholar blocked (429/CAPTCHA); Crossref fallback failed",
            })
            print(f"q{qid:03d}: ERROR {e}", flush=True)
        time.sleep(SLEEP)

    with open(META, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(meta_rows[0]))
        w.writeheader()
        w.writerows(meta_rows)
    with open(LINKS, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(link_rows[0]))
        w.writeheader()
        w.writerows(link_rows)
    ok = sum(1 for r in meta_rows if r["status"] == "ok")
    LOG.write_text(f"""# Search log

- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} CST
- Queries: {len(queries)}
- Successful Crossref queries: {ok}
- Failed: {len(queries) - ok}

## Important note on Google Scholar

Google Scholar returned HTTP 429 / CAPTCHA ("sorry") pages to automated requests
from this environment. The block was not bypassed. Each CSV therefore contains
**Crossref** results for the same query string, restricted to 2022+ publications.
`google_scholar_links.csv` contains the original query and a clickable Google
Scholar URL so the same search can be run manually from a browser or an
institutional IP.

## Files

- `q001.csv` … `q100.csv` — one CSV per query (Crossref results, top 20)
- `search_metadata.csv` — query, status, total hits, returned rows, timestamp
- `google_scholar_links.csv` — original query + Google Scholar URL
""", encoding="utf-8")
    print("done", ok, "/", len(queries))


if __name__ == "__main__":
    main()
