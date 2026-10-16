"""笔记相关的接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from app.database import get_db
from app.models import Note
from app.schemas import NoteCreate, NoteRead, NoteUpdate
from app.services.llm import stream_summarize
from app.utils.sse import to_sse

# prefix: 这个 router 下所有路径都自动加上 /notes
# tags:   在 /docs 文档里给这组接口分组
router = APIRouter(prefix="/notes", tags=["笔记"])


@router.get("", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)):
    return db.query(Note).all()


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note


@router.post("", response_model=NoteRead)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")

    db.delete(note)
    db.commit()
    return {"message": "已删除", "id": note_id}


@router.post("/{note_id}/summarize")
def summarize_note(note_id: int, db: Session = Depends(get_db)):
    """用 AI 总结这条笔记（流式返回）。"""
    # ───── 第一步：取数（数据库的活，在这里干完）─────
    note = db.query(Note).filter(Note.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")

    title = note.title
    content = note.content

    # ───── 第二步：推流（跟数据库无关了）─────
    return StreamingResponse(
        to_sse(stream_summarize(title, content)),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )