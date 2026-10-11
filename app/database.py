"""数据库连接与会话管理。

连接串从 .env 读，代码里不写死密码。
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

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


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：每个请求给一个会话，用完自动关闭。"""
    with SessionLocal() as db:
        yield db

    # db = SessionLocal()
    # try:
    #     yield db          # 把会话交给接口函数
    # finally:
    #     db.close()        # 无论成功还是报错，一定关闭