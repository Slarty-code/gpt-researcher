"""Maximal Marginal Relevance (MMR) re-ranking for context selection.

MMR balances relevance with diversity by iteratively selecting items that
maximize: λ * relevance - (1-λ) * max_similarity_to_selected.

See Carbonell & Goldstein, "The Use of MMR, Diversity-Based Reranking" (1998).
"""

import os
import re
from typing import Generic, List, TypeVar

# Default: opt-in, lambda 0.7 (slight bias to relevance)
DEFAULT_MMR_LAMBDA = 0.7


def _tokenize(text: str) -> set:
    """Tokenize for Jaccard: alphanumeric + underscore, lowercased."""
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    return set(tokens)


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two token sets; returns value in [0, 1]."""
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def text_similarity(content_a: str, content_b: str) -> float:
    """Similarity between two content strings using Jaccard on tokens."""
    return jaccard_similarity(_tokenize(content_a), _tokenize(content_b))


def compute_mmr_score(relevance: float, max_similarity: float, lambda_: float) -> float:
    """MMR score = λ * relevance - (1-λ) * max_similarity_to_selected."""
    return lambda_ * relevance - (1.0 - lambda_) * max_similarity


T = TypeVar("T")


class MMRItem(Generic[T]):
    """Item with id, score (relevance), and content for MMR."""

    __slots__ = ("id", "score", "content", "item")

    def __init__(self, id: str, score: float, content: str, item: T = None):
        self.id = id
        self.score = score
        self.content = content
        self.item = item


def mmr_rerank(
    items: List[MMRItem[T]],
    lambda_: float = DEFAULT_MMR_LAMBDA,
) -> List[MMRItem[T]]:
    """
    Re-rank items by MMR: balance relevance and diversity.

    Args:
        items: List of MMRItem (id, score, content, optional wrapped item).
        lambda_: 0 = max diversity, 1 = max relevance. Clamped to [0, 1].

    Returns:
        New list of same items in MMR order.
    """
    if len(items) <= 1:
        return list(items)

    lam = max(0.0, min(1.0, lambda_))
    if lam == 1.0:
        return sorted(items, key=lambda x: -x.score)

    # Pre-tokenize
    token_cache: dict[str, set] = {}
    for it in items:
        token_cache[it.id] = _tokenize(it.content)

    # Normalize scores to [0, 1]
    scores = [it.score for it in items]
    lo, hi = min(scores), max(scores)
    span = hi - lo
    if span == 0:
        span = 1.0

    def norm(s: float) -> float:
        return (s - lo) / span

    selected: List[MMRItem[T]] = []
    remaining = set(items)

    while remaining:
        best_item = None
        best_mmr = -float("inf")
        for candidate in remaining:
            rel = norm(candidate.score)
            max_sim = 0.0
            for s in selected:
                sim = jaccard_similarity(
                    token_cache[candidate.id],
                    token_cache[s.id],
                )
                if sim > max_sim:
                    max_sim = sim
            mmr = compute_mmr_score(rel, max_sim, lam)
            if mmr > best_mmr or (
                mmr == best_mmr and (best_item is None or candidate.score > best_item.score)
            ):
                best_mmr = mmr
                best_item = candidate
        if best_item is None:
            break
        selected.append(best_item)
        remaining.discard(best_item)

    return selected


def rerank_documents_by_mmr(
    docs: list,
    content_key: str = "page_content",
    id_key: str = "id",
    score_from_rank: bool = True,
    lambda_: float = DEFAULT_MMR_LAMBDA,
) -> list:
    """
    Re-rank a list of document-like objects (e.g. LangChain Document) using MMR.

    Args:
        docs: List of objects with page_content (or content_key) and optional metadata.
        content_key: Attribute name for text content (default 'page_content').
        id_key: Attribute in metadata for id, or use index.
        score_from_rank: If True, relevance = 1 - (rank / n); else use doc.get('score', 1).
        lambda_: MMR lambda.

    Returns:
        Same docs in MMR order.
    """
    if not docs or len(docs) <= 1:
        return docs

    mmr_items: List[MMRItem] = []
    for i, doc in enumerate(docs):
        content = getattr(doc, content_key, None) or getattr(doc, "page_content", "") or ""
        meta = getattr(doc, "metadata", None) or {}
        uid = meta.get(id_key) or str(i)
        if score_from_rank:
            score = 1.0 - (i / max(len(docs), 1))
        else:
            score = float(getattr(doc, "score", meta.get("score", 1.0)))
        mmr_items.append(MMRItem(id=uid, score=score, content=content, item=doc))

    reranked = mmr_rerank(mmr_items, lambda_=lambda_)
    return [m.item for m in reranked]


def is_mmr_enabled() -> bool:
    """True if ENABLE_MMR_RERANK is set to a truthy value."""
    return os.environ.get("ENABLE_MMR_RERANK", "").strip().lower() in ("1", "true", "yes")


def get_mmr_lambda() -> float:
    """MMR lambda from MMR_LAMBDA env (default 0.7)."""
    try:
        return float(os.environ.get("MMR_LAMBDA", DEFAULT_MMR_LAMBDA))
    except ValueError:
        return DEFAULT_MMR_LAMBDA
