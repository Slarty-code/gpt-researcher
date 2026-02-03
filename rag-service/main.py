"""
Dex-researcher RAG API service.

Exposes POST /query with the minimal contract expected by the GPT Researcher
RAG retriever. Use LightRAG when LIGHTRAG_WORKING_DIR is set and lightrag-hku
is installed; otherwise returns empty chunks (for pipeline testing).
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional: LightRAG instance (lazy init)
_rag = None


def get_rag():
    global _rag
    if _rag is not None:
        return _rag
    working_dir = os.environ.get("LIGHTRAG_WORKING_DIR")
    if not working_dir:
        return None
    try:
        from lightrag import LightRAG, QueryParam
        _rag = LightRAG(working_dir=working_dir)
        logger.info("LightRAG initialized with working_dir=%s", working_dir)
        return _rag
    except ImportError:
        logger.warning("lightrag-hku not installed; RAG will return empty results.")
        return None


class QueryRequest(BaseModel):
    query: str = Field(..., description="Research question or query text")
    top_k: int = Field(default=10, ge=1, le=50, description="Max chunks to return")


class ChunkOut(BaseModel):
    doc_id: str
    doc_title: str
    location: str
    chunk_id: str
    text: str
    score: float = 0.0


class QueryResponse(BaseModel):
    chunks: list[ChunkOut] = Field(default_factory=list)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if get_rag() is not None:
        logger.info("RAG backend ready (LightRAG).")
    else:
        logger.info("RAG backend: stub mode (no index). Set LIGHTRAG_WORKING_DIR and install lightrag-hku for real retrieval.")
    yield


app = FastAPI(title="Dex-researcher RAG API", lifespan=lifespan)


def _lightrag_to_chunks(result: str, query: str) -> list[dict]:
    """Map LightRAG query result (string) to our chunk schema. LightRAG returns generated text; we treat it as one chunk for MVP."""
    chunks = []
    if not result or not result.strip():
        return chunks
    # LightRAG may return a single string; we don't have per-chunk metadata in that case.
    # Use a single synthetic chunk so the pipeline gets something.
    chunks.append(ChunkOut(
        doc_id="lightrag",
        doc_title="Corpus",
        location="retrieval",
        chunk_id="0",
        text=result.strip()[:8000],
        score=1.0,
    ))
    return chunks


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Query the RAG index. Returns chunks with doc_id, doc_title, location, chunk_id, text, score."""
    rag = get_rag()
    if rag is None:
        return QueryResponse(chunks=[])

    try:
        from lightrag import QueryParam
        param = QueryParam(mode="hybrid")
        result = rag.query(req.query, param=param)
    except Exception as e:
        logger.exception("LightRAG query failed: %s", e)
        return QueryResponse(chunks=[])

    if result is None:
        return QueryResponse(chunks=[])
    if isinstance(result, str):
        chunk_list = _lightrag_to_chunks(result, req.query)
    elif isinstance(result, list):
        chunk_list = []
        for i, item in enumerate(result[: req.top_k]):
            if isinstance(item, dict):
                chunk_list.append(ChunkOut(
                    doc_id=item.get("doc_id", ""),
                    doc_title=item.get("doc_title", "Corpus"),
                    location=item.get("location", ""),
                    chunk_id=item.get("chunk_id", str(i)),
                    text=item.get("text", str(item))[:8000],
                    score=float(item.get("score", 0)),
                ))
            else:
                chunk_list.append(ChunkOut(doc_id="", doc_title="", location="", chunk_id=str(i), text=str(item)[:8000], score=0.0))
    else:
        chunk_list = _lightrag_to_chunks(str(result), req.query)

    return QueryResponse(chunks=chunk_list[: req.top_k])


@app.get("/health")
async def health():
    return {"status": "ok", "backend": "lightrag" if get_rag() else "stub"}
