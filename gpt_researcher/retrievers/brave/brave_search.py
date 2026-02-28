"""Brave Search API retriever for GPT Researcher.

This module provides the BraveSearch class for performing web searches
using the Brave Search API, with optional freshness (recency) filtering.
"""

import logging
import os
from typing import List, Optional, Sequence

import requests

logger = logging.getLogger(__name__)

BRAVE_WEB_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# Freshness shortcuts supported by Brave: pd (day), pw (week), pm (month), py (year)
# Or date range: YYYY-MM-DDtoYYYY-MM-DD
FRESHNESS_VALID_SHORTCUTS = frozenset({"pd", "pw", "pm", "py"})


def _parse_freshness(freshness: Optional[str]) -> Optional[str]:
    """Return Brave freshness param or None. Valid: pd, pw, pm, py or YYYY-MM-DDtoYYYY-MM-DD."""
    if not freshness or not isinstance(freshness, str):
        return None
    s = freshness.strip().lower()
    if s in FRESHNESS_VALID_SHORTCUTS:
        return s
    # Optional: allow date range format
    if "to" in s and len(s) == 21 and s[4] == "-" and s[7] == "-" and s[10] == "t":
        return s
    return None


class BraveSearch:
    """
    Brave Search API retriever with optional freshness (recency) and domain filtering.
    """

    def __init__(
        self,
        query: str,
        query_domains: Optional[Sequence[str]] = None,
        freshness: Optional[str] = None,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        headers: Optional[dict] = None,
        recency: Optional[str] = None,
    ):
        """
        Initialize the BraveSearch retriever.

        Args:
            query: The search query string.
            query_domains: Optional list of domains to restrict results (site: filter).
            freshness: Optional recency filter: 'pd' (day), 'pw' (week), 'pm' (month),
                'py' (year), or 'YYYY-MM-DDtoYYYY-MM-DD'.
            country: Optional 2-letter country code (e.g. 'US', 'DE').
            search_lang: Optional ISO language code for results (e.g. 'en', 'de').
            headers: Optional dict; if it contains 'brave_api_key' that overrides env.
            recency: Optional shared RECENCY value (same as freshness); overrides freshness if set.
        """
        self.query = query
        self.query_domains = query_domains or None
        recency = recency or (headers.get("recency") if isinstance(headers, dict) else None)
        self.freshness = _parse_freshness(freshness or recency)
        self.country = country
        self.search_lang = search_lang
        self._headers = headers or {}
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> str:
        key = self._headers.get("brave_api_key")
        if key:
            return key
        key = os.environ.get("BRAVE_API_KEY") or os.environ.get("BRAVE_SEARCH_API_KEY")
        if not key:
            logger.warning(
                "Brave API key not found. Set BRAVE_API_KEY or BRAVE_SEARCH_API_KEY."
            )
            return ""
        return key

    def search(self, max_results: int = 10) -> List[dict]:
        """
        Run the search and return results in the standard format.

        Returns:
            List of dicts with 'title', 'href', 'body' (and optionally 'age').
        """
        if not self.api_key:
            logger.error("Brave API key missing; returning empty results.")
            return []

        query = self.query
        if self.query_domains:
            site_filter = " OR ".join(f"site:{d.strip()}" for d in self.query_domains)
            query = f"{query} ({site_filter})"

        params: dict = {
            "q": query,
            "count": min(max(1, max_results), 20),
        }
        if self.freshness:
            params["freshness"] = self.freshness
        if self.country:
            params["country"] = self.country
        if self.search_lang:
            params["search_lang"] = self.search_lang

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }

        try:
            resp = requests.get(
                BRAVE_WEB_SEARCH_URL,
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error("Brave Search API request failed: %s", e)
            return []

        results = data.get("web", {}).get("results") or []
        search_response = []
        for entry in results:
            search_response.append({
                "title": entry.get("title") or "",
                "href": entry.get("url") or "",
                "body": entry.get("description") or "",
            })
        return search_response
