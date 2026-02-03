"""On-prem RAG API retriever for GPT Researcher (Dex-researcher).

Queries an external RAG service (POST /query) and returns chunks in the
same shape as web retrievers, with source_type 'rag' and citation fields.
"""

import os
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class RAGSearch:
    """
    On-prem RAG API retriever. Calls RAG_API_URL/query and maps response
    to the standard retriever format with citation metadata.
    """

    def __init__(self, query, headers=None, topic="general", query_domains=None):
        self.query = query
        self.headers = headers or {}
        self.topic = topic
        self.query_domains = query_domains or None
        self.base_url = os.environ.get("RAG_API_URL", "").rstrip("/")
        self.api_key = os.environ.get("RAG_API_KEY", "")

    def search(self, max_results=10):
        """
        Query the RAG API and return results in the same shape as Tavily:
        list of dicts with href, body, and for RAG: source_type, doc_id, doc_title, location, chunk_id.
        """
        if not self.base_url:
            logger.warning("RAG_API_URL not set; skipping RAG search.")
            return []

        url = f"{self.base_url}/query"
        payload = {"query": self.query, "top_k": max_results}
        req_headers = {"Content-Type": "application/json"}
        if self.api_key:
            req_headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(url, json=payload, headers=req_headers, timeout=60)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.warning("RAG API request failed: %s. Returning empty RAG results.", e)
            return []

        chunks = data.get("chunks") or []
        search_response = []
        for c in chunks:
            doc_id = c.get("doc_id", "")
            doc_title = c.get("doc_title", doc_id)
            location = c.get("location", "")
            chunk_id = c.get("chunk_id", "")
            text = c.get("text", "")
            href = f"corpus://{doc_id}#{location}" if doc_id else f"corpus://chunk#{chunk_id}"
            search_response.append({
                "href": href,
                "body": text,
                "source_type": "rag",
                "doc_id": doc_id,
                "doc_title": doc_title,
                "location": location,
                "chunk_id": chunk_id,
            })
        return search_response
