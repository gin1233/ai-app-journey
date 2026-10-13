# Day 10 · 接入大模型 API

## 我做了什么

- 申请了 `__________` 平台的 API Key
- 装了 `openai` SDK
- `.env` 里配置了 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`
- 新建 `app/services/llm.py`（业务层）
- 新建 `app/routers/ai.py`，新增 `POST /ai/chat`
- 命令行验证通过 → `/docs` 里测通

## 我用的平台

| 项目 | 值 |
|---|---|
| 平台 | |
| `LLM_BASE_URL` | |
| `LLM_MODEL` | |
| 大概价格 | |

## 为什么用 "OpenAI 兼容格式"

**我的理解**：

大部分模型都兼容

**"OpenAI SDK" 和 "OpenAI 公司的模型" 是同一件事吗**：

openai sdk是python调用的一种工具 openai的模型是llm

**这样设计对我的实际好处**：

兼容市面大部分模型，想用别的模型直接换key换baseurl就行 省的大改

## `messages` 的三种 role

```python
messages=[
    {"role": "system", "content": "你是一个乐于助人的助手。"},
    {"role": "user", "content": "你好"},
]
```

| role | 谁说的 | 作用 |
|---|---|---|
| `system` | 我说的 | 告诉ai模型需要扮演的角色 |
| `user` | 使用者 | 问问题（prompt） |
| `assistant` | AI(llm) | 回答 |

**多轮对话是怎么实现的**（提示：历史消息放哪）：
message

## 为什么取值要写三层

```python
response.choices[0].message.content
```

| 层级 | 为什么存在 |
|---|---|
| `.choices` | 是一个「列表」 —— 因为你可以让模型一次生成多个候选回复 默认为1|
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    n=3,          # ← 让它生成 3 个候选答案)# 这时 response.choices 里就有 3 个元素
| `[0]` |取第一个 |
| `.message` | message={} |
| `.content` | 取message中的content |

**`or ""` 是干什么的**：

content要么是 str要么是 none，如果模型的回答是none 会报错 所以'' 用字符串兜底不会报错 或者改成“目前无法回答”

## 为什么要单独搞一个 `services/` 层

逻辑拆分

**分层的三个好处**：

routers 里不出现一句大模型的代码 —— 它只管"收到请求、返回响应"
换模型只改 services/llm.py 一个文件
以后加日志、重试、缓存，全在这一个地方改

## ⭐ 为什么必须先在命令行验证

```
PS> python -c "from app.services.llm import chat; print(chat('你好'))"
```

**如果直接在接口里测，报错了会有什么问题**：

如果直接在接口里测，报错了你分不清是哪一层的问题：

**先跑通命令行，等于确认了什么**：

确认了"service 层是好的

**这叫什么排查思路**（Day 07 的 Docker 排障也用过）：

分层排查

## 错误处理：6 个状态码

| 状态码 | 名字 | 什么时候用 |
|---|---|---|
状态码	名字	什么时候用
200	OK	成功
422	Unprocessable Entity	用户发的数据不合法
429	Too Many Requests	请求太频繁 / 额度用完
502	Bad Gateway	我调用的上游崩了
504	Gateway Timeout	我调用的上游超时了

**⭐ 关键区分**：

| 谁的错 | 用什么码 |
|---|---|
| 用户发错了 | 400 / 422 |
| 我的服务崩了 |500 |
| 我调用的第三方崩了 |502 / 504 |


**`/docs` 里 `/ai/chat` 的请求体**：

**返回的 `reply`**：

## 今天踩的坑

**我做的操作**：

服务器没连上

**现象**（报错原文一字不改）：
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: 5432, hostaddr: '::1': connection timeout expired
- host: 'localhost', port: 5432, hostaddr: '127.0.0.1': connection timeout expired
**原因**：

忘记开了docker

**正确做法**：

开docker

## 还没搞懂的地方

（至少写 1 条。写不出来就回顾这几个：
 - `temperature` 参数是干什么的？默认值是多少？
temperature 控制"随机性 / 创造性"。

| 值 | 效果 | 适合场景 |
|---|---|---|
| **0** | 几乎确定，每次答得一样 | **抽取、分类、写代码** |
| 0.7 左右（常见默认） | 平衡 | 日常对话 |
| 1.5+ | 很发散 | 创意写作 |


 - 一次对话花了多少钱？怎么估算？
 花费 = 输入 token 数 × 输入单价 + 输出 token 数 × 输出单价

 - 如果用户发一句 10 万字的话，会怎样？）
 发不出去 limit是4000写在prompt限制里
模型本身也有上下文上限（比如 64K / 128K token）。