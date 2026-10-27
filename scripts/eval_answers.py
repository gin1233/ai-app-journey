"""评答案质量：跑评测集，用 LLM 当裁判打分。"""

from statistics import mean

from app.database import SessionLocal
from app.services.eval_judge import  (
    check_citations,
    is_independent_judge,
    judge,
    judge_model_name,
)
from app.services.rag import answer, retrieve

EVAL_SET = [
    {"q": "如果我在上海出差 3 晚，最多能报销多少？"},
    {"q": "公司给不给报打车钱？"},
    {"q": "去年的年终奖发了吗？"},
    {"q": "听说员工可以无限期远程办公？"},
    {"q": "每年的培训预算是多少钱？"},
    {"q": "红烧肉怎么做"},              # ← 故意放一个"资料里没有"的
]


def main() -> None:
    if not is_independent_judge():
        print("⚠️  警告：裁判和生成是同一个平台，评分存在自评偏差\n")
    print(f"裁判模型：{judge_model_name()}\n")

    rows = []

    with SessionLocal() as db:
        for item in EVAL_SET:
            q = item["q"]
            result = answer(db, q)
            chunks = retrieve(db, q, top_k=5)
            context = "\n\n".join(c.content for c in chunks)

            if result["sources"]:
                score = judge(q, context, result["answer"])
            else:
                # 拒答的不需要裁判，直接算满分（它没编）
                score = {"relevance": 0, "faithfulness": 5,
                         "completeness": 0, "reason": "拒答"}

            cite = check_citations(result["answer"], len(chunks))
            rows.append((q, score, cite))

            print(f"\n问题：{q}")
            print(f"答案：{result['answer'][:80]}")
            print(f"评分：相关 {score['relevance']} / 忠实 {score['faithfulness']} / 完整 {score['completeness']}")
            print(f"理由：{score['reason']}")
            print(f"引用：{cite}")

    print("\n" + "=" * 50)
    print(f"平均相关性  ：{mean(r[1]['relevance'] for r in rows):.2f}")
    print(f"平均忠实度  ：{mean(r[1]['faithfulness'] for r in rows):.2f}")
    print(f"平均完整度  ：{mean(r[1]['completeness'] for r in rows):.2f}")
    print(f"有引用的比例：{sum(1 for r in rows if r[2]['has_citation']) / len(rows):.0%}")


if __name__ == "__main__":
    main()