# Day 09 · 补上 U，给 main.py 瘦身

## 我做了什么

- 新增 `app/schemas.py`（三个 Pydantic 模型搬家）
- 新增 `app/routers/notes.py`（笔记接口分家）
- `app/main.py` 从 75 行瘦到 **24 行**
- 新增 `PATCH /notes/{note_id}`（更新接口）
- **验证：PATCH 只传 title 时，content 不被清空**

## CRUD 收尾

| 字母 | 全称 | 接口 | 状态 |
|---|---|---|---|
| C | Create | `POST /notes` | |
| R | Read | `GET /notes`、`GET /notes/{id}` | |
| U | Update | `PATCH /notes/{id}` | |
| D | Delete | `DELETE /notes/{id}` | |

## PUT 和 PATCH 的区别

| | PUT | PATCH |
|---|---|---|
| 语义 | 全部修改 | 局部修改 |
| 请求体必须包含 | | |
| 类比 | 换门 | 换个门把手 |

**为什么这个项目选 PATCH**：

patch是最新最灵活的写法cover了put

## `NoteUpdate` 里的三处新东西

```python
class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, max_length=5000)
```

**① `str | None` 是什么意思**：
可以是str 或是 none

**为什么更新接口需要它**（对比 `NoteCreate` 里的 `title: str`）：
因为用户不一定两个都修改

**② `default=None` 是什么意思**：
默认是none

**③ 校验器为什么要先判断 `if v is None: return v`**：
是none 后面的代码就不用跑了 不用再判断一次是不是空格 代码效率高

## ⭐ `model_dump(exclude_unset=True)` 为什么是关键

```python
updates = payload.model_dump(exclude_unset=True)
```

**`model_dump()` 是干什么的**：

将Pydantic 模型转成字典

**加不加 `exclude_unset=True` 的区别**：
只包含用户真的传过来的字段。

| 用户发的 | `model_dump()` | `model_dump(exclude_unset=True)` |
|---|---|---|
| `{"title": "新的"}` | | |
| `{"title": "新", "content": "内容"}` | | |

**⚠️ 如果不加这个参数，会发生什么严重的 bug**：
跟put没差别了

## `setattr` 是什么
按"名字"给对象的属性赋值。
```python
setattr(note, field, value)
```

**等价于**：
note.title = "新标题"

**为什么不直接写 `note.title = ...`**：
写死了 改变不生效

## ⚠️ 为什么更新不需要 `db.add(note)`

**对比三个接口**：

| 接口 | 要 `db.add()` 吗 | 为什么 |
|---|---|---|
| `create_note` | 要 | 不存在所以add |
| `update_note` | 不用 | 已经存在了只是在基础上进行修改 |

**这用上了 Day 07 学的哪个能力**：

这就是你 Day 07 记的"对象跟踪"能力。 当时你只是抄下来，现在它派上用场了。
对比一下 db.add() 的语义：add 的意思是"这个新对象，请开始跟踪它"。已经跟踪着的，不用再说一遍。

## `APIRouter`：分机类比

| 代码 | 类比 |
|---|---|
| `APIRouter()` | 部门总机 |
| `app.include_router(...)` | 部门总机和公司总机的连接 |

**重构前后对比**：

| | 重构前 | 重构后 |
|---|---|---|
| `main.py` 行数 | 很多 | 变少 |
| 笔记接口在哪 | main.py | notes.py |
| Pydantic 模型在哪 | main.py | schemas.py |

## ⚠️ `@router.get("")` 的坑

```python
router = APIRouter(prefix="/notes")

@router.get("")      # 最终路径是？ /notes
@router.get("/")     # 最终路径是？ /notes/
```

**为什么用空字符串 `""` 而不是 `"/"`**：

prefix="/notes"

## ⚠️ `Base.metadata` 的隐式依赖

**`main.py` 里已经删掉了 `from app.models import Note`，为什么建表还是成功的？**
调用了notes的部门总机里的from app.models import Note

（提示：`app/routers/notes.py` 里 import 了什么？`Base.metadata` 是什么？）

**如果哪天所有 router 都被删掉，会发生什么**：
不工作

**保险写法是什么**：
在main.py 加上

## 🧪 我的验证结果

**PATCH 只传 title 前后对比**：

| 步骤 | title | content |
|---|---|---|
| POST 建的时候 | 新的 | 新的 |
| PATCH `{"title":"新标题"}` 之后 | {"title":"新标题"} | content 不变|

**`content` 有没有被清空**：
patch不清空 unless你给新的值

**PATCH 不存在的 id 返回**：
status_code=404, detail="笔记不存在"

