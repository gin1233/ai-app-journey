"""批量处理任务。

注意：这里不用 FastAPI 的 Depends(get_db)，而是自己开会话。
因为后台任务执行时，请求早就结束了 —— 请求作用域的会话不该依赖。
"""

from __future__ import annotations

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Job, Note
from app.services.llm import chat



def summarize_all_notes(job_id: int) -> None:
    """后台任务：给所有笔记生成一句话摘要。"""
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if job is None:
            return

        try:
            notes = db.scalars(select(Note)).all()
            job.total = len(notes)
            job.status = "running"
            db.commit()

            results: list[str] = []

            for i, note in enumerate(notes):
                try:
                    summary = chat(
                        f"用一句话概括这条笔记：\n\n标题:{note.title}\n正文:{note.content}",
                        system="你是一个简洁的笔记助手，只输出一句话概括。",
                    )
                except Exception as e:
                    summary = f"(生成失败：{e})"

                results.append(f"## 标题: {note.title}\n 总结:\n{summary}")

                job.done = i + 1
                db.commit()

            job.message = "\n\n".join(results)
            job.status = "done"

        except Exception as e:
            db.rollback()
            job.status = "failed"
            job.message = f"任务失败：{e}"

        db.commit()