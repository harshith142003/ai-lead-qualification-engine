import time

import httpx

SOURCE_URL = "https://hn.algolia.com/api/v1/search"


def scrape_companies(limit: int = 10) -> list[dict]:
    """Collect recent Show HN projects from a public API."""

    params = {
        "tags": "show_hn",
        "hitsPerPage": limit,
    }

    headers = {
        "User-Agent": "AILeadQualificationEngine/1.0"
    }

    for attempt in range(3):
        try:
            response = httpx.get(
                SOURCE_URL,
                params=params,
                headers=headers,
                timeout=15,
            )

            if response.status_code == 429:
                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            data = response.json()

            companies = []

            for hit in data.get("hits", []):
                title = hit.get("title") or ""
                company_name = title.replace(
                    "Show HN:", "", 1
                ).strip()

                website = hit.get("url") or ""
                story_id = hit.get("objectID", "")

                if not company_name:
                    continue

                companies.append({
                    "company_name": company_name,
                    "website": website,
                    "description": hit.get("story_text") or title,
                    "source_url": (
                        f"https://news.ycombinator.com/item?id={story_id}"
                    ),
                })

            return companies

        except (httpx.HTTPError, ValueError):
            if attempt == 2:
                raise

            time.sleep(2 ** attempt)

    return []
