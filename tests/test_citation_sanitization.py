"""
Tests for citation sanitization: ensure only visited URLs appear in citations
and that the References section is grounded in real URLs (no 404s from hallucination).
"""
import pytest

from gpt_researcher.skills.deep_research import (
    _normalize_url_for_match,
    _sanitize_citations,
)


class TestNormalizeUrlForMatch:
    def test_strips_fragment(self):
        assert _normalize_url_for_match("https://example.com/page#section") == "https://example.com/page"

    def test_strips_trailing_slash(self):
        assert _normalize_url_for_match("https://example.com/page/") == "https://example.com/page"

    def test_lowercases_scheme_and_netloc(self):
        assert _normalize_url_for_match("HTTPS://Example.COM/Path") == "https://example.com/Path"

    def test_empty_path_becomes_slash(self):
        assert _normalize_url_for_match("https://example.com") == "https://example.com/"


class TestSanitizeCitations:
    def test_keeps_exact_match(self):
        allowed = {"https://example.com/a", "https://other.com/b"}
        citations = {"learning1": "https://example.com/a", "learning2": "https://other.com/b"}
        out = _sanitize_citations(citations, allowed)
        assert out == citations

    def test_drops_url_not_in_allowed(self):
        allowed = {"https://example.com/a"}
        citations = {"learning1": "https://example.com/a", "learning2": "https://fake.com/hallucinated"}
        out = _sanitize_citations(citations, allowed)
        assert out == {"learning1": "https://example.com/a"}
        assert "learning2" not in out

    def test_matches_normalized_url(self):
        allowed = {"https://example.com/page/"}
        citations = {"learning1": "https://example.com/page"}
        out = _sanitize_citations(citations, allowed)
        assert out["learning1"] == "https://example.com/page/"

    def test_empty_allowed_returns_empty(self):
        citations = {"learning1": "https://example.com/a"}
        out = _sanitize_citations(citations, set())
        assert out == {}

    def test_skips_empty_url(self):
        allowed = {"https://example.com/a"}
        citations = {"learning1": "https://example.com/a", "learning2": ""}
        out = _sanitize_citations(citations, allowed)
        assert "learning2" not in out
        assert out["learning1"] == "https://example.com/a"
