# Day 07 · 接入 PostgreSQL：让数据活下来

## 我做了什么

- 用 `docker-compose.yml` 起了 PostgreSQL 容器
- 装了 `sqlalchemy` 和 `psycopg[binary]`
- `.env` 里配置了 `DATABASE_URL`
- 新建 `app/database.py`、`app/models.py`，改造 `app/main.py`
- **验证：重启服务后数据还在**

## 为什么用 Docker 起数据库，而不是直接装

| | 直接装 | Docker |
|---|---|---|
| 装在哪 | 污染你系统的环境 | **隔离在容器里** |
| 卸载 | 麻烦，容易留残留 | **删掉容器就行** |
| 换版本 | 要卸载重装 | **改一行 `image:` 就行** |
| 换台电脑 | 要重装一遍 | **`docker compose up -d`** 一条命令 |

**我的理解**：

## `docker-compose.yml` 逐块解释

```yaml
services:
  db:
    image: postgres:17
    container_name: aiapp-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: aiapp
      POSTGRES_PASSWORD: aiapp_dev_pw
      POSTGRES_DB: aiapp
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

| 配置 | 作用 |
|---|---|
| `image` | 镜像用的是什么 postgre：17 17是版本号|
| `restart` | restart: unless-stopped 开机自启 |
| `environment` | 初始化环境 用户名 密码 数据库名 |
| `ports: "5432:5432"` | 端口 将数据库和电脑连通 |
| `volumes` | 数据库存储位置 |

## ⭐ `volumes` 是整份配置里最重要的一行

**为什么？**（提示：容器默认是什么特性？删掉容器数据会怎样？）
docker不用了删除了也可以保留数据
**我的理解**：
容器像是docker租的房子 数据存在里面 搬走了就消失了
volume则是在房子外面租的仓库，就算房子不租了数据也会保留在仓库里面
**用杯子类比**：
一次性vs永久
**我实测的验证**（`docker compose down` 再 `up -d` 之后，数据还在吗？）：
在

## SQLAlchemy 三件套

| 名字 | 在哪 | 是什么 | 类比 |
|---|---|---|---|
| `engine` | database.py | 翻译官将sql语言和python语言打通 并且能翻译方言 可以将python指令翻译成不同sql语言适配 | 电信局  |
| `SessionLocal` | database.py | 工厂 | 营业厅|SessionLocal（）才是会话
| `Base` | database.py | 模板并且登记"我一共有哪些表 | |

## ⚠️ 两个 `Note` 的区别（重要）

| 名字 | 在哪 | 是什么 | 代表 |
|---|---|---|---|
| `Note` | models.py | 约定python和sql指令如何映射 | 不知道你想让我填什么|
| `NoteCreate` | main.py | 提交笔记时的格式（输入） | |
| `NoteRead` | main.py | 返回笔记时的格式（输出）| |



## `model_config = ConfigDict(from_attributes=True)` 是干什么的

（提示：`return note` 返回的是字典还是 SQLAlchemy 对象？）

让pydantic可以将note当成属性去读 但是并不是将note实际去转化成字典
(from_attributes=True) pydantic 本身不具备读属性的能力（默认读属性dic），这个相当于给他开了读属性的权限

**如果不加这一行会怎样**：
500 报错

## `add` / `commit` / `refresh` 三步

```python
note = Note(title=..., content=...)
db.add(note)
db.commit()
db.refresh(note)
```

不加commit 不工作

**用银行办理业务的类比解释这四步**：

| 代码 | 类比 |
|---|---|
| `Note(...)` | 填表 |
| `db.add(note)` | 提交表格 |
| `db.commit()` | 收到表格工作 |
| `db.refresh(note)` | 给回执 |

**为什么 `refresh` 是必须的**：
（提示：`id` 是谁生成的？不 refresh 拿得到吗？）

refresh赋值拿到的

## 连接串拆解

```
DATABASE_URL=postgresql+psycopg://aiapp:aiapp_dev_pw@localhost:5432/aiapp
```

| 部分 | 含义 |
|---|---|
| `postgresql+psycopg` |协议 + 驱动 |用什么方式连：postgresql 是数据库类型，psycopg 是 Python 驱动
| `aiapp`（冒号前） | 用户名 |登录数据库的账号
| `aiapp_dev_pw`（冒号后） |密码 |登录数据库的密码
| `localhost` | 主机 | 数据库在哪台机器上（localhost = 本机）
| `5432` | 端口 | 从哪个门进（PostgreSQL 的默认端口）
| `aiapp`（斜杠后） | 数据库名 | 进哪个库 —— 一台服务器上可以有多个库

| 部分 | 类比 |
|---|---|
| `postgresql+psycopg` | **你用什么交通工具来**（开车 / 坐地铁） |
| `aiapp` + `aiapp_dev_pw` | **门口的工牌和密码** —— 保安要核对 |
| `localhost:5432` | **哪栋楼、哪个门** |
| `/aiapp` | **进去之后去哪个房间** —— 一栋楼里有很多房间 |

协议://用户名:密码@主机:端口/库名

**为什么这串东西要放在 `.env` 里，不能写死在代码里**：

会泄露关键信息

| 场景 | 写死在代码里 | 放 `.env` 里 |
|---|---|---|
| 你本地开发 | 要改代码 | **改 `.env`** |
| 部署到服务器 | **又要改代码，还要重新提交** | **在服务器上写一份 `.env` 就行** |
| **密码换了** | **代码要重新提交、重新部署** | **改 `.env` 重启** |
| 多人协作 | **每个人的密码都不同，代码冲突** | **各写各的 `.env`** |

## 🧪 我的验证结果

**表结构**（用 `docker compose exec db psql` 或 Python 查出来的）：
？
**提交数据前** `GET /notes` 返回：
nothing
**提交 2 条后** `GET /notes` 返回：
[{"id":1,"title":"string","content":"t"},{"id":2,"title":"string","content":"ww"}]
**重启服务器后** `GET /notes` 返回：
[{"id":1,"title":"string","content":"t"},{"id":2,"title":"string","content":"ww"}]
**删掉容器重建后** `GET /notes` 返回：
[{"id":1,"title":"string","content":"t"},{"id":2,"title":"string","content":"ww"}]
## 今天踩的坑

**我做的操作**：

**现象**：

**原因**：

**正确做法**：

## 还没搞懂的地方

（至少写 1 条。写不出来就回顾这几个：
 - 为什么用 `SessionLocal()` 而不是直接操作 `engine`？
 | | engine | session |
|---|---|---|
| 是什么 | **通往数据库的管道** | **一次具体的操作过程** |
| 类比 | **电信局**（保证线路通） | **一通电话**（谈成什么事） |

| 问题 | 说明 |
|---|---|
| **① 要手写 SQL** | 那你用 ORM 干嘛？等于白装了 |
| **② 没有事务边界** | 你做 5 个操作，没法保证"要么全成功、要么全回滚" |
| **③ 没有对象跟踪** | 你写 `note.title = "新标题"`，SQLAlchemy **不会自动知道**该生成 UPDATE |

Session 给了你这四样东西
| 能力 | 说明 |
|---|---|
| **ORM 查询** | `db.query(Note).all()`，不用写 SQL |
| **对象跟踪** | 你改对象属性，commit 时**自动生成** UPDATE |
| **事务边界** | 一个 `with` 块 = 一个事务，**要么全成功、要么全回滚** |
| **身份映射** | 同一条记录只对应一个 Python 对象，不会重复创建 |

 - `with SessionLocal() as db:` 这个 `with` 是什么语法？不用它行不行？
 借 autoclose 可以但是怕你忘记close 坑是不会直接报错 会在100条之后报错 排查困难
 类比：顶了酒店人走了房卡没还，理论上不影响但酒店系统会显示你还在入住，直到酒店房间在系统中订满，实际没人住，但是系统会告诉你住满了

 - 表已经存在了，如果再改 `models.py` 加一个字段，数据库会自动更新吗？）
不会 "表不存在 → 创建。Base.metadata.create_all(bind=engine) = 表已存在 → 什么都不做。" 它不检查"结构变了没有"。
迁移工具	"房子有了，我要在墙上开个窗户。" —— 它记录"从 v1 到 v2 改了哪些结构"
  主流工具叫 Alembic（SQLAlchemy 官方出品）。它做的事：
    PS> alembic revision --autogenerate -m "给 notes 表加 created_at"
    PS> alembic upgrade head

    | 能力 | 说明 |
    |---|---|
    | **自动对比** | 对比"代码里的表结构"和"数据库里的实际结构" |
    | **生成脚本** | 改了什么，写成一份**可读的 Python 文件** |
    | **脚本进 Git** | **团队每个人都能执行它**，把数据库升到同一版本 |
    | **能降级** | `alembic downgrade` —— **能反悔** |

## 待办

- [ ] 提交推送
- [ ] 清理误建的文件（`notes/s` 那个）