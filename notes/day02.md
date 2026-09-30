# Day 02 · Git 基础

## 我做了什么

- 配置了 Git 身份（user.name / user.email）
- 跑通了 git init → git add → git commit → git log 完整流程
- 一共产生了 4 个提交

## 三个区域（自己画一遍，别抄）

要求：把"工作区 → 暂存区 → 版本库"这条链路**用自己的话和箭头画出来**，
并在箭头旁边标上是哪个命令让它动了。

首先是自己的文件夹 —— 缓冲区（纸箱）—— 版本库
文件夹也就是自己的工作台，就像上班一样你会出好几版 通过git add将他们都放进自己的电脑里面存着（这是类比这里的电脑就是缓冲区），最后查看缓冲区决定发布发给领导（版本库）

Git的作用
-时间机器 hash id 回溯
-allows 多人更改同一段代码，将相同位置改动标注，标注给参与者决策 ————衍生：Git冲突 hint：解释冲突形成的原因，而不是讲技术
-证据链 - 面试官打开你的github能看到你的提交记录

| **CR 回车** | **横向**（回到行首） | `Home` | `0D` |
| **LF 换行** | **纵向**（下一行） | `↓` | `0A` |

回溯 git switch --detach 8f3a1c2

## 为什么 add 和 commit 要分两步

（用自己的话解释。最好举一个"你今天同时改了 3 个文件，想分 3 次提交"的场景）

## 今天踩的坑：把命令输出粘进了终端 ⭐

### 坑1：git add 报 "LF will be replaced by CRLF"
现象：git add 时刷出一堆 warning
原因：Git 装了 core.autocrlf=true（写在 D:\Git\etc\gitconfig，
     系统级配置，安装时选的 "Checkout Windows-style,
     commit Unix-style" 写入的）
     → 提交时 CRLF 转 LF，检出时 LF 转 CRLF
性质：warning 不是 error，提交正常

延伸：CRLF = 0D 0A（2字节），LF = 0A（1字节），肉眼无法区分
     真正的危险不是两种风格本身，而是"仓库里混着两种风格"
     —— 有人用 autocrlf=false 把 CRLF 文件提交了，
     之后别人提交时整份文件被规范化，diff 显示全文改动
解决：加 .gitattributes 把规则写进项目，优先级高于个人配置

### 坑 2：Git 报 dubious ownership 拒绝工作
现象：git status 报 "detected dubious ownership"，
     说仓库属于 CodexSandboxOffline，但当前用户是 Administrator
原因：Git 2022 年加入的安全特性 —— 别人拥有的仓库里
     可能藏着会执行恶意代码的配置，所以直接拒绝
解决：用 takeown 把文件夹所有权拿回来
     （备用方案：git config --global --add safe.directory）

## 还没搞懂的地方

下面是几个"你可能其实没搞懂"的自检问题，挑你答不上来的写进来：

- [hash code 回溯id] commit 后面那串乱码（4d36c4f）是什么？为什么这么长？
- [不会 ] `.gitignore` 里已经写进去的文件，之后再改它还会被跟踪吗？

**我的疑问**：
（至少写 1 条，写不出来就从上面挑一条你答不上来的）
- [] `HEAD` 是什么意思？  - [] 分支（branch）是干什么用的？
head是我目前的坐标是什么，branch则是这个坐标id名字一样的东西，git不会每次都自动生成branch是因为怕垃圾宇宙太多容易混淆视听，就像dc最后会重启宇宙。所以git将是否创建平行宇宙的权利交给了使用者，如果想保留平行宇宙就get switch -c XXX 去生成一个branch来保留。
branch 分支本质上只是一个"指针" —— 就是 .git 目录下一个几十字节的小文件，里面存着一串哈希值。
git branch                    # 看有哪些分支（当前分支前面有个 *）
git switch -c feature-x       # 创建并切到新分支  ← 创建时最常用
git switch feature-x          # 切换到已有分支
git switch main               # 切回 main
git merge feature-x           # 把 feature-x 合并到当前分支
git branch -d feature-x       # 删掉分支（已合并的）
git branch -D feature-x       # 强制删掉（未合并的）

- [] 如果我 commit 之后发现有错，怎么改？
情况 A：还没 push，只是提交信息写错了： git commit --amend -m "修正后的提交信息"
情况 B：还没 push，漏加了文件：git add 忘记的文件.py git commit --amend --no-edit --no-edit = "提交信息不用改，保持原样"。
情况 C：还没 push，代码本身写错了：# 1. 改好代码 # 2. 提交 git add . git commit -m "fix: 修正 xxx 的逻辑错误"
情况 D：想撤销提交，但保留改动：三种方案
git reset --soft HEAD~1      # 撤销最近 1 次提交，改动回到"纸箱"
git reset HEAD~1             # 撤销提交，改动回到"工作区"（默认）
git reset --hard HEAD~1      # ⚠️ 撤销提交并【丢弃】改动
情况 E：已经 push 了：# 改好代码 新提交一个修正。绝对不要 amend / reset。
git add .
git commit -m "fix: 修正 xxx"
git push
git push --force⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️ never