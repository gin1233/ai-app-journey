"""RAG：检索 + 生成。

这个模块把 Day 17 的"检索"和 Day 10 的"生成"接起来。
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.services.embeddings import embed_texts
from app.services.llm import chat
from app.services.keyword_search import keyword_search

# 低于这个分数就认为"没有相关内容"
MIN_SCORE = 0.35

RAG_SYSTEM = """你是一个严谨的知识库助手。

规则：
1. 只根据【参考资料】里的内容回答
2. 如果资料里没有答案，就说"资料里没有相关内容"，不要编
3. 引用资料时，在句末标注编号，比如 [1]
4. 不要使用资料之外的知识
"""

RAG_TEMPLATE = """【参考资料】

{context}

【问题】
{question}

【回答要求】
- 只使用上面的资料
- 每条结论后标注来源编号，比如 [1]
- 用中文回答
"""


@dataclass
class RetrievedChunk:
    """一条检索结果。"""

    chunk_id: int
    filename: str
    content: str
    score: float                    # 排序分：纯向量=余弦相似度；混合=RRF 分
    vec_score: float | None = None  # 向量相似度，专门用于拒答判断


def retrieve(db: Session, question: str, top_k: int = 5) -> list[RetrievedChunk]:
    """按语义检索最相关的几块。"""
    q_vec = embed_texts([question])[0]

    distance = DocumentChunk.embedding.cosine_distance(q_vec)
    stmt = (
        select(DocumentChunk, Document.filename, distance.label("dist"))
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(DocumentChunk.embedding.isnot(None))
        .order_by(distance)
        .limit(top_k)
    )

    rows = db.execute(stmt).all()
    return [
        RetrievedChunk(
            chunk_id=chunk.id,
            filename=filename,
            content=chunk.content,
            score=1 - dist,
            vec_score=1 - dist,        # ← 新增：纯向量时，两者相同
        )
        for chunk, filename, dist in rows
    ]


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """把检索结果拼成 prompt。"""
    parts = [
        f"[{i}] 来源：{c.filename}\n{c.content}"
        for i, c in enumerate(chunks, start=1)
    ]
    return RAG_TEMPLATE.format(
        context="\n\n".join(parts),
        question=question,
    )


def answer(db: Session, question: str, top_k: int = 5) -> dict:
    """RAG 主流程：混合检索 → 判断 → 生成。"""
    chunks = hybrid_retrieve(db, question, top_k)      # ← 改成混合检索

    if not chunks:
        return {"answer": "知识库里还没有任何文档。", "sources": []}

    # ⚠️ 用「向量相似度」判断，不能用 RRF 分数（量纲不同）
    vec_scores = [c.vec_score for c in chunks if c.vec_score is not None]
    best_vec = max(vec_scores) if vec_scores else 0.0

    if best_vec < MIN_SCORE:
        return {"answer": "资料里没有找到相关内容。", "sources": []}

    prompt = build_prompt(question, chunks)
    text = chat(prompt, system=RAG_SYSTEM)

    return {
        "answer": text,
        "sources": [
            {
                "index": i,
                "filename": c.filename,
                "score": round(c.vec_score, 3) if c.vec_score is not None else 0.0,
                "preview": c.content[:80],
            }
            for i, c in enumerate(chunks, start=1)
        ],
    }


def hybrid_retrieve(
    db: Session,
    question: str,
    top_k: int = 5,
    recall_n: int = 20,
    rrf_k: int = 60,
) -> list[RetrievedChunk]:
    """混合检索：向量 + BM25，用 RRF 融合。"""
    # ① 两路各取 20 个候选
    vec_chunks = retrieve(db, question, top_k=recall_n)
    vec_scores = {r.chunk_id: r.score for r in vec_chunks}

    kw_ids = keyword_search(db, question, limit=recall_n)
    kw_chunks = (
        db.query(DocumentChunk, Document.filename)
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(DocumentChunk.id.in_(kw_ids))
        .all()
    ) if kw_ids else []
    # 按 BM25 的原始顺序重排
    kw_map = {c.id: (c, fn) for c, fn in kw_chunks}
    kw_ranked = [kw_map[i] for i in kw_ids if i in kw_map]

    # ② RRF 融合
    rrf: dict[int, float] = {}
    info: dict[int, tuple] = {}

    for rank, r in enumerate(vec_chunks, start=1):
        rrf[r.chunk_id] = rrf.get(r.chunk_id, 0) + 1 / (rrf_k + rank)
        info[r.chunk_id] = (r.filename, r.content)

    for rank, (c, fn) in enumerate(kw_ranked, start=1):
        rrf[c.id] = rrf.get(c.id, 0) + 1 / (rrf_k + rank)
        info[c.id] = (fn, c.content)

    # ③ 按 RRF 分数排序，取 top_k
    ordered = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:top_k]

    return [
        RetrievedChunk(
            chunk_id=cid,
            filename=info[cid][0],
            content=info[cid][1],
            score=score,
            vec_score=vec_scores.get(cid),
        )
        for cid, score in ordered
    ]