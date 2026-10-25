"""评测检索效果：对比向量 / BM25 / 混合三种方案。"""

from app.database import SessionLocal
from app.services.rag import retrieve, hybrid_retrieve
from app.services.keyword_search import keyword_search

# ⚠️ 这是示例，你要按自己的文档调整
EVAL_SET = [
    {"q": "公司现在有多少员工？", "expect": [22]},
    {"q": "入职满 3 年有几天年假？", "expect": [23]},
    {"q": "一周最多可以远程办公几天？", "expect": [24]},
    {"q": "去上海出差，住宿每晚最多报销多少？", "expect": [24]},
    {"q": "报销单最晚要在多少天内提交？", "expect": [24]},
    {"q": "电脑坏了应该联系谁？工作时间内多久响应？", "expect": [25]},
    {"q": "每年的培训预算是多少钱？", "expect": [25]},
    {"q": "试用期多久？试用期工资是转正的多少？", "expect": [26]},
    {"q": "年度调薪一般在几月？整体调薪幅度大概多少？", "expect": [27]},
    {"q": "法定节假日加班怎么算？可以换成调休吗？", "expect": [28]},
]

K = 5


def hit(ids: list[int], expect: list[int]) -> int:
    return 1 if set(ids[:K]) & set(expect) else 0


def main() -> None:
    with SessionLocal() as db:
        vec_hits, kw_hits, hyb_hits = 0, 0, 0

        print(f"{'问题':<24} {'向量':<6} {'BM25':<6} {'混合':<6}")
        print("-" * 48)

        for item in EVAL_SET:
            q, expect = item["q"], item["expect"]

            v_ids = [c.chunk_id for c in retrieve(db, q, top_k=K)]
            k_ids = keyword_search(db, q, limit=K)
            h_ids = [c.chunk_id for c in hybrid_retrieve(db, q, top_k=K)]

            v, k, h = hit(v_ids, expect), hit(k_ids, expect), hit(h_ids, expect)
            vec_hits += v
            kw_hits += k
            hyb_hits += h

            print(f"{q:<24} {'✓' if v else '✗':<6} {'✓' if k else '✗':<6} {'✓' if h else '✗':<6}")

        n = len(EVAL_SET)
        print("-" * 48)
        print(f"Recall@{K}:  向量 {vec_hits/n:.0%}   BM25 {kw_hits/n:.0%}   混合 {hyb_hits/n:.0%}")


if __name__ == "__main__":
    main()