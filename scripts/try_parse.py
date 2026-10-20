from pathlib import Path

from app.services.documents import extract_text, split_text

# 造一个测试文件
test_file = Path("work/test.md")
test_file.parent.mkdir(exist_ok=True)
test_file.write_text(
    "向量数据库是用于存储高维向量的专用数据库。" * 30,
    encoding="utf-8",
)

text = extract_text(test_file)
print(f"提取到 {len(text)} 字")

chunks = split_text(text, chunk_size=50, overlap=10)
print(f"切成了 {len(chunks)} 块")

for i, c in enumerate(chunks[:3]):
    print(f"\n[{i}] ({len(c)} 字)")
    print(c)