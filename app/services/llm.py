"""大模型调用的封装。

为什么单独放一层？
    1. 接口层只关心"要一段回复"，不关心怎么调模型
    2. 以后换平台/换模型，只改这一个文件
    3. 加日志、重试、超时控制，都在这一个地方改
"""

from __future__ import annotations
from openai import OpenAI
from app.config import get_config
from functools import lru_cache
from collections.abc import Iterator

@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """创建（并缓存）大模型客户端。"""
    api_key = get_config("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("没有配置 LLM_API_KEY，请检查 .env")

    return OpenAI(
        api_key=api_key,
        base_url=get_config("LLM_BASE_URL") or None,
    )


def chat(prompt: str, system: str = "你是一个乐于助人的助手。") -> str:
    """发一句问话，拿一句回复。"""
    client = get_client()
    model = get_config("LLM_MODEL", "deepseek-chat")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def stream_chat(
    prompt: str,
    system: str = "你是一个乐于助人的助手。",
) -> Iterator[str]:
    """流式调用：一段一段地产出模型的输出。

    ⚠️ 这里 yield 的是「纯文本片段」，不是 HTTP 格式。
       怎么包装成 SSE 是接口层的事 —— 服务层不该知道 HTTP 长什么样。
    """
    client = get_client()
    model = get_config("LLM_MODEL", "deepseek-chat")

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        stream=True,          # ← 和 chat() 唯一的区别
    )

    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:             # 有些 chunk 的 content 是 None，跳过
            yield piece