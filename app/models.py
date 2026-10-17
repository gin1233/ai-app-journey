"""数据表定义。

一个类 = 一张表
一个属性 = 一列
"""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Note(Base):
    """笔记表。"""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, default="")


class Job(Base):
    """后台任务表。

    为什么任务状态要存数据库，而不是存在内存里？
        1. 用户要能「查」进度 —— 内存里的东西没有句柄给你查
        2. 进程重启后还能知道「有任务没跑完」
        3. 多台服务器部署时，哪台都能看到
    """

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    total: Mapped[int] = mapped_column(default=0)
    done: Mapped[int] = mapped_column(default=0)
    message: Mapped[str] = mapped_column(Text, default="")