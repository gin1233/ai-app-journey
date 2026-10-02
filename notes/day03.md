# Day 03 · GitHub 远程仓库

> ⚠️ 这节课是**补记**的。
> 写之前先翻一眼 `git log --oneline --all` 和 GitHub 页面，把当时的动作回忆起来。
> 记不清的地方就写"记不清了"，那说明这块要补。

## 我做了什么

- 注册 / 登录 GitHub，创建了仓库 `https://github.com/gin1233/ai-app-journey`
- 用 `git remote add` 把本地和远程连起来
- 用 `git push -u origin main` 完成了第一次推送
- 之后又推了 1 次（比如加了 `.gitattributes`）
- git push 失败网络原因

## Git 和 GitHub 的区别（用自己的话）
本地 vs 云端

## 为什么在 GitHub 创建仓库时，那三个选项都不能勾？


**我的理解**：
已经在本地创建过了

**如果不小心勾了会怎样**：
创建平行宇宙吧

## 四个名词：用自己的话解释

| 名词 | 我的理解 |
|---|---|
| `origin` | 仓库地址|
| `main` | 坐标信息里面含hash code|
| `HEAD` | 坐标告诉你的位置在哪 |
| `branch`（分支） | 坐标信息 |

（提示：`origin` 是给远程地址起的"代号"；`main` 是分支名；
 `HEAD` 是"我现在站在哪"；分支是"指向某个提交的指针"）

## `git push -u origin main` 里的 `-u` 是干什么的

-u = --set-upstream 这相当于告诉git以后push默认上传到origin



## 今天踩的坑

一次通过

## 还没搞懂的地方

多个远程仓库怎么管？
PS> git remote add origin  https://github.com/gin1233/ai-app-journey.git
PS> git remote add gitee   https://gitee.com/gin1233/ai-app-journey.git
PS> git remote add backup  https://gitlab.com/xxx/ai-app-journey.git
远程分支和本地分支的关系是什么？