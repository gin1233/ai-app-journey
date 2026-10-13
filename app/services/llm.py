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

# # 模块级变量，用来缓存客户端（只创建一次，反复复用）
# _client: OpenAI | None = None


# def get_client() -> OpenAI:
#     """创建（或复用）大模型客户端。

#     ⚠️ 用 global 是因为要给模块级变量 _client 重新赋值。
#        这正好是 Day 06 记的那条规则：改"标签指向哪个盒子"要用 global。
#     """
#     global _client

#     if _client is None:
#         api_key = get_config("LLM_API_KEY")
#         if not api_key:
#             raise RuntimeError("没有配置 LLM_API_KEY，请检查 .env")

#         _client = OpenAI(
#             api_key=api_key,
#             base_url=get_config("LLM_BASE_URL") or None,
#         )
#     return _client

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