**PATCH 空标题返回的状态码和内容**：
code200 title不变 内容是新的内容
## 今天踩的坑 / 面试官可能追问的点

> 本节课没有踩到实际报错，所以这一栏改成"面试官可能追问的点"。
> 每题格式：**问题 → 答案 → 追问方向**。

---

### 1. `exclude_unset=True` 和 `exclude_none=True` 有什么区别？

**这是 PATCH 接口最容易被追问的一点。**

```python
class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
```

| 用户发的 | `exclude_unset=True` | `exclude_none=True` |
|---|---|---|
| `{"title": "新"}` | `{"title": "新"}` | `{"title": "新"}` |
| **`{"title": "新", "content": null}`** | `{"title": "新", "content": None}` | **`{"title": "新"}`** ← 意图被丢掉 |

**区别的本质：**

| 参数 | 判断依据 |
|---|---|
| `exclude_unset` | **用户有没有传这个字段** |
| `exclude_none` | **这个字段的值是不是 None** |

**为什么这个区别要命？**

用户**主动想清空 content**（发 `{"content": null}`）时：

- `exclude_unset=True` → 字典里有 content → **真的清空** ✅
- `exclude_none=True` → 字典里没 content → **看起来清空了，实际没动** ❌

**结论：做 PATCH 用 `exclude_unset=True`，不要用 `exclude_none=True`。**

**追问**：那什么时候用 `exclude_none`？
→ 生成响应数据时，把值为 None 的字段从 JSON 里去掉（不想显示 `"xxx": null`）。

---

### 2. `setattr(note, field, value)` 按字段名赋值，会不会有安全问题？

**会。这叫「批量赋值漏洞」（Mass Assignment），是后端最经典的安全问题之一。**

**先看一个会出事的例子。**

假设以后给 `Note` 加了 `owner_id`（笔记属于谁），你顺手也加进了 `NoteUpdate`：

```python
class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    owner_id: int | None = None        # ← 危险
```

**任何人都可以这样发：**

```json
{"title": "我的笔记", "owner_id": 1}
```

**结果：笔记被写到"用户 1"名下。**

**更狠的例子**：如果模型里有 `is_admin` 之类的字段，用户就能**把自己提权**。

**为什么我们现在的代码是安全的？**

**因为 Pydantic 模型本身就是「白名单」。**

用户发 `{"owner_id": 1}` 时，`NoteUpdate` 里没声明这个字段 → **Pydantic 直接忽略** → `model_dump()` 里根本不会出现 `owner_id`。

**所以 `setattr` 只能改"模型里声明过的字段"。**

**三层防御，从松到严：**

| 做法 | 效果 |
|---|---|
| ① 敏感字段不写进 Update 模型（默认行为） | 用户发了也没用，**静默忽略** |
| ② `model_config = ConfigDict(extra="forbid")` | 用户发了没声明的字段 → **直接 422**，让他知道发错了 |
| ③ 敏感字段单独走"管理员接口" | 从接口层面隔离 |

**推荐加上第 ② 条：**

```python
class NoteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    content: str | None = None
```

**好处**：用户拼错字段名（`titel`）时会立刻被拒绝，而不是"看起来保存成功，其实啥也没改"。

**⭐ 这里连接回 Day 06**

Day 06 讲"为什么把 NoteCreate / NoteUpdate / NoteRead 拆成三个模型"，当时的理由是**数据结构不同**。现在补上第二个理由：**权限不同。**

| 模型 | 谁能决定字段 |
|---|---|
| `NoteCreate` | 用户**能填**的 |
| `NoteUpdate` | 用户**能改**的（比能填的更少） |
| `NoteRead` | **愿意让用户看到的**（可能隐藏内部字段） |
| `Note`（models.py） | 数据库需要的（**用户永远不该直接决定**） |

**⚠️ 面试官问"你的 PATCH 接口安全吗"，答"我用独立的 Update 模型做白名单，敏感字段不放进去"，这是满分答案。**

---

### 3. PUT 和 PATCH 的区别？PATCH 幂等吗？

**第一问（你已经答对了）：**

| | PUT | PATCH |
|---|---|---|
| 语义 | 整体替换 | 局部更新 |
| 请求体必须包含 | **全部字段** | **只发要改的** |
| 漏发字段的后果 | **被清空** | **保持原样** |

**第二问是真正的考点 —— "PATCH 幂等吗？"**

**答：HTTP 规范里，PATCH 不要求幂等。**

| 方法 | 幂等？ |
|---|---|
| GET | ✅ |
| PUT | ✅ |
| DELETE | ✅ |
| POST | ❌ |
| **PATCH** | **❌ 规范上不要求** |

