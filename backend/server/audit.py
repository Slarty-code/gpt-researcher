"""
Dex-researcher audit: persist per-run audit records.

Writes to file (JSONL), or optionally DB/Phoenix based on AUDIT_STORAGE.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _sources_used_from_context(context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build sources_used list from researcher context (list of dicts with href, body, source_type, etc.)."""
    out = []
    seen = set()
    for item in (context or []):
        if not isinstance(item, dict):
            continue
        st = item.get("source_type", "web")
        if st == "rag":
            doc_id = item.get("doc_id", "")
            doc_title = item.get("doc_title", "")
            location = item.get("location", "")
            chunk_id = item.get("chunk_id", "")
            key = (doc_id, location)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "type": "rag",
                "doc_id": doc_id,
                "doc_title": doc_title,
                "location": location,
                "chunk_id": chunk_id or None,
            })
        else:
            url = item.get("href", "")
            if url and url not in seen:
                seen.add(url)
                out.append({"type": "web", "url": url, "title": item.get("title")})
    return out


def build_audit_record(
    run_id: str,
    query: str,
    mode: str,
    timestamp: str,
    context: List[Dict[str, Any]],
    models: Dict[str, str],
    report_id: str = "",
    steps: List[str] = None,
    error: str = None,
    session_id: str = "",
) -> Dict[str, Any]:
    steps = steps or ["plan", "research", "write"]
    return {
        "run_id": run_id,
        "session_id": session_id,
        "timestamp": timestamp,
        "query": query,
        "mode": mode,
        "sources_used": _sources_used_from_context(context),
        "models": models,
        "report_id": report_id,
        "steps": steps,
        "error": error,
    }


def write_audit_record(record: Dict[str, Any]) -> None:
    """Write one audit record according to AUDIT_STORAGE (file, db, phoenix). Also emit structured log."""
    logger.info(
        "research_run_end %s",
        json.dumps(
            {
                "run_id": record.get("run_id"),
                "query": record.get("query", "")[:80],
                "mode": record.get("mode"),
                "sources_count": len(record.get("sources_used", [])),
                "error": record.get("error"),
            },
            ensure_ascii=False,
        ),
    )
    storage = os.environ.get("AUDIT_STORAGE", "file").lower()
    if storage == "file":
        path = os.environ.get("AUDIT_LOG_PATH", "data/audit.jsonl")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning("Audit write failed: %s", e)
    elif storage == "db":
        logger.info("Audit record (db not implemented): run_id=%s", record.get("run_id"))
    elif storage == "phoenix":
        logger.info("Audit record (phoenix not implemented): run_id=%s", record.get("run_id"))
    else:
        logger.warning("Unknown AUDIT_STORAGE=%s; skipping audit write.", storage)
