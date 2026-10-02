"""配置管理：把"会变的东西"集中到一个地方。

为什么需要这个文件？
    数据库地址、API Key、日志级别……这些东西在不同环境下是不一样的
    （你自己电脑 = development，线上服务器 = production）。

    如果写死在代码里：
        1. 换个环境就要改代码，容易改错
        2. 密钥会跟着 Git 提交出去，等于把钥匙贴在门上

    所以业界惯例是：
        代码里不写具体值  ->  从"环境变量"里读
        环境变量的值存在 .env 文件里（这个文件永远不进 Git）
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# __file__ 是当前这个文件的路径
# .resolve() 转成绝对路径，.parent 取上一层
# 所以：config.py -> app/ -> 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 加载 .env 文件里的配置到环境变量
# 如果 .env 不存在，load_dotenv 会安静地跳过，不报错
load_dotenv(PROJECT_ROOT / ".env")


def get_config(key: str, default: str = "") -> str:
    """读一个配置项。

    规则：环境变量里有什么就用什么，没有就用默认值兜底。
    """
    return os.getenv(key, default)


def show_config() -> dict[str, str]:
    """返回当前配置的快照，用于打印和调试。"""
    return {
        "APP_NAME": get_config("APP_NAME", "ai-app-journey"),
        "APP_ENV": get_config("APP_ENV", "development"),
        "LOG_LEVEL": get_config("LOG_LEVEL", "INFO"),
    }