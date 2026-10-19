# Day 14 · 测试入门

## 我做了什么

- 建 `tests/test_schemas.py`（4 个单元测试）
- 建 `tests/conftest.py`（测试数据库 + TestClient fixture）
- 建 `tests/test_notes_api.py`（5 个接口测试）
- **故意改坏代码，确认测试变红，再改回来**

## 为什么需要测试

**手测的流程是什么**：
去docs 自己点try it out去测
**接口变多之后会怎样**：
挨个点挨个测
**举个"手测抓不到"的例子**（你自己想的）：
代码功能性没问题 但是可能数据库方面的bug你是观测不到的
## pytest 的三条规则

| 规则 | 说明 |
|---|---|
| 文件名 |以 test_ 开头，或 _test.py 结尾 |
| 函数名 | 以 test_ 开头 |
| 断言 |用 assert —— 成立就过，不成立就失败 |

## 第一个测试：为什么不用数据库

**`app/schemas.py` import 了什么**：
import pytest
from pydantic import ValidationError

from app.schemas import NoteCreate, NoteUpdate
**所以测它需要什么**：
import pytest
from pydantic import ValidationError

from app.schemas import NoteCreate, NoteUpdate
**"纯函数"和"有依赖的函数"，哪个更好测**：
纯函数
跟数据库没关系
## `pytest.raises` 是干什么的

```python
with pytest.raises(ValidationError):
    NoteCreate(title="   ")
```
这段代码应该抛出 ValidationError
**如果这段代码没抛异常，测试会怎样**：
这段代码应该抛出 ValidationError
## `TestClient` 是什么

假浏览器

**它和真的启动 uvicorn 有什么区别**：
它不用启动服务器、不用真的走网络 —— 直接在进程内调用你的应用
**用法和什么很像**：
httpx
## ⭐ 测试数据库隔离（今天最重要）

**如果不隔离，会发生什么**：

| 问题 | 后果 |
|---|---|
| 测试会插入数据 | 真实数据库出现垃圾数据 |
| 测试会删除数据 | 可能删除真实数据 |
| 两个测试之间 | 互相污染 |

**⭐ 为什么"依赖注入"让这件事变简单了**（回看 Day 08 "公司配电脑"）：

不是fixed 灵活

**如果当初写的是 `db = SessionLocal()`，测试还能换掉数据库吗**：
只能在代码端改

**`app.dependency_overrides` 是干什么的**：

行政换成测试

## `conftest.py` 里的三行关键代码

### ① `create_engine("sqlite://", ...)`

**`sqlite://` 是什么**：
内存数据库

**它存在磁盘上吗**：
不存在
### ② `poolclass=StaticPool`

**为什么必须加**：
每个连接都有自己的内存 连在一起
**不加会报什么错**：
报表不能存在 因为不在一起
### ③ `app.dependency_overrides[get_db] = override_get_db`

**这行做了什么**：
换部门
**最后为什么必须 `clear()`**：
清除测试数据 不污染其他测试 “| 两个测试之间 | 互相污染 |”
## fixture 是怎么工作的

```python
def test_create_and_get(client):
```
pytest 看到测试函数的参数叫 client，就去 conftest.py 里找同名的 fixture，自动执行它，把结果传进来。
**`client` 这个参数从哪来**：
来自 conftest.py 里那个 @pytest.fixture() 装饰的函数。
**为什么不用 import**：

## 每个测试为什么是独立的
drop_all
**`test_patch_only_title_keeps_content` 建的笔记，`test_delete_then_get_404` 看得到吗**：

**为什么**：
test_patch_only_title_keeps_content 里建的笔记，test_delete_then_get_404 里看不到 —— 因为每个测试跑完都会 drop_all。
**这对写测试有什么好处**：

## ⭐ 最有价值的那条测试

```python
assert body["content"] == "原内容"
```

**它锁死了哪个坑**（Day 09 学的）：
只改标题时内容被清空
**以后谁不小心删了 `exclude_unset=True`，会发生什么**：
这条测试立刻变红。
## 🎯 红绿实验

**我改坏了哪一行**：
updates = payload.model_dump(exclude_unset=True)
**测试输出（贴关键部分）**：
E       sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) NOT NULL constraint failed: notes.content
E       [SQL: UPDATE notes SET title=?, content=? WHERE notes.id = ?]
E       [parameters: ('新标题', None, 1)]
E       (Background on this error at: https://sqlalche.me/e/21/gkpj)

.venv\Lib\site-packages\sqlalchemy\engine\default.py:1192: IntegrityError
**pytest 告诉我什么**：
IntegrityError
**改回来之后**：
all passed
## 测试的三个层次

| 层次 | 测什么 | 速度 | 我现在有吗 |
|---|---|---|---|
| 单元测试 | 一个函数 / 类的逻辑 | 毫秒级 | v |
| 集成测试 |多个组件合起来（接口 + 库） | 几十毫秒 | v |
| 端到端测试 | 真实浏览器点操作 |秒 | x |

**为什么测试金字塔是"下宽上窄"**：
越往下，跑得越快、越容易定位问题。
**面试题：你们项目测试怎么做的**（写出你的答案）：
"以单元测试为主，覆盖核心业务逻辑；接口层用集成测试覆盖关键路径（创建、404、校验失败）；E2E 只覆盖几条最重要的用户流程。"
⚠️ 答"我们测试覆盖率达到 100%"是外行 —— 覆盖率不等于测试质量。
## ⚠️ 你现在遇到的一个问题

**跑 `pytest` 时，`from app.main import app` 会触发什么**：
Base.metadata.create_all(bind=engine)      # ← 连的是【生产数据库】
**所以跑测试前必须确认什么**：
docker 开没开
**这为什么是个设计问题**：
测试不该依赖生产数据库的存在。


## 还没搞懂的地方

（至少写 1 条。写不出来就回顾这几个：
 - `fixture` 的 `yield` 前后分别在什么时候执行？
    测试的时候执行
 - 如果测试需要"预先插入几条数据"，该怎么写？
 插入到假的数据库里
 - 测试 AI 接口时，怎么避免真的花钱调用大模型？）
monkeypatch 把真函数换成假函数 —— 不改源代码，只在这一次测试里生效。
## 待办

- [ ] 提交推送（⚠️ 确认没有 `.env`）