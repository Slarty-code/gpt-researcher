"""
Tests for the rag-service FastAPI app (POST /query, POST /ingest, GET /health).

When LIGHTRAG_WORKING_DIR is unset or lightrag-hku is not installed, the service
runs in stub mode (empty chunks, 503 on ingest). These tests pass in that case.
Optional: skip or extend tests that require a live RAG backend when API keys or
Ollama are unavailable.
"""

import os
import sys

import pytest

# Add rag-service to path so we can import main
_rag_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag-service"))
if _rag_service_dir not in sys.path:
    sys.path.insert(0, _rag_service_dir)

# TestClient + lifespan can trigger "I/O operation on closed file" on Windows; run on Linux/CI
_skip_rag_tests = sys.platform == "win32"


@pytest.fixture
def rag_app():
    import main as rag_main
    return rag_main.app


@pytest.fixture
def rag_client(rag_app):
    from fastapi.testclient import TestClient
    client = TestClient(rag_app)
    yield client
    client.close()


@pytest.mark.skipif(_skip_rag_tests, reason="RAG service TestClient/lifespan can close stderr on Windows; run on Linux/CI")
class TestRagService:
    """Grouped so skipif applies to all."""


    def test_health_returns_ok(self, rag_client):
        r = rag_client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["backend"] in ("stub", "lightrag")

    def test_query_returns_chunks_structure(self, rag_client):
        r = rag_client.post("/query", json={"query": "test", "top_k": 5})
        assert r.status_code == 200
        data = r.json()
        assert "chunks" in data
        assert isinstance(data["chunks"], list)
        # Stub mode returns empty chunks
        if data["chunks"]:
            for c in data["chunks"]:
                assert "doc_id" in c and "text" in c and "doc_title" in c

    def test_ingest_stub_returns_503_or_valid(self, rag_client):
        """Without RAG backend, POST /ingest returns 503. With backend, 202."""
        r = rag_client.post("/ingest", json={"documents": ["short doc"], "file_paths": ["/path/to/doc.txt"]})
        if r.status_code == 503:
            assert "not available" in r.json().get("detail", "").lower() or "stub" in r.json().get("detail", "").lower()
            return
        assert r.status_code == 202
        data = r.json()
        assert "track_id" in data
        assert data.get("documents_accepted") == 1

    def test_ingest_empty_documents_rejected(self, rag_client):
        r = rag_client.post("/ingest", json={"documents": []})
        assert r.status_code == 400

    def test_ingest_mismatched_file_paths_rejected(self, rag_client):
        r = rag_client.post(
            "/ingest",
            json={"documents": ["a", "b"], "file_paths": ["only_one_path"]},
        )
        assert r.status_code == 400
