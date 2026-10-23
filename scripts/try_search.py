"""验证：语义搜索 vs 关键词搜索。"""

from sqlalchemy import select

from app.database import SessionLocal
from app.models import DocumentChunk
from app.services.embeddings import embed_texts


def main() -> None:
    query = "怎么配置数据库连接"
    q_vec = embed_texts([query])[0]

    with SessionLocal() as db:
        # 按"向量距离"排序（<=> 越小越像）
        distance = DocumentChunk.embedding.cosine_distance(q_vec)
        stmt = (
            select(DocumentChunk.content, distance.label("dist"))
            .where(DocumentChunk.embedding.isnot(None))
            .order_by(distance)
            .limit(3)
        )

        print(f"查询：{query}\n")
        for i, (content, dist) in enumerate(db.execute(stmt), 1):
            print(f"[{i}] 相似度 {1 - dist:.3f}")
            print(f"    {content[:60]}...\n")


if __name__ == "__main__":
    main()