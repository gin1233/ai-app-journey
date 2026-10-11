# Day 08 · 查询单条、删除，以及 404 到底从哪来

## 我做了什么

- `app/database.py` 新增 `get_db` 依赖
- `app/main.py` 改造：所有接口改用 `Depends(get_db)`
- 新增 `GET /notes/{note_id}`（查询单条）
- 新增 `DELETE /notes/{note_id}`（删除）
- 验证了**两种 404 的区别**

## CRUD 盘点

| 字母 | 全称 | 中文 | 接口 | 状态 |
|---|---|---|---|---|
| C | Create | 增 | `POST /notes` | |
| R | Read | 查全部 | `GET /notes` | |
| R | Read | 查单条 | `GET /notes/{id}` | |
| U | Update | 改 | —— | |
| D | Delete | 删 | `DELETE /notes/{id}` | |

## `GET /notes/{note_id}` 里那行链式调用

```python
note = db.query(Note).filter(Note.id == note_id).first()
```

| 部分 | 干什么 | 对应 SQL |
|---|---|---|
| `db.query(Note)` | 遍历Note | |
| `.filter(Note.id == note_id)` | filter Note.id == note_id | |
| `.first()` | 拿到第一个 | |

**⚠️ 为什么 `.filter()` 里用 `==` 而不是 `=`**：

= 是赋值 ==是指相同对应

**如果 `first()` 没找到数据，返回的是什么**：

status_code=404, detail="笔记不存在"

## ⭐ 两种 404 的区别（今天的核心）

**场景 ①：访问不存在的路径**

我访问的地址：.../notesx
返回的状态码：404
返回的内容：{"detail":"Not Found"}
**这是谁产生的 404**：FastAPI

**场景 ②：路径对，但数据不存在**

我访问的地址：.../notes/999
返回的状态码：404 Error: Not Found
返回的内容：{"detail":"笔记不存在"}
**这是谁产生的 404**：get_note

**为什么 FastAPI 不能自动处理场景 ②**：
（提示：FastAPI 知道哪些路径存在，但它知道 id=999 在不在数据库里吗？）

?

**用"找办公室"的类比**：

| 类型 | 类比 |
|---|---|
| ① 路径不存在 | 找不到办公室 |
| ② 数据不存在 | 办公室里找不到东西 |

## `raise HTTPException` 是什么

```python
raise HTTPException(status_code=404, detail="笔记不存在")
```

| 部分 | 作用 |
|---|---|
| `raise` |告诉fastapi 转成HTTP报错 并中断函数运行 |
| `HTTPException` | FastAPI 专门准备的异常类型 |
| `status_code` | 告诉 FastAPI "用 404 这个状态码回复" |
| `detail` | 放进响应体的说明 |

**为什么用 `raise` 而不是 `return`**：

raise 会中断函数运行
return 会接着运行后续代码

## `DELETE` 的最后两步

```python
db.delete(note)
db.commit()
```

**这两步分别在干什么**（继续用银行办事的类比）：
db.delete(note) 提交删除申请
db.commit() 确认删除请求


**如果只写了 `db.delete()` 不写 `db.commit()` 会怎样**：
没删掉

**为什么这个接口没有 `response_model`**：
没有对象可返回，但是你会收到提醒{"message": "已删除", "id": note_id}

## `Depends` 依赖注入

**没有 Depends 的时候，每个接口都要写**：

```python
def list_notes():
    with SessionLocal() as db:
        ...
```

**用了 Depends 之后**：

```python
def list_notes(db: Session = Depends(get_db)):
    ...
```

**"依赖注入"用公司配电脑的类比怎么理解**：
就是省去了你自己去配电脑，只需要告诉公司相关部门给你配一台就好离职在还回去就好


**`db: Session = Depends(get_db)` 这行拆开看**：

```python
db : Session  =  Depends(get_db)
└┬┘  └──┬──┘     └─────┬──────┘
```

| 部分 | 作用 |
|---|---|
| `db` | 名字 variable |
| `: Session` | 注释给人看的 |
| `= Depends(get_db)` | 用get_db的方法去生成一个session|

**哪个部分是 FastAPI 真正在用的**：

## ⭐ `yield` 是什么

**先用最小例子理解**：

```python
def demo():
    print("A：我开始了")
    yield "给出去的东西"
    print("C：我又回来了")

for x in demo():
    print("B：我拿到了", x)
```

**输出的顺序是**：

**`yield` 和 `return` 的区别**：

| | `return` | `yield` |
|---|---|---|
| 交出去值之后 | 不管了 | 等着收盘子 |

**在 `get_db` 里的执行顺序**：

```
请求进来
   ↓
db = SessionLocal()
   ↓
yield db
   ↓
【你的接口函数运行】
   ↓
接口返回（或报错）
   ↓
???
```

**问号那里执行的是什么，为什么一定会执行**：

db.close()

**这和 Day 07 那个"酒店房卡"的类比有什么关系**：
一样 不写是隐藏隐患在酒店房间满了之后开始报错


## ⚠️ 路由顺序的坑

```python
@app.get("/notes")            # 先
@app.get("/notes/{note_id}")  # 后
```

**如果以后你写这两个，哪个必须放前面？为什么**：

```python
@app.get("/users/{user_id}")
@app.get("/users/me")
```

@app.get("/users/me") 这个 因为users/me符合users/{user_id}逻辑会被覆盖

## 🧪 我的验证结果

**测试 1**：`GET /notes/99999` 返回
{"detail":"笔记不存在"}

**测试 2**：`GET /notesx` 返回
{"detail":"Not Found"}
**测试 3**：删除后再查，返回

## 今天踩的坑

**代码相关的**：
| | `with SessionLocal() as db:` | `Depends(get_db)` |
|---|---|---|
| **要写几遍** | **每个接口抄一遍** | **只写一次** |
| **测试时换假的** | ❌ 换不了 | ✅ 一行搞定 |
| **加全局逻辑**（记日志、统计耗时） | ❌ 要改 N 个地方 | ✅ 改 1 个地方 |
| **接口代码长什么样** | 多一层缩进 + 3 行样板 | 一行参数声明 |

## 还没搞懂的地方

（至少写 1 条。写不出来就回顾这几个：
 - `Depends` 里的函数可以有多个吗？比如同时要 db 和当前用户？
 不懂
 - 如果接口里抛了异常，`db.commit()` 没执行，数据会怎样？
 没有保存到数据库
 - `db.query()` 和 SQLAlchemy 2.0 的 `select()` 有什么区别？）
应该没区别
## 待办

- [ ] 提交推送