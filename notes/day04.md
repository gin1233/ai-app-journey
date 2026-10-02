# Day 04 · Python 工程化基础

## 我做了什么

- 建立了 `app/` 包：`__init__.py` / `config.py` / `env_check.py`
- 装了 `rich` 和 `python-dotenv` 两个库
- 生成 `requirements.txt`
- 学会了用 `python -m` 运行包内的模块

## 模块和包的区别

| 概念 | 是什么 |
|---|---|
| 模块 module | distribution里只含有一个.py文件 |
| 包 package | 有__init__.py 通常是工具箱级别（大）|

`__init__.py` 的作用是：
装箱须知，告诉你这个package里都有什么，版本信息

## 为什么必须用 `python -m app.env_check`

-m 会让python从文件所在的根目录开始检查也就是从c盘出发
pyhton app\env_check.py 脚本所在位置在app文件夹里面由于from app.config import PROJECT_ROOT, show_config 他无法在app文件夹内找到app

**两种运行方式和结果的对比**：

| 命令 | 能跑吗 | 为什么 |
|---|---|---|
| `python app\env_check.py` | | |
| `python -m app.env_check` | | |

## 直接依赖 vs 间接依赖

我敲了 `pip install rich python-dotenv` 装了 **2 个**包，
但 `pip freeze` 输出了 **5 个**。

直接依赖是你调用的东西
间接依赖是你调用的东西还需要调用已完成直接调用的效果

**为什么 `pip freeze` 要把间接依赖也写进去？**

只写直接依赖无法得知间接依赖的版本号，从而引发问题

## 配置管理：为什么要 `.env` 和 `.env.example` 两份

| 文件 | 进 Git 吗 | 内容是什么 | 为什么 |
|---|---|---|---|
| `.env` | | | |
| `.env.example` | | | |

**如果不小心把 `.env` 推到 GitHub 会怎样**：

泄露APIkey

## 今天踩的坑：用文件路径运行包内的模块

**我敲的命令**：
(.venv) PS C:\Users\Administrator\Documents\Codex\ai-app-journey> python app\env_check.py
**报错原文**（一字不改地抄下来，不要凭记忆写）：
Traceback (most recent call last):
  File "C:\Users\Administrator\Documents\Codex\ai-app-journey\app\env_check.py", line 18, in <module>
    from app.config import PROJECT_ROOT, show_config
ModuleNotFoundError: No module named 'app'
**原因**：
因为无法在app文件夹中找app
**正确做法**：
python -m app.env_check

## 还没搞懂的地方

 **`.env.example`** | 🏨 **客房设施说明卡** | **所有人**（放在桌上） | "本房有：空调、保险箱、迷你吧" |
 **`.env`** | 🔑 **房卡** | **只有你** | 真正能开门的那串数据 |