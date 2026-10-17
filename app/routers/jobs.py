"""后台任务相关的接口。"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job
from app.services.jobs import summarize_all_notes

router = APIRouter(prefix="/jobs", tags=["任务"])


class JobRead(BaseModel):
    """任务状态（返回给前端）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total: int
    done: int
    message: str


@router.post("/summarize-all", response_model=JobRead)
def create_summarize_job(bg: BackgroundTasks, db: Session = Depends(get_db)):
    """给全部笔记生成摘要。立刻返回任务 id，后台慢慢跑。"""
    job = Job(status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    # ⚠️ 只传 job.id —— 绝对不要把 db 传进去
    bg.add_task(summarize_all_notes, job.id)

    return job


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """查询任务进度（前端轮询这个接口）。"""
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return job