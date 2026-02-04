"""
Dex-researcher RAG API service.

Exposes POST /query and POST /ingest with the minimal contract expected by the
GPT Researcher RAG retriever. Uses LightRAG when LIGHTRAG_WORKING_DIR is set
and lightrag-hku is installed (with embedding_func and llm_model_func from env);
otherwise returns empty chunks (stub mode).
"""

import asyncio
import os
import logging
from contextlib import asynccontextmanager
from functools import partial


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LightRAG instance (set at startup in lifespan)
_rag = None

# Default storage backends (file-based; overridable via env for future PostgreSQL/Neo4j)
DEFAULT_KV_STORAGE = "JsonKVStorage"
DEFAULT_VECTOR_STORAGE = "NanoVectorDBStorage"
DEFAULT_GRAPH_STORAGE = "NetworkXStorage"
DEFAULT_DOC_STATUS_STORAGE = "JsonDocStatusStorage"


def _make_embedding_func():
    """Build LightRAG EmbeddingFunc from env: RAG_EMBEDDING_PROVIDER (ollama|openai), etc."""
    try:
        from lightrag.utils import EmbeddingFunc
    except ImportError:
        return None
    provider = (os.environ.get("RAG_EMBEDDING_PROVIDER") or "ollama").strip().lower()
    embedding_dim = int(os.environ.get("RAG_EMBEDDING_DIM", "0") or "0")
    max_token_size = int(os.environ.get("RAG_EMBEDDING_MAX_TOKEN_SIZE", "8192") or "8192")

    if provider == "ollama":
        try:
            from lightrag.llm import ollama_embed
        except ImportError:
            try:
                from lightrag.llm import ollama_embedding as ollama_embed
            except ImportError:
                logger.warning("Ollama embedding not available in lightrag.llm")
                return None
        model = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        host = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        if not embedding_dim:
            embedding_dim = 768
        return EmbeddingFunc(embedding_dim=embedding_dim, max_token_size=max_token_size, func=lambda texts: _run_async(ollama_embed, texts, model, host))
    elif provider == "openai":
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        if not embedding_dim:
            embedding_dim = 1536
        if not api_key:
            logger.warning("OPENAI_API_KEY not set; OpenAI embedding disabled.")
            return None
        return EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=max_token_size,
            func=lambda texts: _openai_embed(texts, base_url=base_url, api_key=api_key, model=model),
        )
    logger.warning("Unknown RAG_EMBEDDING_PROVIDER=%s", provider)
    return None


async def _run_async(ollama_embed_fn, texts, model, host):
    """Run Ollama embed (sync or async) in async context."""
    if hasattr(ollama_embed_fn, "func"):
        ollama_embed_fn = ollama_embed_fn.func
    import asyncio
    fn = getattr(ollama_embed_fn, "__call__", ollama_embed_fn)
    if asyncio.iscoroutinefunction(fn):
        return await fn(texts, embed_model=model, host=host)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: fn(texts, embed_model=model, host=host))


async def _openai_embed(texts, *, base_url, api_key, model):
    """OpenAI-compatible embeddings via httpx."""
    import httpx
    import numpy as np
    if not texts:
        return np.array([], dtype=np.float32)
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            f"{base_url}/embeddings",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"input": texts, "model": model},
        )
        r.raise_for_status()
        data = r.json()
    out = [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]
    return np.array(out, dtype=np.float32)


def _make_llm_model_func():
    """Build LightRAG llm_model_func from env: RAG_LLM_PROVIDER (ollama|openai), etc."""
    provider = (os.environ.get("RAG_LLM_PROVIDER") or "ollama").strip().lower()
    if provider == "ollama":
        try:
            from lightrag.llm import ollama_model_complete
        except ImportError:
            logger.warning("ollama_model_complete not found in lightrag.llm")
            return None
        model = os.environ.get("OLLAMA_LLM_MODEL", "llama3.2")
        host = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        return partial(ollama_model_complete.func if hasattr(ollama_model_complete, "func") else ollama_model_complete, model=model, host=host)
    elif provider == "openai":
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        api_key = os.environ.get("OPENAI_API_KEY", "")
        model = os.environ.get("OPENAI_LLM_MODEL", "gpt-4o-mini")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set; OpenAI LLM disabled.")
            return None
        return partial(_openai_complete, base_url=base_url, api_key=api_key, model=model)
    return None


async def _openai_complete(prompt, *, system_prompt=None, history_messages=None, base_url, api_key, model, hashing_kv=None, **kwargs):
    """OpenAI-compatible chat completion for LightRAG LLM calls."""
    import httpx
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    max_tokens = kwargs.get("max_tokens") or 2048
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "max_tokens": max_tokens},
        )
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]["content"]


