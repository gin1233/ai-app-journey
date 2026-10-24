"""RAG 问答接口。"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.rag import answer

router = APIRouter(prefix="/rag", tags=["RAG"])


class AskRequest(BaseModel):
    """提问。"""

    question: str = Field(min_length=1, max_length=500)


class Source(BaseModel):
    """一条出处。"""

    index: int
    filename: str
    score: float
    preview: str


class AskResponse(BaseModel):
    """回答 + 出处。"""

    answer: str
    sources: list[Source]


@router.post("/ask", response_model=AskResponse)
def rag_ask(payload: AskRequest, db: Session = Depends(get_db)):
    """基于你的文档回答问题。"""
    return answer(db, payload.question)