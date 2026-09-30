r"""
Day 01 · 环境自检脚本
=====================

运行方式（在项目根目录下）：
    python day01\check_env.py

它的唯一作用是：确认你的开发环境是健康的。
但它顺便演示了 Day 01 你要掌握的 Python 知识点，每一条都标了注释。
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

# ---------- 常量：约定俗成用全大写命名 ----------
REQUIRED_PYTHON = (3, 12)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def check_python_version() -> bool:
    """知识点：函数定义、类型注解、切片、元组比较、f-string、条件判断"""
    current = sys.version_info[:2]        # 切片：取 (主版本, 次版本)
    is_ok = current >= REQUIRED_PYTHON    # 元组可以直接比大小：3.14 > 3.12
    mark = "通过" if is_ok else "不合格"
    print(f"[{mark}] Python 版本: {platform.python_version()}  (要求 >= 3.12)")
    return is_ok


def check_virtual_env() -> bool:
    """知识点：布尔表达式、if/else 分支、多行字符串缩进"""
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print(f"[通过] 虚拟环境: 已激活")
        print(f"       路径 -> {sys.prefix}")
    else:
        print("[警告] 虚拟环境: 未激活, 你现在用的是全局 Python")
        print("       正确做法: 先执行  .\\.venv\\Scripts\\Activate.ps1")
    return in_venv


def check_project_files() -> bool:
    """知识点：列表、列表推导式、循环、Path 对象"""
    expected = ["README.md", ".gitignore", "day01", "notes"]

    # 列表推导式：一行完成"遍历 + 过滤"
    missing = [name for name in expected if not (PROJECT_ROOT / name).exists()]

    if missing:
        print(f"[不合格] 项目结构: 缺少 {missing}")
        return False

    print(f"[通过] 项目结构: {len(expected)} 项齐全 -> {', '.join(expected)}")
    return True


def main() -> int:
    """知识点：函数调用、列表套元组、for 解包、内置函数 all()"""
    print("=" * 52)
    print("  AI 应用工程师学习计划 · 环境自检")
    print("=" * 52)

    # 先把每个检查都跑一遍，收集结果
    results = [
        ("Python 版本", check_python_version()),
        ("虚拟环境", check_virtual_env()),
        ("项目结构", check_project_files()),
    ]

    print("-" * 52)
    for name, passed in results:          # 解包：把元组拆成两个变量
        mark = "OK  " if passed else "FAIL"
        print(f"  {mark}  {name}")

    all_passed = all(passed for _, passed in results)
    print("-" * 52)
    if all_passed:
        print("  环境健康, 可以开始 Day 01 的练习")
    else:
        print("  有问题, 按上面的提示处理后重跑")
    print()

    return 0 if all_passed else 1


# 这是 Python 的固定写法：只有"直接运行本文件"时才执行 main()
# 被别人 import 时不会执行 —— 以后写模块必须记住这条
if __name__ == "__main__":
    sys.exit(main())