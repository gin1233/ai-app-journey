"""待确认的操作。

⚠️ 这是内存版，只适合演示。生产上必须：
    1. 存数据库（进程重启不丢、多实例共享）
    2. 加 expires_at（防止内存泄漏、防止旧操作被误确认）
    3. 绑定 user_id（防止别人确认你的操作）
"""

from __future__ import annotations

from uuid import uuid4

# action_id -> {"action": 工具名, "args": 参数}
_pending: dict[str, dict] = {}


def create_pending(action: str, args: dict) -> str:
    """登记一个待确认操作，返回 action_id。"""
    action_id = uuid4().hex[:12]
    _pending[action_id] = {"action": action, "args": args}
    return action_id


def pop_pending(action_id: str) -> dict | None:
    """取出并删除。

    为什么用 pop 而不是 get？
        防止同一个操作被确认两次（双击、重放）。
    """
    return _pending.pop(action_id, None)