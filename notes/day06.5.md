| # | 卡点 | 原因 | 怎么过的 |
|---|---|---|---|
| 1 | Docker 装不上 | WSL 未安装 | `wsl --install` 装上 WSL 3.0.1 |
| 2 | 装不了发行版 | `raw.githubusercontent.com` 被墙 | 改用 `winget install Canonical.Ubuntu` |
| 3 | 拉不了镜像 | **DNS 被污染**（解析到 `31.13.91.6`，一个 Meta 的 IP） | 试着配阿里云镜像源 → **403**（阿里云已不代理公共镜像） |
| 4 | **TUN 开了也没用** | **WSL2 走 Hyper-V 虚拟交换机，TUN 覆盖不到** | ⭐ **在 Docker Desktop 自己的 Proxies 设置里显式填代理** |