**"幂等" = 同一个请求发 1 次和发 100 次，服务器的最终状态一样。**

**为什么 PATCH 不保证幂等？** 因为它允许"**增量式**"的语义：

```json
{"op": "add", "field": "views", "value": 1}
```

发 100 次，浏览量涨 100。**不幂等。**

**但——我们这个实现事实上是幂等的：**

```json
{"title": "新标题"}
```

发 1 次、100 次，`title` 都是 `"新标题"`。**因为 `setattr` 是「覆盖」，不是「累加」。**

> **面试官问这个，想听的是**："规范上不要求幂等，但我这个实现是幂等的，因为它是覆盖语义。"

---

### 4. 更新接口为什么不用 `db.add(note)`？

**答**：`note` 是从数据库**查出来**的，已经被会话跟踪了。我改它的属性，会话会发现对象变"脏"了，`commit()` 时自动生成 `UPDATE`。

**追问 A：那 `db.add()` 到底做了什么？**

→ **它不是"存进数据库"，而是"把对象登记进会话，让会话开始跟踪它"。**

| 场景 | 需要 `add` 吗 | 为什么 |
|---|---|---|
| 新建对象 | ✅ | 会话还不认识它 |
| 从数据库查出来的 | ❌ | 会话已经在跟踪了 |
| 删除 | 用 `db.delete()` | 同样是"登记一个动作"，不是立刻执行 |

**追问 B：那真正的"落库"发生在什么时候？**

→ **`db.commit()` 那一刻。** 之前所有操作都只是"记在会话的记事本上"。

**追问 C：`commit()` 之后对象还能用吗？**

→ 默认 `expire_on_commit=True`，commit 后对象属性会**过期**，下次访问 `note.id` 时会**自动去数据库重查一遍**。

> **这就是 Day 07 讨论"为什么要有 `refresh`"的根源** —— 不写 `refresh` 也能拿到 id，就是这个机制在起作用。

---

### 5. `@router.get("")` 和 `@router.get("/")` 有什么区别？

**答**：`prefix="/notes"` 时，`""` → `/notes`，`"/"` → `/notes/`。

**追问 A：`/notes/` 会怎样？**

→ 用户访问 `/notes` 会被 **307 重定向**到 `/notes/`。功能上能用，但多一次往返，`/docs` 里显示的路径也别扭。

**追问 B：`APIRouter` 还有哪些参数？**

| 参数 | 作用 |
|---|---|
| `prefix` | 路径前缀 |
| `tags` | `/docs` 文档分组 |
| **`dependencies`** | **整组共享的依赖** |
| `responses` | 预设响应说明 |
| `deprecated` | 标记整组废弃 |

**`dependencies` 的用途 —— "依赖注入"的第二次应用：**

```python
router = APIRouter(
    prefix="/notes",
    tags=["笔记"],
    dependencies=[Depends(require_login)],
)
```

**写一次，组里 5 个接口自动全部带上登录校验**，不用在每个接口里各写一遍。

---

### 6. `Base.metadata.create_all()` 是怎么知道要建哪些表的？

**答**：`Base` 是所有表模型的基类。每写一个 `class Xxx(Base)`，SQLAlchemy 就把这张表**登记进 `Base.metadata`**。`create_all` 是按这本"登记簿"施工的。

**追问 A：为什么 `main.py` 里删掉了 `from app.models import Note`，建表还是成功的？**

→ 因为 `include_router(notes.router)` 加载了 `routers/notes.py`，那里有 `from app.models import Note`。

**import 的副作用不只是"拿到名字"，还会"执行那个文件"。** `models.py` 被执行 → `Note` 类被定义 → 登记簿上有了一笔。

**追问 B：这是好事吗？**

→ **不是，这是「隐式依赖」，是坏味道。** 如果哪天某个 router 被删掉，`models` 就没人 import，`create_all` 会以为"一张表都没有"。

**保险写法（放 `main.py` 顶部）：**

```python
from app import models  # noqa: F401
```

**追问 C：在 `models.py` 里加一个字段，`create_all` 会更新表结构吗？**

→ **不会。** `create_all` 只做一件事：**表不存在就建，存在就跳过**，它**不比较结构差异**。

→ 改结构要用迁移工具 **Alembic**，它会把"从 v1 到 v2 改了什么"写成脚本，进 Git，团队共享。

---

## 还没搞懂的地方

（至少写 1 条。写不出来就回顾这几个：
 - `str | None` 和 `Optional[str]` 有什么区别？
 不会
 - 如果 PATCH 要支持"把 content 改成空字符串"，现在这套写法能做到吗？
 能
 - `APIRouter` 的 `prefix` 和 `tags` 还有什么别的参数？）
不知道
