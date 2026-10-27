"""用大模型当裁判，给 RAG 答案打分。

⚠️ 裁判用的是独立配置（JUDGE_*），不是生成用的 LLM_*。
   如果两者配成同一个平台，评分会有"自评偏差"。
"""

from __future__ import annotations

import json
import re

from app.config import get_config
from app.services.llm import judge_chat

JUDGE_SYSTEM = """你是一个严格的答案审核员。

你会收到三样东西：问题、参考资料、候选答案。
请判断候选答案是否合格，只输出 JSON，不要任何其他文字。

判断标准：
1. relevance（相关性）：答案是否回答了问题（1-5）
2. faithfulness（忠实度）：答案内容是否都能在资料里找到依据（1-5）
3. completeness（完整性）：是否遗漏了资料里的关键信息（1-5）

评分锚点（必须按这个来判）：
- 5 分：完整覆盖资料中的全部关键点，没有多余内容
- 3 分：覆盖部分关键点，或混入了资料里没有的内容
- 1 分：没有回答问题，或内容在资料里找不到依据

答案长度不是评分项。简短但完整的答案应该得高分；
冗长但夹杂无关内容或错误的答案应该扣分。

输出格式（只输出 JSON）：
{"relevance": 5, "faithfulness": 4, "completeness": 3, "reason": "一句话说明"}
"""

JUDGE_TEMPLATE = """【问题】
{question}

【参考资料】
{context}

【候选答案】
{answer}
"""


def is_independent_judge() -> bool:
    """裁判和生成是不是两个不同的平台。

    True  = 独立裁判，分数可信
    False = 同一个模型自评，分数存在偏差
    """
    gen_url = get_config("LLM_BASE_URL")
    judge_url = get_config("JUDGE_BASE_URL") or gen_url
    return judge_url != gen_url


def judge_model_name() -> str:
    """当前实际使用的裁判模型名（用于日志）。"""
    return get_config("JUDGE_MODEL") or get_config("LLM_MODEL", "unknown")


def _parse_json(raw: str) -> dict:
    """从模型输出里抠出 JSON（它可能包了 ```json）。"""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {
            "relevance": 0,
            "faithfulness": 0,
            "completeness": 0,
            "reason": f"解析失败：{raw[:80]}",
        }


def judge(question: str, context: str, answer: str) -> dict:
    """给一个答案打分 —— 用的是裁判模型，不是生成模型。"""
    prompt = JUDGE_TEMPLATE.format(
        question=question,
        context=context,
        answer=answer,
    )
    return _parse_json(judge_chat(prompt, system=JUDGE_SYSTEM))


def check_citations(answer_text: str, num_chunks: int) -> dict:
    """检查引用编号是否有效（规则判断，不花钱）。"""
    cited = {int(m) for m in re.findall(r"\[(\d+)\]", answer_text)}
    if not cited:
        return {"has_citation": False, "valid_ratio": 0.0}
    valid = {i for i in range(1, num_chunks + 1)}
    return {
        "has_citation": True,
        "valid_ratio": len(cited & valid) / len(cited),
    }