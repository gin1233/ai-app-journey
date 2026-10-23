"""Embedding 服务：把文本变成向量。

为什么用本地模型，不调 API？
    1. DeepSeek 没有 embedding 接口
    2. 本地模型免费、离线
    3. 换模型只改 MODEL_NAME 和维度
"""

from __future__ import annotations

from functools import lru_cache

from fastembed import TextEmbedding

# BGE-small-zh-v1.5：中文小模型，512 维，约 100MB
MODEL_NAME = "BAAI/bge-small-zh-v1.5"


@lru_cache(maxsize=1)
def get_model() -> TextEmbedding:
    """加载模型（只加载一次，之后复用）。

    第一次调用会下载模型，可能要等几分钟。
    """
    return TextEmbedding(model_name=MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量把文本变成向量。

    输入 10 段文字，输出 10 个向量（每个 512 个数字）。
    """
    model = get_model()
    return [vec.tolist() for vec in model.embed(texts)]