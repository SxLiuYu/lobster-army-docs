# 🦞 龙虾军团 - Windows 部署方案

在 Windows 电脑上部署龙虾军团的完整指南。

---

## 📋 目录

1. [环境要求](#-环境要求)
2. [软件安装](#-软件安装)
3. [服务配置](#-服务配置)
4. [项目部署](#-项目部署)
5. [内网穿透配置](#-内网穿透配置)
6. [验证与测试](#-验证与测试)
7. [开机自启](#-开机自启)
8. [备份与恢复](#-备份与恢复)

---

## 💻 环境要求

### 最低配置

| 项目 | 要求 | 推荐 |
|------|------|------|
| 系统 | Windows 10/11 | Windows 11 |
| 内存 | 8GB | 16GB+ |
| 硬盘 | 50GB 可用 | 100GB SSD |
| CPU | 4 核 | 8 核+ |

### 需要安装的软件

| 软件 | 版本 | 用途 |
|------|------|------|
| Docker Desktop | Latest | 容器化 |
| Python | 3.10+ | 运行环境 |
| Git | Latest | 版本控制 |
| FFmpeg | Latest | 媒体处理 |

---

## 🛠️ 软件安装

### 1. 安装 Docker Desktop

**方式一：官方安装包**

1. 下载：https://www.docker.com/products/docker-desktop
2. 运行安装程序
3. 勾选 "Use WSL 2 instead of Hyper-V"（推荐）
4. 启动 Docker Desktop

**方式二：winget（推荐）**

```powershell
winget install Docker.DockerDesktop
```

**验证安装**

```powershell
docker --version
docker-compose --version
```

> ⚠️ 首次启动 Docker Desktop 需要登录 Docker Hub 账号

### 2. 安装 Python

**方式一：官方安装包**

1. 下载：https://www.python.org/downloads/
2. 运行安装程序
3. **重要**：勾选 "Add Python to PATH"
4. 选择 "Customize installation"
5. 勾选所有选项，特别是 "pip"

**方式二：winget（推荐）**

```powershell
winget install Python.Python.3.11
```

**验证安装**

```powershell
python --version
pip --version
```

### 3. 安装 Git

```powershell
winget install Git.Git
```

**配置**

```powershell
git config --global user.name "YourName"
git config --global user.email "your@email.com"
```

### 4. 安装 FFmpeg（媒体处理用）

```powershell
winget install FFmpeg.FFmpeg
```

**验证**

```powershell
ffmpeg -version
```

---

## 🐳 服务配置

### 1. 创建项目目录

```powershell
# 在 D 盘或合适位置创建
D:
mkdir lobster-army
cd lobster-army
mkdir -p services data skills memory logs
```

### 2. Docker Compose 配置

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # Qdrant 向量数据库
  qdrant:
    image: qdrant/qdrant:latest
    container_name: lobster-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant:/qdrant/storage
    restart: unless-stopped

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: lobster-redis
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    restart: unless-stopped

  # PostgreSQL 数据库（可选）
  postgres:
    image: postgres:16-alpine
    container_name: lobster-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: lobster123
      POSTGRES_DB: lobster
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    restart: unless-stopped

  # FRP 内网穿透客户端
  frpc:
    image: snowdreamtech/frpc:latest
    container_name: lobster-frpc
    volumes:
      - ./config/frpc.ini:/etc/frp/frpc.ini
    network_mode: host
    restart: unless-stopped
```

### 3. 启动服务

```powershell
# 进入项目目录
cd D:\lobster-army

# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps
```

**验证服务启动**

```powershell
# Qdrant
curl http://localhost:6333/collections

# Redis
docker exec lobster-redis redis-cli ping
```

---

## 📦 项目部署

### 1. 克隆项目

```powershell
cd D:\lobster-army
git clone https://github.com/SxLiuYu/lobster-army.git src
```

### 2. 创建虚拟环境

```powershell
cd D:\lobster-army\src
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```powershell
# 升级 pip
pip install --upgrade pip

# 安装核心依赖
pip install crewai>=0.70.0
pip install 'crewai[tools]'
pip install qdrant-client>=1.7.0
pip install redis>=5.0.0
pip install openai>=1.0.0
pip install anthropic>=0.18.0
pip install python-dotenv>=1.0.0
pip install pydantic>=2.0.0
pip install sqlalchemy>=2.0.0
pip install aiohttp>=3.9.0
pip install pydantic-settings>=2.0.0
```

### 4. 配置环境变量

创建 `src/.env` 文件：

```env
# OpenAI（必须）
OPENAI_API_KEY=sk-...

# Anthropic（可选）
ANTHROPIC_API_KEY=sk-ant-...

# Qdrant
QDRANT_URL=http://localhost:6333

# Redis
REDIS_URL=redis://localhost:6379

# 数据库（可选）
DATABASE_URL=postgresql://postgres:lobster123@localhost:5432/lobster

# FRP 配置
FRP_SERVER_ADDR=your-vps-ip
FRP_SERVER_PORT=7000
FRP_TOKEN=your-token

# 日志
LOG_LEVEL=INFO
```

### 5. 测试运行

```powershell
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 运行测试
python -c "from crewai import Agent; print('OK')"

# 运行主程序
python src/main.py
```

---

## 🌐 内网穿透配置

### 方案一：FRP（需要 VPS）

#### 1. 服务端（VPS）

在 VPS 上运行：

```bash
# 下载 FRP
wget https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_linux_amd64.tar.gz
tar -zxf frp_0.52.3_linux_amd64.tar.gz
cd frp_0.52.3_linux_amd64

# 配置
cat > frps.ini << 'EOF'
[common]
bind_port = 7000
token = your_secret_token
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = admin123
EOF

# 启动
./frps -c frps.ini
```

#### 2. 客户端（Windows）

创建 `config/frpc.ini`：

```ini
[common]
server_addr = your-vps-ip
server_port = 7000
token = your_secret_token

# SSH（可选）
[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 6000

# Web 服务
[web]
type = http
local_ip = 127.0.0.1
local_port = 8000
custom_domains = your-domain.com

# API
[api]
type = tcp
local_ip = 127.0.0.1
local_port = 8001
remote_port = 8001
```

### 方案二：Cloudflare Tunnel（免费推荐）

#### 1. 安装 cloudflared

下载：https://github.com/cloudflare/cloudflared/releases

或者 PowerShell：

```powershell
irm https://get.clouder.fl | iex
```

#### 2. 登录

```powershell
cloudflared tunnel login
```

#### 3. 创建隧道

```powershell
cloudflared tunnel create lobster-army
```

#### 4. 配置

创建 `config/tunnel.yaml`：

```yaml
tunnel: lobster-army
credentials-file: %USERPROFILE%\.cloudflared\credentials.json

ingress:
  - hostname: lobster.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

#### 5. 启动

```powershell
cloudflared tunnel --config config/tunnel.yaml run
```

---

## ✅ 验证与测试

### 1. 检查服务状态

```powershell
# Docker 服务
docker-compose ps

# 手动检查端口
netstat -an | findstr "6333"
netstat -an | findstr "6379"
```

### 2. 测试 API

```powershell
# 测试 Qdrant
curl http://localhost:6333/collections

# 测试 Redis
docker exec lobster-redis redis-cli ping

# 测试 FRP
curl http://localhost:7500
```

### 3. 运行示例

```powershell
.\venv\Scripts\Activate.ps1

# 运行简单测试
python examples/simple_test.py
```

---

## 🔄 开机自启

### 方式一：Windows 任务计划程序

```powershell
# 创建任务
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File D:\lobster-army\start.ps1"
$trigger = New-ScheduledTaskTrigger -At Startup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -TaskPath "LobsterArmy" -Name "Start"
```

创建 `start.ps1`：

```powershell
# Docker Desktop 自启
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 等待 Docker 启动
Start-Sleep -Seconds 30

# 启动服务
Set-Location D:\lobster-army
docker-compose up -d

# 启动 Python
Set-Location D:\lobster-army\src
.\venv\Scripts\Activate.ps1
python src/main.py
```

### 方式二：启动文件夹

```powershell
# 创建快捷方式到启动文件夹
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\lobster-army.lnk")
$shortcut.TargetPath = "D:\lobster-army\start.bat"
$shortcut.WorkingDirectory = "D:\lobster-army"
$shortcut.Save()
```

创建 `start.bat`：

```batch
@echo off
cd D:\lobster-army
docker-compose up -d
cd D:\lobster-army\src
call venv\Scripts\activate.bat
python src\main.py
```

---

## 💾 备份与恢复

### 1. 备份数据

```powershell
# 备份 Docker 数据
Copy-Item -Path "D:\lobster-army\data" -Destination "D:\lobster-army\backup\data" -Recurse

# 备份配置
Copy-Item -Path "D:\lobster-army\config" -Destination "D:\lobster-army\backup\config" -Recurse

# 备份代码
Copy-Item -Path "D:\lobster-army\src" -Destination "D:\lobster-army\backup\src" -Recurse
```

### 2. 自动备份脚本

创建 `backup.ps1`：

```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$backupDir = "D:\lobster-army\backup\$date"

New-Item -ItemType Directory -Path $backupDir -Force

# 停止服务
Set-Location D:\lobster-army
docker-compose stop

# 备份
Compress-Archive -Path "D:\lobster-army\data" -DestinationPath "$backupDir\data.zip"
Compress-Archive -Path "D:\lobster-army\config" -DestinationPath "$backupDir\config.zip"

# 重启服务
docker-compose start

# 清理 7 天前的备份
Get-ChildItem "D:\lobster-army\backup" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Recurse
```

### 3. 恢复数据

```powershell
# 停止服务
docker-compose stop

# 解压备份
Expand-Archive -Path "D:\lobster-army\backup\data.zip" -DestinationPath "D:\lobster-army\data" -Force

# 重启服务
docker-compose up -d
```

---

## 🛠️ 常用命令

### Docker

```powershell
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启某个服务
docker-compose restart qdrant
```

### Python

```powershell
# 激活环境
.\venv\Scripts\Activate.ps1

# 安装新依赖
pip install new-package

# 运行
python src/main.py

# 退出环境
deactivate
```

### FRP

```powershell
# 查看 FRP 日志
docker logs lobster-frpc

# 重启 FRP
docker restart lobster-frpc
```

---

## ⚠️ 常见问题

### Docker 启动失败

```powershell
# 检查 Hyper-V
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V /all /norestart

# 重启电脑
```

### 端口被占用

```powershell
# 查看占用
netstat -ano | findstr "6333"

# 结束进程
taskkill /PID <PID> /F
```

### Python 依赖安装失败

```powershell
# 使用管理员权限
# 或者换源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package-name
```

### 内存不足

```powershell
# 减少 Docker 内存
# Docker Desktop → Settings → Resources → Memory
# 建议设置为 4GB 以上
```

---

## 📞 支持

遇到问题可以查看：

- Docker 日志：`docker-compose logs`
- Qdrant 文档：https://qdrant.tech/documentation/
- CrewAI 文档：https://docs.crewai.com

---

*Generated on 2026-03-23 | Windows 部署方案*
