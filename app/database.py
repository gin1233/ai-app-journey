"""数据库连接与会话管理。

连接串从 .env 读，代码里不写死密码。
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_config

DATABASE_URL = get_config(
    "DATABASE_URL",
    "postgresql+psycopg://aiapp:aiapp_dev_pw@localhost:5432/aiapp",
)

# 引擎：通往数据库的"管道"
engine = create_engine(DATABASE_URL, echo=False)

# 会话工厂：每次操作数据库就造一个"会话"
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """所有数据表都要继承它。"""