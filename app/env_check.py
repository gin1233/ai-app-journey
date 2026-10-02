"""环境自检：确认开发环境健康。

这是 day01/check_env.py 的工程化版本，三处升级：
    1. 住进了 app/ 包里，可以被别的代码 import 复用
    2. 用 rich 库输出彩色表格（终于像个工具了）
    3. 配置从 config.py 读，不写死在代码里
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from app.config import PROJECT_ROOT, show_config

console = Console()

REQUIRED_PYTHON = (3, 12)


def check_python_version() -> tuple[bool, str]:
    """检查 Python 版本。"""
    current = sys.version_info[:2]
    ok = current >= REQUIRED_PYTHON
    required = ".".join(str(n) for n in REQUIRED_PYTHON)
    return ok, f"当前 {platform.python_version()}，要求 >= {required}"


def check_virtual_env() -> tuple[bool, str]:
    """检查是否运行在虚拟环境里。"""
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        return True, str(Path(sys.prefix).name)
    return False, "未激活！正在使用全局 Python"


def check_project_files() -> tuple[bool, str]:
    """检查项目结构是否完整。"""
    expected = ["README.md", "requirements.txt", ".gitignore", "app"]
    missing = [name for name in expected if not (PROJECT_ROOT / name).exists()]
    if missing:
        return False, f"缺少 {missing}"
    return True, f"{len(expected)} 项齐全"


def main() -> int:
    """跑全部检查，打印表格，返回退出码。"""
    checks = [
        ("Python 版本", check_python_version),
        ("虚拟环境", check_virtual_env),
        ("项目结构", check_project_files),
    ]

    table = Table(title="环境自检")
    table.add_column("检查项", style="cyan", no_wrap=True)
    table.add_column("结果", justify="center")
    table.add_column("详情", style="dim")

    all_ok = True
    for name, check in checks:          # check 是个函数，这里才调用它
        ok, detail = check()
        if not ok:
            all_ok = False
        table.add_row(name, "[green]通过[/green]" if ok else "[red]失败[/red]", detail)

    console.print(table)

    config = show_config()
    console.print("\n[bold]当前配置[/bold]")
    for key, value in config.items():
        console.print(f"  {key} = [yellow]{value}[/yellow]")

    if all_ok:
        console.print("\n[bold green]环境健康，可以开始学习[/bold green]")
    else:
        console.print("\n[bold red]有问题，按上面的提示处理后重跑[/bold red]")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())