"""测试笔记接口（集成测试：路由 + 校验 + 数据库）。"""


def test_create_and_get(client):
    """建一条，再查回来。"""
    r = client.post("/notes", json={"title": "测试笔记", "content": "内容"})
    assert r.status_code == 200
    note_id = r.json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "测试笔记"


def test_get_missing_returns_404(client):
    """查不存在的笔记 → 404。"""
    r = client.get("/notes/99999")
    assert r.status_code == 404
    assert r.json()["detail"] == "笔记不存在"


def test_create_with_blank_title_returns_422(client):
    """标题只有空格 → 422。"""
    r = client.post("/notes", json={"title": "   "})
    assert r.status_code == 422


def test_patch_only_title_keeps_content(client):
    """⭐ 只改标题时，内容必须保持原样。"""
    r = client.post("/notes", json={"title": "原标题", "content": "原内容"})
    note_id = r.json()["id"]

    r = client.patch(f"/notes/{note_id}", json={"title": "新标题"})
    assert r.status_code == 200

    body = r.json()
    assert body["title"] == "新标题"
    assert body["content"] == "原内容"        # ← 这条最重要


def test_delete_then_get_404(client):
    """删掉之后，再查应该是 404。"""
    r = client.post("/notes", json={"title": "待删除"})
    note_id = r.json()["id"]

    assert client.delete(f"/notes/{note_id}").status_code == 200
    assert client.get(f"/notes/{note_id}").status_code == 404