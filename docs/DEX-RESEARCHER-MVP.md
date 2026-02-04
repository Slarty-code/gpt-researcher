# Dex-researcher MVP

This document describes the Dex-researcher MVP: GPT Researcher with OpenRouter, on-prem RAG, reliable citations, audit trail, structured logging, and private mode.

## Environment variables

| Variable | Description |
|----------|-------------|
| **OpenRouter** | |
| `OPENROUTER_API_KEY` | API key for OpenRouter (required for inference when using openrouter provider). |
| `OPENROUTER_BASE_URL` | Base URL (default `https://openrouter.ai/api/v1`). Set to on-prem gateway URL in private mode. |
| **LLM config** | Use `FAST_LLM=openrouter:openai/gpt-4o-mini`, `SMART_LLM=openrouter:...`, `STRATEGIC_LLM=openrouter:...` to route all chat through OpenRouter. |
| **RAG** | |
| `RAG_API_URL` | On-prem RAG service URL (e.g. `http://localhost:8001` or `http://rag-service:8000` in Docker). |
| `RAG_API_KEY` | Optional auth header for RAG API. |
| **RAG service (rag-service)** | |
| `LIGHTRAG_WORKING_DIR` | Directory for LightRAG file-based storage (required for real RAG). |
| `RAG_EMBEDDING_PROVIDER` | `ollama` or `openai`. |
| `RAG_LLM_PROVIDER` | `ollama` or `openai`. |
| `OLLAMA_BASE_URL` | Ollama API URL (default `http://localhost:11434`). |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model name (default `nomic-embed-text`). |
| `OLLAMA_LLM_MODEL` | LLM model for entity/relation extraction (default `llama3.2`). |
| `OPENAI_API_KEY` | Required when using OpenAI for embedding/LLM. |
| `OPENAI_BASE_URL` | OpenAI-compatible API URL (default `https://api.openai.com/v1`). |
| `OPENAI_EMBEDDING_MODEL` | Embedding model (default `text-embedding-3-small`). |
| `OPENAI_LLM_MODEL` | LLM model (default `gpt-4o-mini`). |
| `RAG_EMBEDDING_DIM` | Optional; override embedding dimension (e.g. 768 for nomic, 1536 for OpenAI small). |
| `RAG_INGEST_MAX_DOCUMENTS` | Max documents per POST /ingest (default 300). |
| `RAG_INGEST_MAX_PAYLOAD_BYTES` | Max request body size for ingest (default 10M). |
| `LIGHTRAG_KV_STORAGE` | LightRAG KV backend (default `JsonKVStorage`). |
| `LIGHTRAG_VECTOR_STORAGE` | LightRAG vector backend (default `NanoVectorDBStorage`). |
| `LIGHTRAG_GRAPH_STORAGE` | LightRAG graph backend (default `NetworkXStorage`). |
| `LIGHTRAG_DOC_STATUS_STORAGE` | LightRAG doc-status backend (default `JsonDocStatusStorage`). |
| **Retrievers** | Set `RETRIEVER=tavily,rag` to use both web search and RAG; in private mode only RAG is used. |
| **Private mode** | |
| `PRIVATE_MODE` | Set to `true` or `1` to disable external search and use only on-prem RAG (and on-prem LLM via `OPENROUTER_BASE_URL`). |
| **Audit / logging** | |
| `AUDIT_STORAGE` | `file` (default), `db`, or `phoenix`. Where the per-run audit record is written. |
| `AUDIT_LOG_PATH` | When `AUDIT_STORAGE=file`, path for JSONL file (default `data/audit.jsonl`). |
| `DOC_PATH` | Folder(s) for local documents (non-RAG). Use a single path or comma-separated (e.g. `C:\docs,D:\docs`). |

## DOC_PATH and per-run override

- **`_set_doc_path`** is an internal config method: it runs when the app loads config and sets `doc_path` from `DOC_PATH` (env or config file). It is not a user-facing API or UI control.
- **Multiple folders:** Set `DOC_PATH=C:\docs,D:\docs` (comma-separated) to load local documents from both folders for the non-RAG pathway (Local / Hybrid report source).
- **Override from UI/API:** The WebSocket "start" message can include an optional **`doc_path`** field. When present, that run uses the given path(s) instead of the global `DOC_PATH`. So a UI can let users choose or type a doc path for that research run. Values:
  - **String:** one path, or comma-separated paths (e.g. `"C:\\docs,D:\\docs"`).
  - **Array:** list of path strings (e.g. `["C:\\docs", "D:\\docs"]`).
