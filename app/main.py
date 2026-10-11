"""FastAPI 应用入口。"""

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Note

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


@app.get("/notes", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)):
    return db.query(Note).all()


@app.get("/notes/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note


@app.post("/notes", response_model=NoteRead)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")

    db.delete(note)
    db.commit()
    return {"message": "已删除", "id": note_id}