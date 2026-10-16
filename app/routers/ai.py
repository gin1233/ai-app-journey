"""大模型相关的接口。"""
import json
from fastapi import APIRouter, HTTPException
from openai import APIError, APITimeoutError, RateLimitError
from pydantic import BaseModel, Field, field_validator
from app.services.llm import chat
from collections.abc import Iterator
from fastapi.responses import StreamingResponse
from app.services.llm import chat, stream_chat
from app.utils.sse import to_sse

router = APIRouter(prefix="/ai", tags=["AI"])


class ChatRequest(BaseModel):
    """对话请求。"""

    prompt: str = Field(min_length=1, max_length=4000)
    system: str = Field(default="你是一个乐于助人的助手。", max_length=1000)
    @field_validator("prompt")
    @classmethod
    def prompt_not_blank(cls, v: str) -> str:
        """去掉首尾空白；如果剩下是空的，就拒绝。"""
        v = v.strip()
        if not v:
            raise ValueError("找不到要发送的消息，请重试。")
        return v

class ChatResponse(BaseModel):
    """对话响应。"""

    reply: str


@router.post("/chat", response_model=ChatResponse)
def ai_chat(payload: ChatRequest):
    """把用户的话发给大模型，返回它的回复。"""
    try:
        reply = chat(payload.prompt, payload.system)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="大模型响应超时，请重试")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="请求太频繁或额度不足")
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"大模型服务出错: {e}")

    return ChatResponse(reply=reply)


@router.post("/chat/stream")
def ai_chat_stream(payload: ChatRequest):
    """流式对话：文字一个一个字往外冒。"""
    return StreamingResponse(
        to_sse(stream_chat(payload.prompt, payload.system)),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",     # 防止 nginx 之类的反代攒着不发
        },
    )