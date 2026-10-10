"""FastAPI 应用入口。"""

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.database import Base, SessionLocal, engine
from app.models import Note

# 建表：表不存在就创建，已存在就跳过
Base.metadata.create_all(bind=engine)

app = FastAPI()


class NoteCreate(BaseModel):
    """提交笔记时的格式（输入）。"""

    title: str = Field(min_length=1, max_length=100)
    content: str = Field(default="", max_length=5000)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("标题不能为空或只有空格")
        return v


class NoteRead(BaseModel):
    """返回笔记时的格式（输出）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str


@app.get("/")
def read_root():
    return {"message": "Hello, AI 应用工程师"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"你好，{name}！"}


@app.get("/notes", response_model=list[NoteRead])
def list_notes():
    with SessionLocal() as db:
        return db.query(Note).all()


@app.post("/notes", response_model=NoteRead)
def create_note(payload: NoteCreate):
    with SessionLocal() as db:
        note = Note(title=payload.title, content=payload.content)
        db.add(note)          # 放进会话（还在排队）
        db.commit()           # 提交（真正写进数据库）
        db.refresh(note)      # 读回最新状态，拿到自动生成的 id
        return note