"""FastAPI 应用入口。"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, AI 应用工程师"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"你好，{name}！"}