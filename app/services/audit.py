"""审计日志。"""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models import AuditLog


def log_action(db: Session, action: str, args: dict, result: dict) -> None:
    """记一条审计日志。

    ⚠️ 这里单独 try：审计失败不应该让业务失败。
       但"要不要这么做"是个权衡 —— 见下面说明。
    """
    try:
        db.add(
            AuditLog(
                action=action,
                args=json.dumps(args, ensure_ascii=False)[:2000],
                result=json.dumps(result, ensure_ascii=False)[:2000],
            )
        )
        db.commit()
    except Exception:
        db.rollback()