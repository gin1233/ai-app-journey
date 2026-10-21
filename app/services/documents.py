"""文档解析与切分。

这个模块只做两件事：
    1. 把不同格式的文件变成「纯文本」
    2. 把长文本切成一块一块（chunk）

为什么单独放一层？
    解析和切分都是「数据预处理」，和 HTTP、数据库都没关系。
    写成纯函数，最好测试。
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


def extract_text(path: Path) -> str:
    """把一个文件变成纯文本。

    支持：.txt / .md / .pdf
    """
    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8")

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        # 注意 page.extract_text() 可能返回 None（比如纯图片页）
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    raise ValueError(f"不支持的文件类型: {suffix}")


def split_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """把长文本切成固定大小的块。

    chunk_size: 每块大约多少字
    overlap:    相邻两块重叠多少字（防止一句话被切断）
    """
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap          # ← 往回退一点，形成重叠

    return chunks


def clean_text(text: str) -> str:
    """清掉无法编码成 UTF-8 的字符。

    为什么需要？
        PDF 的字体映射偶尔会吐出「孤立代理字符」
        （U+D800~U+DFFF，比如 \\ud83d）。
        这种字符在 UTF-8 里是非法的，存进数据库会报
        UnicodeEncodeError。
    """
    return text.encode("utf-8", errors="ignore").decode("utf-8")



def extract_text_from_bytes(content: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix in (".txt", ".md"):
        text = content.decode("utf-8")
    elif suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages)
    else:
        raise ValueError(f"不支持的文件类型: {suffix}")

    return clean_text(text)      # ← 所有出口统一清洗


def extract_text(path: Path) -> str:
    """便捷函数：从磁盘上的文件提取文字。"""
    return extract_text_from_bytes(path.read_bytes(), path.name)


