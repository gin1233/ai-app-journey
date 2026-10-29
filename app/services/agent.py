"""Agent：让模型自己决定调用哪些工具。

核心是一个「循环」：
    模型说要调工具 → 我们执行 → 把结果还给它 → 它再决定下一步
"""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models import Note
from app.services.llm import get_client
from app.config import get_config

MAX_STEPS = 5

AGENT_SYSTEM = """你是一个笔记助手。

规则：
1. 需要找笔记时，先用 search_notes 搜索，再用 get_note 读取完整内容
2. 只根据笔记内容回答，不要编造
3. 工具返回错误时，换一种方式重试，或者如实告诉用户
4. 回答要简洁，必要时标明是第几条笔记
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": (
                "按关键词搜索用户的笔记标题，返回匹配的笔记 id 和标题。"
                "只返回标题，不返回正文。想读正文请接着用 get_note。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "要搜索的关键词，比如「向量数据库」",
                    }
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_note",
            "description": "根据笔记 id 读取完整内容（标题 + 正文）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "integer",
                        "description": "笔记的 id，从 search_notes 的返回里拿",
                    }
                },
                "required": ["note_id"],
            },
        },
    },
]


def execute_tool(db: Session, name: str, args: dict) -> dict:
    """执行一个工具，返回结果字典。

    ⚠️ 出错时返回 {"error": "..."}，不要抛异常。
       抛异常会中断整个循环，模型就没机会改正了。
    """
    if name == "search_notes":
        keyword = (args.get("keyword") or "").strip()
        if not keyword:
            return {"error": "keyword 不能为空"}

        notes = (
            db.query(Note)
            .filter(Note.title.contains(keyword))
            .limit(5)
            .all()
        )
        return {
            "count": len(notes),
            "notes": [{"id": n.id, "title": n.title} for n in notes],
        }

    if name == "get_note":
        note = db.get(Note, args.get("note_id"))
        if note is None:
            return {"error": f"笔记 {args.get('note_id')} 不存在"}
        return {"id": note.id, "title": note.title, "content": note.content}

    return {"error": f"未知工具：{name}"}


def run_agent(db: Session, question: str) -> dict:
    """跑一次完整的 Agent 循环。"""
    client = get_client()
    model = get_config("LLM_MODEL", "deepseek-chat")

    messages: list[dict] = [
        {"role": "system", "content": AGENT_SYSTEM},
        {"role": "user", "content": question},
    ]
    trace: list[dict] = []

    for step in range(MAX_STEPS):
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
        )
        msg = resp.choices[0].message

        # ① 没有工具调用 → 模型要直接回答，结束
        if not msg.tool_calls:
            return {"answer": msg.content or "", "steps": step + 1, "trace": trace}

        # ② 把模型的"调用请求"追加进历史
        messages.append(msg)

        # ③ 逐个执行工具
        for call in msg.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            result = execute_tool(db, name, args)
            trace.append({"tool": name, "args": args, "result": result})

            # ④ 把工具结果作为 role=tool 追加
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    # 超过最大步数，强制收尾
    return {
        "answer": "（这个任务需要的步骤太多，已停止。请把问题拆小一点。）",
        "steps": MAX_STEPS,
        "trace": trace,
    }