"""文档上传与解析接口。"""

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, DocumentChunk
from app.services.documents import extract_text_from_bytes, split_text

router = APIRouter(prefix="/documents", tags=["文档"])

# 上限 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# 只允许这三种
ALLOWED_SUFFIXES = {".txt", ".md", ".pdf"}


class DocumentRead(BaseModel):
    """返回给前端的文档信息。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    chunk_count: int


@router.post("", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """上传文档 → 解析 → 切分 → 存库。"""
    filename = file.filename or "未命名"
    suffix = Path(filename).suffix.lower()

    # ① 类型校验
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{suffix}（只支持 {', '.join(sorted(ALLOWED_SUFFIXES))}）",
        )

    # ② 流式读取 + 大小限制
    pieces: list[bytes] = []
    total = 0
    while True:
        piece = await file.read(1024 * 1024)      # 每次读 1MB
        if not piece:
            break
        total += len(piece)
        if total > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="文件超过 10MB 上限")
        pieces.append(piece)
    content = b"".join(pieces)

    # ③ 解析
    try:
        text = extract_text_from_bytes(content, filename)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"解析失败：{e}")

    # ④ 切分
    chunks = split_text(text, chunk_size=500, overlap=50)
    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="没有提取到任何文字（可能是扫描件，需要 OCR）",
        )

    # ⑤ 存库
    document = Document(filename=filename, chunk_count=len(chunks))
    db.add(document)
    db.flush()                      # ← 先拿到 document.id，但还没提交

    for i, chunk in enumerate(chunks):
        db.add(DocumentChunk(
            document_id=document.id,
            chunk_index=i,
            content=chunk,
        ))

    db.commit()
    db.refresh(document)
    return document