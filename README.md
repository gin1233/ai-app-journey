# AI 应用工程师 · 学习历程

> 从「会一点 Python」到「能独立交付 LLM 应用」的转型记录。
> 每一天的代码、笔记和踩过的坑，都在这个仓库里。

## 关于我

- 前端背景（HTML / CSS / JavaScript），后端从零开始
- 目标岗位：AI 应用工程师（LLM 应用 / RAG / Agent 方向）
- 起点：2026-09-29

## 这个仓库记录什么

不只是「学了什么」，更重要的是：

- **每天能跑的代码** —— 不是抄来的
- **用自己的话写的笔记** —— 不是复制粘贴的
- **真实踩过的坑** —— 报错原文 + 原因分析 + 解决方案

## 学习进度

| 阶段 | 内容 | 状态 |
|---|---|---|
| Day 01 | 环境搭建、虚拟环境、项目结构 | 完成 |
| Day 02 | Git 版本控制基础 | 完成 |
| Day 03 | 连接 GitHub 远程仓库 | 完成 |
| Day 04 | Python 工程化基础 | 进行中 |
| Day 05+ | FastAPI / 数据库 / LLM 接入 / RAG / Agent | 待开始 |

## 目录结构

    ai-app-journey/
    ├── day01/                  Day 01 练习：环境自检脚本
    ├── notes/
    │   ├── day01.md            Day 01 学习笔记
    │   ├── day02.md            Day 02 学习笔记
    │   └── git-cheatsheet.md   Git 速查手册
    ├── .gitattributes          统一换行符规则
    ├── .gitignore              Git 忽略规则
    └── README.md               本文件

## 环境要求

- Python >= 3.12（当前使用 3.14.7）
- Git >= 2.40
- VS Code

## 快速开始

    # 1. 创建虚拟环境
    python -m venv .venv

    # 2. 激活虚拟环境（PowerShell）
    .\.venv\Scripts\Activate.ps1

    # 3. 运行环境自检
    python day01\check_env.py

## 笔记索引

- [Day 01 · 环境搭建](notes/day01.md)
- [Day 02 · Git 基础](notes/day02.md)
- [Git 速查手册](notes/git-cheatsheet.md)