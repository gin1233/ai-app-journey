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
    score: float


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
    """RAG 主流程：检索 → 判断 → 生成。"""
    chunks = retrieve(db, question, top_k)

    if not chunks:
        return {"answer": "知识库里还没有任何文档。", "sources": []}

    if chunks[0].score < MIN_SCORE:
        return {"answer": "资料里没有找到相关内容。", "sources": []}

    prompt = build_prompt(question, chunks)
    text = chat(prompt, system=RAG_SYSTEM)

    return {
        "answer": text,
        "sources": [
            {
                "index": i,
                "filename": c.filename,
                "score": round(c.score, 3),
                "preview": c.content[:80],
            }
            for i, c in enumerate(chunks, start=1)
        ],
    }