#!/usr/bin/env python3
"""
Ingest documents from a directory (DOC_PATH or CLI arg) into the RAG service.

Run with the project venv activated (from repo root: .venv\\Scripts\\activate on
Windows, source .venv/bin/activate on Linux/macOS) so dependencies are installed
in the venv. Supported file extensions (plain-text): .txt, .md, .html, .htm.
For PDF, DOC, DOCX, etc., run from the repo root with the project venv so
optional loaders (e.g. PyMuPDF via langchain_community) are available.

Usage:
  DOC_PATH=/path/to/docs python rag-service/ingest_from_path.py
  python rag-service/ingest_from_path.py /path/to/corpus
  python rag-service/ingest_from_path.py --path /path/to/corpus --rag-url http://localhost:8001
  cd rag-service && python ingest_from_path.py /path/to/corpus

Environment:
  DOC_PATH          Default corpus path (if --path not given).
  RAG_API_URL       RAG service base URL (default http://localhost:8001).
  RAG_API_KEY       Optional Bearer token for RAG API.
"""

import argparse
import os
import sys
from pathlib import Path

# Supported extensions for plain-text read (no extra deps)
TEXT_EXTENSIONS = {"txt", "md", "html", "htm"}

# Optional: same set as gpt_researcher/document/document.py when loaders available
EXTENSIONS_WITH_LOADERS = TEXT_EXTENSIONS | {"pdf", "doc", "docx", "pptx", "csv", "xls", "xlsx"}


def _read_file_plain(path: Path) -> str | None:
    """Read file as UTF-8 text. Returns None on error."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _load_with_loader(file_path: Path) -> str | None:
    """Try to load with langchain-style loaders if available (run from repo root with venv)."""
    try:
        from langchain_community.document_loaders import (
            PyMuPDFLoader,
            TextLoader,
            UnstructuredCSVLoader,
            UnstructuredExcelLoader,
            UnstructuredMarkdownLoader,
            UnstructuredPowerPointLoader,
            UnstructuredWordDocumentLoader,
        )
        from langchain_community.document_loaders import BSHTMLLoader
    except ImportError:
        return None
    ext = file_path.suffix.lower().lstrip(".")
    loaders = {
        "pdf": PyMuPDFLoader,
        "txt": TextLoader,
        "doc": UnstructuredWordDocumentLoader,
        "docx": UnstructuredWordDocumentLoader,
        "pptx": UnstructuredPowerPointLoader,
        "csv": lambda p: UnstructuredCSVLoader(p, mode="elements"),
        "xls": lambda p: UnstructuredExcelLoader(p, mode="elements"),
        "xlsx": lambda p: UnstructuredExcelLoader(p, mode="elements"),
        "md": UnstructuredMarkdownLoader,
        "html": BSHTMLLoader,
        "htm": BSHTMLLoader,
    }
    loader_cls = loaders.get(ext)
    if not loader_cls:
        return None
    try:
        loader = loader_cls(str(file_path))
        docs = loader.load()
        if not docs:
            return None
        return "\n\n".join(d.page_content for d in docs if getattr(d, "page_content", None))
    except Exception:
        return None


def collect_documents(root: Path, use_loaders: bool = True) -> list[tuple[str, str]]:
    """Walk root and return list of (content, file_path_str)."""
    root = root.resolve()
    if not root.is_dir():
        return []
    out: list[tuple[str, str]] = []
    extensions = EXTENSIONS_WITH_LOADERS if use_loaders else TEXT_EXTENSIONS
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower().lstrip(".")
        if ext not in extensions:
            continue
        if ext in TEXT_EXTENSIONS:
            content = _read_file_plain(path)
        else:
            content = _load_with_loader(path) if use_loaders else None
        if content and content.strip():
            out.append((content.strip(), str(path)))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest documents from a path into the RAG service.")
    parser.add_argument("path", nargs="?", default=None, help="Corpus directory (default: DOC_PATH env)")
    parser.add_argument("--rag-url", default=os.environ.get("RAG_API_URL", "http://localhost:8001"), help="RAG service base URL")
    parser.add_argument("--no-loaders", action="store_true", help="Only use plain-text extensions (txt, md, html, htm)")
    parser.add_argument("--batch", type=int, default=100, help="Max documents per POST /ingest request")
    args = parser.parse_args()
    corpus_path = args.path or os.environ.get("DOC_PATH")
    if not corpus_path:
        print("Error: provide path as argument or set DOC_PATH", file=sys.stderr)
        return 1
    path = Path(corpus_path)
    if not path.is_dir():
        print(f"Error: not a directory: {path}", file=sys.stderr)
        return 1
    docs = collect_documents(path, use_loaders=not args.no_loaders)
    if not docs:
        print("No documents found.", file=sys.stderr)
        return 0
    try:
        import httpx
    except ImportError:
        print("Error: httpx required. pip install httpx", file=sys.stderr)
        return 1
    base = args.rag_url.rstrip("/")
    headers = {"Content-Type": "application/json"}
    if os.environ.get("RAG_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ.get('RAG_API_KEY')}"
    total = 0
    for i in range(0, len(docs), args.batch):
        batch = docs[i : i + args.batch]
        documents = [c for c, _ in batch]
        file_paths = [p for _, p in batch]
        try:
            r = httpx.post(
                f"{base}/ingest",
                json={"documents": documents, "file_paths": file_paths},
                headers=headers,
                timeout=60.0,
            )
            r.raise_for_status()
            data = r.json()
            track_id = data.get("track_id", "")
            accepted = data.get("documents_accepted", len(batch))
            total += accepted
            print(f"Accepted {accepted} documents (track_id={track_id})")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} {e.response.text}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Request failed: {e}", file=sys.stderr)
            return 1
    print(f"Total documents enqueued: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
