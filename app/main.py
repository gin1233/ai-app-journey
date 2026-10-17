"""FastAPI 应用入口。

这个文件只负责"组装"：
    1. 建表
    2. 创建应用
    3. 把各个 router 挂上去
"""

from fastapi import FastAPI
from app.database import Base, engine
from app.routers import ai, notes, jobs
from fastapi.staticfiles import StaticFiles


Base.metadata.create_all(bind=engine)


app = FastAPI(title="AI 应用学习项目")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# 把 notes 这个"分机"接到总机上
app.include_router(notes.router)
app.include_router(ai.router)
app.include_router(jobs.router)


@app.get("/")
def read_root():
    return {"message": "Hello, AI 应用工程师"}