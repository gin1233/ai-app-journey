"""Agent 接口。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.agent import execute_tool, run_agent
from app.services.pending import pop_pending

router = APIRouter(prefix="/agent", tags=["Agent"])


class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class AgentResponse(BaseModel):
    """两种状态都可能返回，所以字段都有默认值。"""

    status: str = "answered"          # answered / needs_confirm / max_steps
    answer: str = ""
    action_id: str | None = None
    action: str | None = None
    args: dict | None = None
    steps: int = 0
    trace: list[dict] = Field(default_factory=list)


class ConfirmRequest(BaseModel):
    action_id: str
    approved: bool


@router.post("/ask", response_model=AgentResponse)
def agent_ask(payload: AgentRequest, db: Session = Depends(get_db)):
    """问一句话，让 Agent 自己决定调用哪些工具。"""
    return run_agent(db, payload.question)


@router.post("/confirm")
def agent_confirm(payload: ConfirmRequest, db: Session = Depends(get_db)):
    """用户确认（或取消）一个待执行的操作。

    这里用的是 pop —— 同一个 action_id 只能确认一次。
    """
    pending = pop_pending(payload.action_id)
    if pending is None:
        raise HTTPException(
            status_code=404,
            detail="操作不存在、已确认过，或已过期",
        )

    if not payload.approved:
        return {"status": "cancelled"}

    result = execute_tool(db, pending["action"], pending["args"])
    return {"status": "done", "result": result}