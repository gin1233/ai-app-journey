# Git 速查手册

> **格式约定**
> - `PS>` 开头 = 你要输入的命令
> - 没有前缀 = 电脑的输出，只读，别输入

---

## 一、三个区域（核心心智模型）

    工作区                 暂存区                 版本库
 （你的文件夹）          （待寄的纸箱）         （已寄出的包裹）
      |                      |                      |
      |     git add          |   git commit         |
      +--------------------->+--------------------->
        "这个我要寄"            "封箱，寄出去"

| 区域 | 类比 | 命令进入方式 |
|---|---|---|
| 工作区 Working Directory | 你的书桌 | 直接用编辑器改 |
| 暂存区 Staging Area | 待寄的纸箱 | `git add` |
| 版本库 Repository | 已寄出的包裹 | `git commit` |

---

## 二、日常四连（每天用几百遍）

    PS> git status                      看现在什么情况
    PS> git add .                       把所有改动放进纸箱
    PS> git commit -m "feat: 做了啥"     封箱寄出
    PS> git log --oneline               看历史

---

## 三、状态里出现的三种文件

| 显示 | 含义 | 怎么处理 |
|---|---|---|
| `Untracked files` | 新文件，Git 还没管它 | `git add` 后进入暂存区 |
| `Changes not staged for commit` | 老文件改了，还没进纸箱 | `git add` 后进入暂存区 |
| `Changes to be committed` | 已在纸箱里，等着被封箱 | `git commit` 封箱 |

---

## 四、提交信息怎么写

    feat: 新增用户登录接口        新功能
    fix:  修复检索结果重复        修 bug
    docs: 补充部署说明            文档
    refactor: 重构检索模块        重构（不改功能）
    chore: 更新依赖版本           杂活

**禁止写**：update、修改、aaa、123

---

## 五、查看类命令

    PS> git status --short          简洁版状态
    PS> git diff                    看"改了但没暂存"的具体内容
    PS> git diff --staged           看"已暂存"的具体内容
    PS> git log --oneline           历史（一行一条）
    PS> git log --oneline -5        只看最近 5 条
    PS> git show <哈希>             看某次提交改了什么
    PS> git ls-files                列出所有被跟踪的文件

---

## 六、撤销类命令（危险，先问再敲）

    PS> git restore <文件>          丢弃工作区改动（改的东西直接没了）
    PS> git restore --staged <文件> 把文件从暂存区拿出来（改动还在）
    PS> git commit --amend          修改最后一次提交信息

**注意**：`git restore` 是不可逆的，改动会真的消失。

---

## 七、救命命令

    PS> git status                  遇到任何困惑，先敲这个
    PS> git --help                  查帮助
    PS> git <命令> --help           查具体命令帮助
                                    （在帮助页里按 q 退出）

---

## 八、保命守则

1. **永远不要**把网上复制的一大段文字无脑粘进终端
2. 粘之前先看懂它，看不懂就问
3. 一次只粘一条命令
4. `.venv/`、`.env`、`__pycache__/` 永远不进 Git
5. 一个提交只做一件事

---

## 九、本项目已有的提交

    PS> git log --oneline

    （运行上面这条命令查看）