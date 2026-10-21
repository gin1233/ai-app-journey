"""数据表定义。

一个类 = 一张表
一个属性 = 一列
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
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


class Document(Base):
    """上传的文档。"""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    chunk_count: Mapped[int] = mapped_column(default=0)


class DocumentChunk(Base):
    """文档切出来的块。

    为什么单独一张表，而不是塞进 documents 的一个 JSON 字段？
        1. 以后要按块检索 —— 一块一行，才好建索引
        2. 一个文档可能有几百块 —— JSON 字段会很臃肿
        3. 能单独删除/更新某一块
    """

    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    chunk_index: Mapped[int] = mapped_column()
    content: Mapped[str] = mapped_column(Text)