- **Programmatic override:** Code that holds a `Config` instance can call **`cfg.set_doc_path(path_or_paths)`** to update doc path at runtime (e.g. before starting a researcher) with a string, comma-separated string, or list of paths.

## Running with OpenRouter only

1. Set `OPENROUTER_API_KEY` and in `.env` or env set:
   - `FAST_LLM=openrouter:openai/gpt-4o-mini`
   - `SMART_LLM=openrouter:openai/gpt-4o-mini`
   - `STRATEGIC_LLM=openrouter:openai/gpt-4o-mini`
2. Do not set `OPENAI_API_KEY` (or leave empty) so all calls go through OpenRouter.

## Running with RAG

1. **Use the project venv** so `lightrag-hku` and other deps are available: activate the repo venv (e.g. `source .venv/bin/activate` or `.venv\Scripts\activate`), then install if needed with `pip install -r requirements.txt` or `uv sync` / `poetry install` from the repo root.
2. Start the RAG service from the repo root with the venv active: `cd rag-service && uvicorn main:app --host 0.0.0.0 --port 8001` (or use Docker profile `rag`).
3. Set `RAG_API_URL=http://localhost:8001` and `RETRIEVER=tavily,rag`.
4. For RAG-only (no web), set `RETRIEVER=rag`.

## RAG ingest and DOC_PATH sync

- **POST /ingest**: The RAG service exposes `POST /ingest` with a JSON body: `documents` (list of document text strings), optional `file_paths` (same length as documents, for citation), optional `ids`. The service enqueues documents for LightRAG processing and returns `202 Accepted` with `track_id` and `documents_accepted`. Limits (configurable via env): default max 300 documents per request and 10 MB payload.
- **Ingest script**: Use `rag-service/ingest_from_path.py` to index a directory into the RAG service. Run from repo root: `python rag-service/ingest_from_path.py /path/to/corpus` or set `DOC_PATH` and run `python rag-service/ingest_from_path.py`. The script discovers files (by default .txt, .md, .html, .htm; with optional langchain loaders from repo venv also .pdf, .doc, .docx, etc.), sends them to `RAG_API_URL/ingest`, and batches requests.
- **Pilot sync**: For the pilot, DOC_PATH (or your corpus path) and the RAG index stay in sync by **running the ingest script or calling POST /ingest when you add or update documents**. There is no automatic file watcher or cron in the MVP; run ingest after changing the corpus.

## Private mode

1. Set `PRIVATE_MODE=true`.
2. Set `OPENROUTER_BASE_URL` to your on-prem LLM gateway (or use a local model provider).
3. Set `RAG_API_URL` to your on-prem RAG service.
4. Only RAG and the configured LLM are used; no Tavily or other external APIs.

## Audit and logs

- Each run gets a `run_id` (UUID) and a timestamp. At the end of the run, an audit record is written.
- With `AUDIT_STORAGE=file` (default), records are appended to `AUDIT_LOG_PATH` (default `data/audit.jsonl`) as one JSON object per line.
- Structured log lines `research_run_start` and `research_run_end` are emitted with run_id, query, mode, and source count.

## Citation schema (corpus sources)

Corpus (RAG) sources are cited in the report as: `[Source: doc_title, location]`. The report prompt instructs the model to use this format for any claim from a "Corpus source".

## Reliable citations (web)

To avoid 404s and hallucinated links, web reports use citation link verification:

- **Deep Research:** Citations extracted from the LLM (learnings and source URLs) are sanitized so only URLs that were actually visited during research are kept; any other URL is dropped or matched to a visited URL by normalization (fragment, trailing slash).
- **Report generation:** When writing the report, the model receives the list of allowed (visited) URLs and is instructed to use only those for in-text citations.
- **References section:** For Summary and Deep web reports, a programmatic "## References" section is appended after the report, built from `visited_urls`, so the reference list contains only real, visited URLs.

Result: links in the citation section and reference list point to pages that were actually fetched during research.

## Testing checklist

1. **OpenRouter only**: Run a research query with only OpenRouter configured; confirm report is generated and audit/log shows the OpenRouter model.
2. **RAG only**: Set `RETRIEVER=rag`, run with RAG service; report should include corpus-derived content and citations `[Source: doc_title, location]`.
3. **Web + RAG**: Set `RETRIEVER=tavily,rag`; report should cite both web and corpus; audit `sources_used` should contain both types.
4. **Private mode**: Set `PRIVATE_MODE=true`, run a query; verify no calls to Tavily or public OpenRouter; audit should show `mode: "private"` and no web sources.
5. **Audit and logs**: For any run, confirm audit record and logs contain `run_id`, `query`, `mode`, `sources_used`, and `models`.
