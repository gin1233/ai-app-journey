"""pytest 的共享配置（fixture）。

这个文件里的 fixture，所有测试函数都能直接当参数用。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# ── 独立的测试数据库：SQLite 内存库，进程结束就消失 ──
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,          # 让所有连接共用同一块内存
)
TestingSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False
)


@pytest.fixture()
def client():
    """给每个测试一个「干净的库 + 可用的客户端」。

    一个测试跑完，库就 drop 掉 —— 下一个测试从零开始。
    """
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # ⭐ 把「真数据库」换成「测试数据库」
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)