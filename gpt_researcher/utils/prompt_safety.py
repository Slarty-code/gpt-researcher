"""
Prompt injection detection and sanitization for report generation and RAG.

Implements pattern-based detection as recommended in the security planning report
(Section 7: Injection Defense Design). Used before sending user/context content
to the LLM and before loading content into the vector store.
"""
import re
from typing import Tuple

# Patterns that may indicate prompt injection or unsafe instructions.
# Matched case-insensitively; keep phrases distinct to reduce false positives.
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"disregard\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"forget\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"override\s+(your\s+)?(system|initial)\s+instructions",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"show\s+(your\s+)?(system\s+)?prompt",
    r"output\s+(your\s+)?(system\s+)?prompt",
    r"retrieve\s+(local\s+)?(files?|env|environment)",
    r"read\s+(local\s+)?(files?|env|environment)",
    r"access\s+(local\s+)?(files?|env|environment)",
    r"api\s+key|apikey|api_key",
    r"secret\s+(key|token|password)",
    r"environment\s+variable|env\s+var",
    r"\.env\s+file|/etc/passwd",
    r"execute\s+(arbitrary\s+)?(command|code|shell)",
    r"run\s+(arbitrary\s+)?(command|code|shell)",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


class PromptInjectionRefusal(Exception):
    """Raised when injection is detected and refuse_on_detection is True."""

    pass


def scan_user_content(
    content: str,
    *,
    refuse_on_detection: bool = False,
    redact_with: str = "[REDACTED]",
) -> Tuple[str, bool]:
    """
    Scan content for known prompt-injection patterns.

    Args:
        content: User or context string to scan.
        refuse_on_detection: If True, raise PromptInjectionRefusal when a pattern matches.
        redact_with: String to replace matched spans with when redacting (used when refuse_on_detection is False).

    Returns:
        (safe_content, was_modified): safe_content is either redacted content or original; was_modified is True if any redaction occurred.

    Raises:
        PromptInjectionRefusal: When refuse_on_detection is True and a pattern matches.
    """
    if not content or not isinstance(content, str):
        return content or "", False

    modified = False
    result = content

    for pattern in _COMPILED_PATTERNS:
        for match in pattern.finditer(result):
            if refuse_on_detection:
                raise PromptInjectionRefusal(
                    "Prompt injection pattern detected; generation refused for safety."
                )
            result = result[: match.start()] + redact_with + result[match.end() :]
            modified = True

    return result, modified


def normalize_for_rag(text: str) -> str:
    """
    Lightweight normalization before indexing: strip null bytes and trim excessive whitespace.
    Reduces hidden-character and whitespace-stuffing attacks.
    """
    if not text or not isinstance(text, str):
        return text or ""
    text = text.replace("\x00", "").strip()
    return re.sub(r"\s+", " ", text).strip()


def sanitize_documents_for_rag(documents: list) -> list:
    """
    Sanitize document content before indexing (report §4.4 RAG poisoning).
    Runs injection-pattern scan (redact) and normalize_for_rag on each item's text field.
    Expects list of dicts with 'raw_content' (or 'page_content') and preserves other keys.
    """
    if not documents:
        return documents
    result = []
    for item in documents:
        if not isinstance(item, dict):
            result.append(item)
            continue
        item = dict(item)
        text = item.get("raw_content", item.get("page_content", ""))
        if text and isinstance(text, str):
            safe, _ = scan_user_content(text, refuse_on_detection=False)
            item["raw_content"] = normalize_for_rag(safe)
            if "page_content" in item:
                item["page_content"] = normalize_for_rag(safe)
        result.append(item)
    return result
