"""关键词检索（BM25）。

为什么单独一个模块？
    向量检索和关键词检索是两种完全不同的机制，
    分开写、分开测，最后再融合。
"""

from __future__ import annotations

import jieba
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.models import DocumentChunk


def tokenize(text: str) -> list[str]:
    """中文分词。"""
    return [w.strip() for w in jieba.lcut(text) if w.strip()]


def keyword_search(db: Session, question: str, limit: int = 20) -> list[int]:
    """按 BM25 检索，返回 chunk id 列表（按相关度从高到低）。

    ⚠️ 这个实现每次都把所有 chunk 读进内存 —— 只适合小规模。
       生产上要用 Elasticsearch 之类专门做这件事。
    """
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.content.isnot(None))
        .all()
    )
    if not chunks:
        return []

    corpus = [tokenize(c.content) for c in chunks]
    bm25 = BM25Okapi(corpus)

    scores = bm25.get_scores(tokenize(question))

    ranked = sorted(
        zip(chunks, scores),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [c.id for c, s in ranked[:limit] if s > 0]