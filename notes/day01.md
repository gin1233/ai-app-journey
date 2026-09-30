# Day 01 · 环境搭建

## 我做了什么
- 用 python -m venv .venv 命令创建了虚拟环境
- 激活后，提示符多了 (.venv) 才说明成功
- 跑了 check_env.py，三项检查是
OK    Python 版本
OK    虚拟环境
OK    项目结构

pwd print working directory
cd change directory
dir directory (double click) 相当于查看当前文件夹内容
    dir -force 查看隐藏文件内容
    ----- 5个
        第一个-：d文件夹 -文件 l链接
        第二个-：a archive
        第三个-：r read-only
        第四个-：h hidden
        第五个-：s system
prompt PS C:\Users\Administrator\Documents\Codex\ai-app-journey> 这里的PS指的是 接线员是PS 也有可能是bash/cmd....

激活：.\.venv\Scripts\Activate.ps1
验证：where.exe python ----------  C:\Users\Administrator\Documents\Codex\ai-app-journey\.venv\Scripts\python.exe 第一个不是这个都是错的
验证：python -c "import sys; print(sys.prefix)"

## 虚拟环境解决了什么问题
1.虚拟环境解决的头号问题是：同一个包的不同版本互斥。
    项目 A 要 fastapi 0.100，项目 B 要 0.115。
    全局只能装一个 → 装了新的，A 崩；卸了装旧的，B 崩。
    虚拟环境让两个项目各装各的，谁也不用迁就谁。
2.虚拟环境就像是鞋盒，将不同的项目所需要的东西放在不同的鞋盒里。 方便回头查找

## 为什么 .venv 不能提交 Git
1.没必要 10 秒重建一个等价环境
2.量大
3.没用，只适用于本地，换台电脑跑不通

## 今天踩的坑
ctrl + fn + esc = VS terminal

cd 是转移自身视角不是转移文件
PS是类似于和鼠标一样的抽象与电脑交互方式

报错	                                              原因	                                         解决
无法将"...Activate.ps1"项识别为...	             你没站在项目目录里	                       cd 过去再试，先 pwd 确认
无法加载文件...因为在此系统上禁止运行脚本	      Windows 默认安全策略	执行 Set-ExecutionPolicy -Scope CurrentUser RemoteSigned，输入 Y，然后重开终端再试
提示符没出现 (.venv)，但也没报错	                 激活其实没生效	                  用 where.exe python 验证，别看提示符猜
关掉终端再打开，(.venv) 没了	                      正常现象	                           每个新终端都要重新激活一次

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned 没有反应 = 成功了
验证： Get-ExecutionPolicy -Scope CurrentUser 应return RemoteSigned


## 还没搞懂的地方
暂无