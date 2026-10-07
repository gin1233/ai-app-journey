# Day 06 · FastAPI（中）：接收数据与自动校验

## 我做了什么

- 新增了 Pydantic 模型 `Note`
- 新增两个接口：`GET /notes`（查看全部）、`POST /notes`（新增一条）
- 用 `/docs` 的 Try it out 提交了数据
- 做了「数据丢失」实验

## GET 和 POST 的区别

| | GET | POST |
|---|---|---|
| 干什么 | 读取数据 | 上传数据 |
| 数据放在哪 | 内存 | JSON |
| 有副作用吗 | | |
| 类比 | 查看账户 | 实际转账 |

**我发送的数据长什么样（POST 的请求体）**：

## Pydantic 模型是什么

```python
class Note(BaseModel):
    """一条笔记。"""
    title: str
    content: str = ""
```

**用自己的话解释这三行**：

- `class Note(BaseModel)`： 创建新的类型 区别去python自带的int，str... BaseModel是pydantic中的notes模板工具调用
- `title: str`： 基于basemodel针对于这个class新加的title
- `content: str = ""`： 基于basemodel针对于这个class新加的content

**登记表类比**（哪些是必填、哪些是选填）：

## 为什么 FastAPI 知道要从「请求体」拿数据

对比这两个函数：

```python
def say_hello(name: str):      # 数据从哪来？
def create_note(note: Note):   # 数据从哪来？
```

**我的理解**：
（提示：看参数的类型是什么 —— 基本类型 vs 模型类）

## 自动校验：三种情况

### 情况 A：缺少必填字段

**我发送的**：
{"content": }

**返回的状态码**：
HTTP 422

**返回的内容**（关键部分）：
| 字段 | 含义 |
|---|---|
| `"type": "missing"` | **问题类型：缺字段** |
| `"loc": ["body", "title"]` | **位置：请求体里的 title** |
| `"msg": "Field required"` | **说明：这是必填项** |
| `"input": {...}` | **你实际发过来的东西** |

**这个报错告诉我什么**：
缺字段

### 情况 B：类型不对（title 传成数字）

**我发送的**：
{"title": 123}

**返回的状态码**：
HTTP 422

**返回的内容**：
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["body", "title"],
      "msg": "Input should be a valid string",
      "input": 123
    }
  ]
}

### 情况 C：多传了没定义的字段
{"title": "正常", "extra": "多余的东西"}
**结果**：

## 🧪 数据丢失实验（重点）
没有报错 —— 多余的字段被忽略了。

**实验步骤与结果**：

1. 提交 2 条笔记
2. `GET /notes` 返回：
3. **改了一下 `main.py` 并保存**（触发 `--reload` 重启）
4. 再 `GET /notes` 返回：

**为什么数据会消失**：
（提示：`notes` 这个列表存在哪里？进程结束时它会怎样？）
notes: list[Note] = [] 存在这里
存在内存里 进程结束小时

**如果我不想数据消失，应该怎么办**：
调用数据库


## 内存 vs 数据库

| | 内存（Python 列表） | 数据库 |
|---|---|---|
| 类比 | 白板 | 记事本 |
| 速度 | 快 | 慢 |
| 进程结束后 | 消失 | 保留 |

**内存存储还有哪些问题**：
（提示：多人同时写？跑多个进程时各存各的？）

| **多人同时写会乱** | 两个请求同时 `append`，列表是共用的，可能出问题 |
| **多台服务器各存各的** | 以后如果跑 2 个进程分摊压力，A 存的笔记，B 根本看不见 |


## 还没搞懂的地方

 - `422` 和 `404` 有什么区别？

 - 为什么 `notes.append(note)` 不用写 `global`？）
 不懂你想问什么

