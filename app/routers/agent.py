"""Agent 接口。"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.agent import run_agent

router = APIRouter(prefix="/agent", tags=["Agent"])


class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class AgentResponse(BaseModel):
    answer: str
    steps: int
    trace: list[dict]


@router.post("/ask", response_model=AgentResponse)
def agent_ask(payload: AgentRequest, db: Session = Depends(get_db)):
    """问一句话，让 Agent 自己决定调用哪些工具。"""
    return run_agent(db, payload.question)