"""Agent：让模型自己决定调用哪些工具。

核心是一个「循环」：
    模型说要调工具 → 我们执行 → 把结果还给它 → 它再决定下一步

Day 22 新增：
    写工具（create_note）不再直接执行，
    而是返回 needs_confirm + action_id，等用户确认后再执行。
"""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models import Note
from app.services.llm import get_client
from app.config import get_config
from app.services.pending import create_pending
from datetime import datetime, timezone
from app.services.audit import log_action

MAX_STEPS = 5

# 这些工具会改数据，必须先让用户确认
WRITE_TOOLS = {"create_note", "delete_note"}

AGENT_SYSTEM = """你是一个笔记助手。

规则：
1. 需要找笔记时，先用 search_notes 搜索，再用 get_note 读取完整内容
2. 只根据笔记内容回答，不要编造
3. 工具返回错误时，换一种方式重试，或者如实告诉用户
4. 回答要简洁，必要时标明是第几条笔记
5. create_note 是写操作，只在用户明确要求「创建 / 记录 / 保存」时才用
6. 当用户要求删除笔记时，必须直接调用 delete_note 工具。
   不要在回复里问「是否确认」——系统会自动弹出确认框让用户确认。
   你的职责是「提出操作」，不是「征求同意」。
7. 绝对不要声称"已经删除/已经创建"——除非你真的调用了对应的工具
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
    {
        # ⭐ Day 22 新增：写工具
        "type": "function",
        "function": {
            "name": "create_note",
            "description": (
                "创建一条新笔记。这是写操作，会真的存进数据库。"
                "只有在用户明确要求「创建 / 记录 / 保存」时才使用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "笔记标题",
                    },
                    "content": {
                        "type": "string",
                        "description": "笔记正文，可以为空",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_note",
            "description": (
                "删除一条笔记（软删除，之后可以在数据库里恢复）。"
                "这是不可逆操作，只有在用户明确要求「删除」时才使用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "integer",
                        "description": "要删除的笔记 id",
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

    if name == "create_note":
        # ⭐ 即使用户点了确认，参数还是要校验 —— 因为参数是模型生成的
        title = (args.get("title") or "").strip()
        if not title:
            return {"error": "标题不能为空"}

        note = Note(title=title, content=args.get("content", ""))
        db.add(note)
        db.commit()
        db.refresh(note)
        return {"id": note.id, "title": note.title, "created": True}

    if name == "delete_note":
        note = db.get(Note, args.get("note_id"))
        if note is None or note.deleted_at is not None:
            return {"error": "笔记不存在或已删除"}

        note.deleted_at = datetime.now(timezone.utc)
        db.commit()

        result = {"id": note.id, "deleted": True}
        log_action(db, "delete_note", args, result)
        return result

    return {"error": f"未知工具：{name}"}


def run_agent(db: Session, question: str) -> dict:
    """跑一次 Agent 循环。

    返回两种状态：
        {"status": "answered", "answer": ..., "steps": ..., "trace": ...}
        {"status": "needs_confirm", "action_id": ..., "action": ..., "args": ...}
    """
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
            return {
                "status": "answered",
                "answer": msg.content or "",
                "steps": step + 1,
                "trace": trace,
            }

        # ② 把模型的"调用请求"追加进历史
        messages.append(msg)

        # ③ 逐个处理工具调用
        for call in msg.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            # ⭐ 写工具：不执行，立刻返回，等用户确认
            if name in WRITE_TOOLS:
                action_id = create_pending(name, args)
                return {
                    "status": "needs_confirm",
                    "action_id": action_id,
                    "action": name,
                    "args": args,
                    "steps": step + 1,
                    "trace": trace,
                }

            # 只读工具：照常执行
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
        "status": "max_steps",
        "answer": "（这个任务需要的步骤太多，已停止。请把问题拆小一点。）",
        "steps": MAX_STEPS,
        "trace": trace,
    }