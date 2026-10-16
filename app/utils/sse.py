"""SSE（Server-Sent Events）格式的工具函数。

为什么单独放一个模块？
    因为「笔记接口」和「AI 接口」都要用它。
    两个地方用同一个函数时，它就该从某一方搬出来，成为公共工具。
"""

from __future__ import annotations

import json
from collections.abc import Iterator


def to_sse(pieces: Iterator[str]) -> Iterator[str]:
    """把纯文本片段包装成 SSE 格式。

    为什么用 json.dumps？
        模型输出里可能有换行符。SSE 协议里「换行 = 消息分隔符」，
        不转义的话，一条消息会被切成两条。
    """
    for piece in pieces:
        yield f"data: {json.dumps(piece, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"