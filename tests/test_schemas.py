"""测试 Pydantic 模型的校验逻辑。

这一类测试【不需要数据库、不需要启动应用】—— 跑得最快。
"""

import pytest
from pydantic import ValidationError

from app.schemas import NoteCreate, NoteUpdate


def test_create_ok():
    """正常数据应该能通过。"""
    note = NoteCreate(title="正常标题", content="内容")
    assert note.title == "正常标题"


def test_title_cannot_be_blank():
    """只有空格的标题应该被拒绝。"""
    with pytest.raises(ValidationError):
        NoteCreate(title="   ")


def test_title_is_stripped():
    """标题两边的空格应该被去掉。"""
    note = NoteCreate(title="  前后有空格  ")
    assert note.title == "前后有空格"


def test_update_allows_partial():
    """更新时可以只传一个字段。"""
    upd = NoteUpdate(title="只改标题")
    assert upd.content is None

    dumped = upd.model_dump(exclude_unset=True)
    assert dumped == {"title": "只改标题"}
    assert "content" not in dumped