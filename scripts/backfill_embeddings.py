"""给所有还没有向量的 chunk 生成向量。

用法：
    python scripts/backfill_embeddings.py
"""

from app.database import SessionLocal
from app.models import DocumentChunk
from app.services.embeddings import embed_texts

BATCH_SIZE = 32


def main() -> None:
    with SessionLocal() as db:
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.embedding.is_(None))
            .all()
        )
        print(f"待处理：{len(chunks)} 块")

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            vectors = embed_texts([c.content for c in batch])

            for chunk, vec in zip(batch, vectors):
                chunk.embedding = vec

            db.commit()
            print(f"已完成 {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")


if __name__ == "__main__":
    main()