def _create_rag():
    """Create and return a LightRAG instance (storages not yet initialized). Returns None if disabled or import fails."""
    working_dir = os.environ.get("LIGHTRAG_WORKING_DIR")
    if not working_dir:
        return None
    try:
        from lightrag import LightRAG
    except ImportError:
        logger.warning("lightrag-hku not installed; RAG will return empty results.")
        return None
    embedding_func = _make_embedding_func()
    llm_model_func = _make_llm_model_func()
    if not embedding_func or not llm_model_func:
        logger.warning("RAG disabled: embedding_func or llm_model_func not available (check RAG_* and OLLAMA_*/OPENAI_* env).")
        return None
    kv = os.environ.get("LIGHTRAG_KV_STORAGE", DEFAULT_KV_STORAGE)
    vec = os.environ.get("LIGHTRAG_VECTOR_STORAGE", DEFAULT_VECTOR_STORAGE)
    graph = os.environ.get("LIGHTRAG_GRAPH_STORAGE", DEFAULT_GRAPH_STORAGE)
    doc_status = os.environ.get("LIGHTRAG_DOC_STATUS_STORAGE", DEFAULT_DOC_STATUS_STORAGE)
    rag = LightRAG(
        working_dir=working_dir,
        embedding_func=embedding_func,
        llm_model_func=llm_model_func,
        kv_storage=kv,
        vector_storage=vec,
        graph_storage=graph,
        doc_status_storage=doc_status,
    )
    logger.info("LightRAG created with working_dir=%s (storages: kv=%s, vector=%s, graph=%s)", working_dir, kv, vec, graph)
    return rag


def get_rag():
    """Return the global LightRAG instance (set at startup)."""
    return _rag


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


# Ingest limits (MVP: avoid OOM)
INGEST_MAX_DOCUMENTS = int(os.environ.get("RAG_INGEST_MAX_DOCUMENTS", "300"))
INGEST_MAX_PAYLOAD_BYTES = int(os.environ.get("RAG_INGEST_MAX_PAYLOAD_BYTES", "10_000_000"))


class IngestRequest(BaseModel):
    documents: list[str] = Field(..., description="List of document text contents to index")
    file_paths: list[str] | None = Field(default=None, description="Optional paths for citation (same length as documents)")
    ids: list[str] | None = Field(default=None, description="Optional document IDs (same length as documents)")


class IngestResponse(BaseModel):
    track_id: str = Field(..., description="Tracking ID for this ingest batch")
    documents_accepted: int = Field(..., description="Number of documents enqueued")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _rag
    _rag = _create_rag()
    if _rag is not None:
        try:
            await _rag.initialize_storages()
            logger.info("RAG backend ready (LightRAG).")
        except Exception as e:
            logger.exception("LightRAG initialize_storages failed: %s", e)
            _rag = None
    else:
        logger.info("RAG backend: stub mode (no index). Set LIGHTRAG_WORKING_DIR and install lightrag-hku with embedding/LLM env for real retrieval.")
    yield
    if _rag is not None:
        try:
            await _rag.finalize_storages()
            logger.info("LightRAG storages finalized.")
        except Exception as e:
            logger.exception("LightRAG finalize_storages failed: %s", e)
        _rag = None


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
        # LightRAG.query may be sync; run in thread to avoid blocking the event loop
        result = await asyncio.to_thread(rag.query, req.query, param=param)
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


@app.post("/ingest", response_model=IngestResponse, status_code=202)
async def ingest(req: IngestRequest):
    """Ingest documents into the RAG index. Processing is async; use track_id to monitor status."""
    rag = get_rag()
    if rag is None:
        raise HTTPException(status_code=503, detail="RAG backend not available (stub mode or not configured).")
    if not req.documents:
        raise HTTPException(status_code=400, detail="documents must not be empty.")
    if len(req.documents) > INGEST_MAX_DOCUMENTS:
        raise HTTPException(
            status_code=413,
            detail=f"Too many documents: {len(req.documents)} (max {INGEST_MAX_DOCUMENTS}).",
        )
    payload_bytes = sum(len(d.encode("utf-8")) for d in req.documents)
    if payload_bytes > INGEST_MAX_PAYLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Payload too large: {payload_bytes} bytes (max {INGEST_MAX_PAYLOAD_BYTES}).",
        )
    if req.file_paths is not None and len(req.file_paths) != len(req.documents):
        raise HTTPException(status_code=400, detail="file_paths length must match documents length.")
    if req.ids is not None and len(req.ids) != len(req.documents):
        raise HTTPException(status_code=400, detail="ids length must match documents length.")
    try:
        track_id = await rag.ainsert(
            input=req.documents,
            file_paths=req.file_paths,
            ids=req.ids,
        )
        return IngestResponse(track_id=track_id, documents_accepted=len(req.documents))
    except Exception as e:
        logger.exception("Ingest failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "backend": "lightrag" if get_rag() else "stub"}
