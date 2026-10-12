"""接口的输入输出格式（Pydantic 模型）。

放这里是为了和"数据库表定义"（models.py）分开：
    models.py  —— 数据库长什么样
    schemas.py —— 接口收发什么样
这两个东西经常长得像，但职责完全不同。
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NoteCreate(BaseModel):
    """提交笔记时的格式（输入）。"""

    title: str = Field(min_length=1, max_length=100)
    content: str = Field(default="", max_length=5000)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("标题不能为空或只有空格")
        return v


class NoteUpdate(BaseModel):
    """更新笔记时的格式（输入，字段都可选）。"""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, max_length=5000)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("标题不能为空或只有空格")
        return v


class NoteRead(BaseModel):
    """返回笔记时的格式（输出）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str