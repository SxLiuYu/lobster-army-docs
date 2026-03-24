# 🦞 龙虾军团 - CrewAI 实现方案

基于 CrewAI 的多 Agent 协作系统，帮你自动干活。

> 📚 参考来源：https://github.com/crewAIInc/crewAI (46.9k ⭐) | https://github.com/qdrant/qdrant (29.8k ⭐)

## 📋 目录

1. [为什么选 CrewAI](#-为什么选-crewai)
2. [核心概念：Crews vs Flows](#-核心概念-crews-vs-flows)
3. [项目结构](#-项目结构)
4. [环境配置](#-环境配置)
5. [Agent 定义](#-agent-定义)
6. [工具/技能系统](#-工具技能系统)
7. [记忆系统 Qdrant](#-记忆系统-qdrant)
8. [多 Agent 协作模式](#-多-agent-协作模式)
9. [层级模式详解](#-层级模式详解)
10. [快速开始](#-快速开始)
11. [对比其他框架](#-对比其他框架)

---

## 🏆 为什么选 CrewAI

| 特性 | CrewAI | LangGraph | AutoGen |
|------|--------|-----------|---------|
| **Stars** | 46.9k ⭐ | - | 56k ⭐ |
| **独立框架** | ✅ 纯 Python | 依赖 LangChain | 依赖 OpenAI |
| **速度** | 5.76x 快于 LangGraph | - | - |
| **上手难度** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Flows 企业级** | ✅ | ✅ | ❌ |
| **100k+ 认证开发者** | ✅ | - | - |

> *"CrewAI is a lean, lightning-fast Python framework built entirely from scratch—completely independent of LangChain or other agent frameworks."* — 官方 README

### CrewAI 核心优势

1. **完全独立** - 不依赖 LangChain或其他框架，更轻量、更快
2. **Crews + Flows** - 同时支持自主协作和精确工作流
3. **高性能** - 比 LangGraph 快 5.76 倍
4. **企业级** - Flows 提供生产级事件驱动控制
5. **活跃社区** - 10万+ 认证开发者

---

## 🔀 核心概念：Crews vs Flows

### Crews（机组）- 自主协作

```
Crews = 多个 Agent 组成团队，协同完成复杂任务

特点：
✓ Agent 之间自主决策和协作
✓ 动态任务分配
✓ 适合需要灵活性的场景
✓ 支持 Sequential / Hierarchical 流程
```

**适用场景**：研究分析、多阶段创作、复杂问题求解

### Flows（流程）- 精确控制

```
Flows = 事件驱动的工作流，精确控制执行路径

特点：
✓ 细粒度控制
✓ 条件分支（or_, and_）
✓ 状态管理
✓ Python 代码集成
✓ 生产级稳定性
```

**适用场景**：自动化流水线、业务流程、精确执行

### 两者的力量

> *"The true power of CrewAI emerges when combining Crews and Flows"*

```python
# 组合使用示例
from crewai import Flow

@start()
def begin():
    return "start"

@listen(begin)
def run_crew():
    return crew.kickoff()  # 调用 Crew

@listen(run_crew)
def end():
    return "completed"
```

---

## 📦 项目结构

```
lobster-army/
├── config/
│   ├── agents.yaml        # Agent 配置
│   ├── memory.yaml        # 记忆配置
│   └── .env               # 环境变量
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── commander.py   # 指挥官
│   │   ├── researcher.py  # 研究员
│   │   ├── coder.py       # 工程师
│   │   ├── writer.py      # 写手
│   │   └── ops.py         # 运维
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── search.py      # 搜索技能
│   │   ├── code.py        # 代码技能
│   │   └── tools.py       # 工具集
│   ├── memory/
│   │   ├── __init__.py
│   │   └── store.py       # 记忆存储
│   └── main.py            # 入口
├── requirements.txt
└── README.md
```

---

## 🔧 环境配置

```bash
# 安装 CrewAI
uv pip install crewai

# 带工具版本
uv pip install 'crewai[tools]'

# 安装 Qdrant 客户端
pip install qdrant-client

# Python 版本要求
# Python >= 3.10 < 3.14
```

### 环境变量配置

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# 可选：本地模型
# OLLAMA_BASE_URL=http://localhost:11434

# Qdrant 配置
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key  # 可选
```

---

## 🤖 Agent 定义

### Agent 核心属性

```python
from crewai import Agent

agent = Agent(
    role="角色名称",           # 如 "研究员"
    goal="目标",              # Agent 要达成什么
    backstory="背景故事",      # 设定 Agent 的性格和能力
    verbose=True,             # 输出详细信息
    allow_delegation=True,   # 是否允许委托任务
    tools=[tool1, tool2],   # 分配的工具
    llm_model="gpt-4"        # 使用的模型
)
```

### 1. 指挥官 (Commander)

```python
from crewai import Agent

commander = Agent(
    role="指挥官",
    goal="协调各个 Agent 高效完成任务，将复杂任务拆分为子任务并分配给合适的 Agent",
    backstory="""你是龙虾军团的指挥官，负责：
1. 理解用户需求
2. 将任务分发给合适的 Agent
3. 汇总结果返回给用户
4. 管理整个团队的记忆和状态""",
    verbose=True,
    allow_delegation=True,
    max_iterations=10
)
```

### 2. 研究员 (Researcher)

```python
from crewai import Agent
from crewai.tools import Tool

researcher = Agent(
    role="信息研究员",
    goal="收集最准确、最相关的信息",
    backstory="""你是一个专业的研究员，擅长：
- 网络搜索和信息收集
- 分析和整理数据
- 提炼关键信息
- 验证信息来源可靠性""",
    verbose=True,
    allow_delegation=False,
    tools=[
        search_tool,      # 搜索工具
        scrape_tool      # 网页抓取工具
    ]
)
```

### 3. 工程师 (Coder)

```python
from crewai import Agent

coder = Agent(
    role="软件工程师",
    goal="编写高质量、可维护的代码",
    backstory="""你是一个资深工程师，注重：
- 代码质量和性能
- 清晰的注释和文档
- 错误处理和边界情况
- 测试覆盖""",
    verbose=True,
    allow_delegation=False,
    tools=[code_executor_tool]
)
```

### 4. 写手 (Writer)

```python
from crewai import Agent

writer = Agent(
    role="技术写手",
    goal="将复杂信息转化为清晰的文档",
    backstory="""你擅长：
- 技术文档撰写
- 清晰易懂的解释
- Markdown 格式
- 中英文技术写作""",
    verbose=True,
    allow_delegation=False
)
```

### 5. 运维 (Ops)

```python
from crewai import Agent

ops = Agent(
    role="运维工程师",
    goal="确保服务稳定运行",
    backstory="""你擅长：
- 自动化部署
- 监控和日志分析
- 故障排查
- 性能优化""",
    verbose=True,
    allow_delegation=False,
    tools=[docker_tool, ssh_tool]
)
```

---

## 🛠️ 工具/技能系统

### 内置工具

```python
from crewai.tools import Tool

# 创建自定义工具
search_tool = Tool(
    name="web_search",
    description="搜索网络信息，返回相关内容",
    func=lambda query: search_api(query)
)

# 或使用 @tool 装饰器
from crewai.tools import tool

@tool("search")
def search(query: str) -> str:
    """搜索网络信息"""
    return search_api(query)
```

### 自定义工具示例

```python
# src/skills/search.py
from crewai.tools import BaseTool
from pydantic import BaseModel
import requests

class SearchInput(BaseModel):
    query: str
    max_results: int = 5

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "搜索网络信息，包括新闻、文章、技术文档等"
    args_schema = SearchInput
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """执行搜索"""
        response = requests.get(
            "https://api.search.com/search",
            params={"q": query, "limit": max_results}
        )
        return response.json()

# 使用示例
search_tool = WebSearchTool()
```

### 代码执行工具（安全沙箱）

```python
# src/skills/code.py
from crewai.tools import BaseTool

class SafeCodeExecutor(BaseTool):
    """安全代码执行器 - 使用 Docker 沙箱"""
    
    name = "execute_code"
    description = "执行 Python/Bash 代码并返回结果"
    
    def _run(self, code: str, language: str = "python") -> dict:
        if language == "python":
            result = subprocess.run(
                ["docker", "run", "--rm", "-i", 
                 "python:3.11-slim", "python", "-c", code],
                capture_output=True, text=True, timeout=30
            )
        return {
            "output": result.stdout,
            "error": result.stderr,
            "success": result.returncode == 0
        }
```

---

## 💾 记忆系统：Qdrant

### Qdrant 核心特性

| 特性 | 说明 |
|------|------|
| **高性能** | Rust 编写，高并发支持 |
| **向量搜索** | 支持 HNSW、量化等算法 |
| **混合搜索** | 向量 + 关键词组合 |
| **过滤支持** | 丰富的 payload 过滤 |
| **分布式** | 支持水平扩展 |
| **云端/本地** | 支持自托管和云服务 |

### Qdrant 安装

```bash
# Docker 部署（推荐）
docker run -d -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# 或使用 Python 嵌入式模式
from qdrant_client import QdrantClient
client = QdrantClient(path="./qdrant_storage")
```

### 记忆存储实现

```python
# src/memory/store.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import json
from datetime import datetime

class AgentMemory:
    """龙虾军团记忆系统 - 基于 Qdrant"""
    
    def __init__(self, url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=url)
        self.collection = "lobster_memory"
        self._init_collection()
    
    def _init_collection(self):
        """初始化集合"""
        collections = self.client.get_collections().collections
        if self.collection not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_size=1536,  # OpenAI embedding size
                distance=Distance.COSINE
            )
            # 创建 payload 索引
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="timestamp",
                field_type="datetime"
            )
    
    def add(self, key: str, content: str, metadata: dict = None):
        """添加记忆"""
        # 生成 embedding
        from openai import OpenAI
        client = OpenAI()
        vector = client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        ).data[0].embedding
        
        self.client.upsert(
            collection_name=self.collection,
            points=[{
                "id": key,
                "vector": vector,
                "payload": {
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata or {}
                }
            }]
        )
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        """语义搜索记忆"""
        from openai import OpenAI
        client = OpenAI()
        vector = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding
        
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit
        )
        return [{
            "content": r.payload["content"],
            "timestamp": r.payload.get("timestamp"),
            "score": r.score
        } for r in results]
    
    def get_by_time_range(self, start: datetime, end: datetime) -> list:
        """按时间范围获取记忆"""
        return self.client.scroll(
            collection_name=self.collection,
            scroll_filter={
                "must": [
                    {
                        "key": "timestamp",
                        "range": {
                            "gte": start.isoformat(),
                            "lte": end.isoformat()
                        }
                    }
                ]
            }
        )[0]
```

### 三层记忆架构

```python
class ThreeLayerMemory:
    """三层记忆系统"""
    
    def __init__(self):
        # Layer 1: Redis 短期记忆
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        
        # Layer 2: Qdrant 长期向量记忆
        self.qdrant = AgentMemory()
        
        # Layer 3: SQLite 持久化存储
        self.sqlite = sqlite3.connect('memory.db')
    
    def remember(self, key: str, content: str, important: bool = False):
        # 1. 短期：24小时 TTL
        self.redis.setex(f"mem:{key}", 86400, content)
        
        # 2. 长期：向量存储
        self.qdrant.add(key, content, {"important": important})
        
        # 3. 重要记忆持久化
        if important:
            self.sqlite.execute(
                "INSERT OR REPLACE INTO memory VALUES (?, ?, ?)",
                (key, content, datetime.now().isoformat())
            )
            self.sqlite.commit()
    
    def recall(self, query: str) -> list:
        """语义检索 + 时间排序"""
        return self.qdrant.search(query)
```

---

## 🤝 多 Agent 协作模式

### 1. Sequential 模式（顺序执行）

```python
from crewai import Crew, Task, Process

# 定义任务
task1 = Task(
    description="研究内网穿透方案",
    agent=researcher,
    expected_output="详细的技术方案文档"
)

task2 = Task(
    description="写实现代码",
    agent=coder,
    expected_output="可运行的代码文件"
)

task3 = Task(
    description="写使用文档",
    agent=writer,
    expected_output="完整的文档"
)

# 创建 Crew（顺序执行）
crew = Crew(
    agents=[researcher, coder, writer],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
```

### 2. Hierarchical 模式（层级管理）

```python
# 创建层级 Crew（自动分配管理器）
crew = Crew(
    agents=[researcher, coder, writer, ops],
    tasks=[task1, task2, task3],
    process=Process.hierarchical,
    manager_agent=commander,  # 指定管理器
    verbose=True
)
```

### 3. 任务依赖关系

```python
# Task 2 依赖 Task 1 的输出
task2 = Task(
    description="基于研究结果写代码",
    agent=coder,
    expected_output="完整的实现代码",
    context=[task1]  # 依赖 task1 的结果
)
```

---

## 📊 层级模式详解

### Hierarchical 流程工作原理

```
用户输入
    ↓
[管理器 Agent]
    ↓
┌──────────────┐
│  分配任务    │
└──────────────┘
    ↓
┌────────────────┐
│ Worker Agent 1 │ ──┐
│ Worker Agent 2 │ ──┼──→ 并行执行
│ Worker Agent 3 │ ──┘
└────────────────┘
    ↓
[管理器 Agent]
    ↓
验证结果
    ↓
返回给用户
```

### 完整示例

```python
from crewai import Agent, Crew, Task, Process

# 定义 Agent
researcher = Agent(
    role="研究员",
    goal="收集准确的信息",
    backstory="专业研究员，擅长搜索和分析"
)

coder = Agent(
    role="工程师",
    goal="写出高质量代码",
    backstory="资深工程师，注重代码质量"
)

commander = Agent(
    role="项目经理",
    goal="协调团队，高效完成任务",
    backstory="经验丰富的项目经理"
)

# 定义任务
research_task = Task(
    description="研究 FRP 内网穿透方案",
    agent=researcher,
    expected_output="技术方案文档"
)

code_task = Task(
    description="实现 FRP 客户端",
    agent=coder,
    expected_output="可运行的代码"
)

# 创建 Crew
crew = Crew(
    agents=[researcher, coder],
    tasks=[research_task, code_task],
    process=Process.hierarchical,
    manager_agent=commander
)

# 执行
result = crew.kickoff(inputs={"topic": "内网穿透"})
```

---

## ⚡ 快速开始

```bash
# 1. 安装
uv pip install crewai 'crewai[tools]'
pip install qdrant-client openai

# 2. 配置环境变量
cp config/.env.example config/.env
# 编辑 .env 填入 API Key

# 3. 启动 Qdrant（可选）
docker run -d -p 6333:6333 qdrant/qdrant

# 4. 运行示例
python examples/simple_crew.py
```

### 完整运行示例

```python
# examples/simple_crew.py
import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, Process

load_dotenv()

# 1. 定义 Agent
researcher = Agent(
    role="研究员",
    goal="研究给定主题并提供详细信息",
    backstory="你是专业的研究员，擅长搜索和分析"
)

writer = Agent(
    role="写手",
    goal="将研究结果转化为清晰的文档",
    backstory="你擅长技术写作"
)

# 2. 定义任务
research_task = Task(
    description="研究内网穿透技术方案",
    agent=researcher,
    expected_output="详细的技术研究报告"
)

write_task = Task(
    description="将研究报告整理成文档",
    agent=writer,
    expected_output="Markdown 格式的技术文档"
)

# 3. 创建 Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)

# 4. 执行
result = crew.kickoff()
print(result)
```

---

## 🔄 对比其他框架

| 特性 | CrewAI | LangGraph | AutoGen | ChatDev |
|------|--------|-----------|---------|---------|
| **Stars** | 46.9k | - | 56k | - |
| **独立框架** | ✅ 纯 Python | ❌ 依赖 LangChain | ❌ 依赖 OpenAI | ✅ |
| **速度** | 最快 | 中等 | 中等 | - |
| **Flows** | ✅ 企业级 | ✅ | ❌ | ❌ |
| **多模型支持** | ✅ | ✅ | ✅ | ✅ |
| **本地模型** | ✅ Ollama | ✅ | ✅ | ✅ |
| **上手难度** | 低 | 高 | 中等 | 低 |
| **生产级** | ✅ | ✅ | ✅ | ❌ |

### 选择建议

| 场景 | 推荐 |
|------|------|
| 快速原型 | CrewAI ✅ |
| 企业生产 | CrewAI Flows |
| 复杂研究 | CrewAI + Qdrant |
| 简单任务 | ChatDev |
| 深度定制 | LangGraph |

---

## 📚 参考资源

| 资源 | 链接 |
|------|------|
| CrewAI 官网 | https://crewai.com |
| CrewAI 文档 | https://docs.crewai.com |
| 学习课程 | https://learn.crewai.com |
| Qdrant 文档 | https://qdrant.tech/documentation/ |
| 示例项目 | https://github.com/crewAIInc/crewAI-examples |

---

*Generated on 2026-03-23 | Updated with latest CrewAI & Qdrant info*
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
```

---

## 🤖 Agent 定义

### 1. 指挥官 (Commander)

```python
# src/agents/commander.py
from crewai import Agent
from pydantic import BaseModel

class CommanderAgent(Agent):
    """龙虾军团指挥官 - 统筹协调"""
    
    def __init__(self):
        super().__init__(
            role="指挥官",
            goal="协调各个 Agent 高效完成任务",
            backstory="""你是龙虾军团的指挥官，负责：
1. 理解用户需求
2. 将任务拆分并分配给合适的 Agent
3. 汇总结果返回给用户
4. 管理整个团队的记忆""",
            verbose=True,
            allow_delegation=True,
            max_iterations=10
        )
    
    def decompose_task(self, task: str) -> list[dict]:
        """分解任务"""
        # 智能拆分任务
        pass
```

### 2. 研究员 (Researcher)

```python
# src/agents/researcher.py
from crewai import Agent
from crewai.tools import Tool

class ResearcherAgent(Agent):
    """信息研究员"""
    
    def __init__(self, tools: list[Tool]):
        super().__init__(
            role="信息研究员",
            goal="收集最准确、最相关的信息",
            backstory="""你是一个专业的研究员，擅长：
- 网络搜索和信息收集
- 分析和整理数据
- 提炼关键信息
- 验证信息来源""",
            verbose=True,
            allow_delegation=False,
            tools=tools
        )
```

### 3. 工程师 (Coder)

```python
# src/agents/coder.py
from crewai import Agent

class CoderAgent(Agent):
    """代码工程师"""
    
    def __init__(self, tools: list[Tool]):
        super().__init__(
            role="软件工程师",
            goal="编写高质量、可维护的代码",
            backstory="""你是一个资深工程师，注重：
- 代码质量和性能
- 清晰的注释和文档
- 错误处理和边界情况
- 测试覆盖""",
            verbose=True,
            allow_delegation=False,
            tools=tools
        )
```

### 4. 写手 (Writer)

```python
# src/agents/writer.py
from crewai import Agent

class WriterAgent(Agent):
    """文档写手"""
    
    def __init__(self):
        super().__init__(
            role="技术写手",
            goal="将复杂信息转化为清晰的文档",
            backstory="""你擅长：
- 技术文档撰写
- 清晰易懂的解释
- Markdown 格式
- 中英文技术写作""",
            verbose=True,
            allow_delegation=False
        )
```

### 5. 运维 (Ops)

```python
# src/agents/ops.py
from crewai import Agent

class OpsAgent(Agent):
    """运维工程师"""
    
    def __init__(self, tools: list[Tool]):
        super().__init__(
            role="运维工程师",
            goal="确保服务稳定运行",
            backstory="""你擅长：
- 自动化部署
- 监控和日志分析
- 故障排查
- 性能优化""",
            verbose=True,
            allow_delegation=False,
            tools=tools
        )
```

---

## 🛠️ 技能/工具定义

### 搜索工具

```python
# src/skills/search.py
from crewai.tools import BaseTool
from pydantic import BaseModel
import requests

class SearchInput(BaseModel):
    query: str
    max_results: int = 5

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "搜索网络信息"
    args_schema = SearchInput
    
    def _run(self, query: str, max_results: int = 5) -> str:
        # 使用 Tavily / 百度 等 API
        return results

class WebsiteScrapeTool(BaseTool):
    name = "scrape_website"
    description = "抓取网页内容"
    
    def _run(self, url: str) -> str:
        # 使用 beautifulsoup 抓取
        return content
```

### 代码执行工具

```python
# src/skills/code.py
from crewai.tools import BaseTool
import subprocess

class CodeExecutorTool(BaseTool):
    name = "execute_code"
    description = "执行代码并返回结果"
    
    def _run(self, code: str, language: str = "python") -> dict:
        if language == "python":
            # 使用 docker 容器执行，更安全
            result = subprocess.run(
                ["docker", "run", "--rm", "python:3.11", "python", "-c", code],
                capture_output=True, text=True
            )
        return {"output": result.stdout, "error": result.stderr}
```

---

## 💾 记忆系统

### Qdrant 向量存储

```python
# src/memory/store.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import json

class MemoryStore:
    """记忆存储 - 基于 Qdrant"""
    
    def __init__(self, url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=url)
        self.collection = "lobster_memory"
        self._init_collection()
    
    def _init_collection(self):
        """初始化集合"""
        collections = self.client.get_collections().collections
        if self.collection not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_size=1536,  # OpenAI embedding size
                distance=Distance.COSINE
            )
    
    def add(self, key: str, content: str, metadata: dict = None):
        """添加记忆"""
        # 生成 embedding
        from openai import OpenAI
        client = OpenAI()
        vector = client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        ).data[0].embedding
        
        self.client.upsert(
            collection_name=self.collection,
            points=[{
                "id": key,
                "vector": vector,
                "payload": {"content": content, "metadata": metadata or {}}
            }]
        )
    
    def search(self, query: str, limit: int = 5) -> list:
        """搜索记忆"""
        from openai import OpenAI
        client = OpenAI()
        vector = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding
        
        results = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=limit
        )
        return [r.payload["content"] for r in results]
```

---

## 🚀 主程序

```python
# src/main.py
import os
from dotenv import load_dotenv
from crewai import Crew, Task, Process

# 导入 Agent
from agents.commander import CommanderAgent
from agents.researcher import ResearcherAgent
from agents.coder import CoderAgent
from agents.writer import WriterAgent
from agents.ops import OpsAgent

# 导入工具
from skills.search import WebSearchTool, WebsiteScrapeTool
from skills.code import CodeExecutorTool
from memory.store import MemoryStore

load_dotenv()

class LobsterArmy:
    """龙虾军团主程序"""
    
    def __init__(self):
        # 初始化工具
        self.search_tool = WebSearchTool()
        self.scrape_tool = WebsiteScrapeTool()
        self.code_tool = CodeExecutorTool()
        
        # 初始化记忆
        self.memory = MemoryStore(
            url=os.getenv("QDRANT_URL", "http://localhost:6333")
        )
        
        # 初始化 Agent
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有 Agent"""
        
        # 研究员
        self.researcher = ResearcherAgent(
            tools=[self.search_tool, self.scrape_tool]
        )
        
        # 工程师
        self.coder = CoderAgent(
            tools=[self.code_tool]
        )
        
        # 写手
        self.writer = WriterAgent()
        
        # 运维
        self.ops = OpsAgent(
            tools=[self.code_tool]  # 可以添加 docker tool 等
        )
    
    def create_crew(self, task_description: str):
        """创建 Crew 并执行任务"""
        
        # 创建任务
        research_task = Task(
            description=f"研究：{task_description}",
            agent=self.researcher,
            expected_output="详细的研究报告"
        )
        
        code_task = Task(
            description=f"实现：{task_description}",
            agent=self.coder,
            expected_output="可运行的代码"
        )
        
        write_task = Task(
            description=f"文档：{task_description}",
            agent=self.writer,
            expected_output="清晰的文档"
        )
        
        # 创建 Crew（层级模式）
        crew = Crew(
            agents=[self.researcher, self.coder, self.writer, self.ops],
            tasks=[research_task, code_task, write_task],
            process=Process.hierarchical,
            manager_agent=self.commander,
            verbose=True
        )
        
        return crew
    
    def run(self, task: str):
        """运行任务"""
        # 先检查记忆
        related_memory = self.memory.search(task)
        
        # 创建 Crew
        crew = self.create_crew(task)
        
        # 执行
        result = crew.kickoff()
        
        # 存储到记忆
        self.memory.add(
            key=f"task_{hash(task)}",
            content=f"任务：{task}\n结果：{result}",
            metadata={"task": task}
        )
        
        return result


# 使用示例
if __name__ == "__main__":
    army = LobsterArmy()
    
    # 执行任务
    result = army.run("帮我研究内网穿透方案，然后写一个实现")
    print(result)
```

---

## ⚡ 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/SxLiuYu/lobster-army.git
cd lobster-army

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp config/.env.example config/.env
# 编辑 .env 填入 API Key

# 4. 启动 Qdrant（可选）
docker run -d -p 6333:6333 qdrant/qdrant

# 5. 运行
python src/main.py
```

---

## 📊 对比总结

| 特性 | CrewAI | 说明 |
|------|--------|------|
| 上手难度 | ⭐⭐ | 简单易学 |
| 多 Agent | ✅ | 原生支持 |
| 记忆存储 | + Qdrant | 向量检索 |
| 工具扩展 | + 自定义 Tool | 灵活 |
| 企业级 | ⭐⭐⭐ | 需要二次开发 |

---

*Generated on 2026-03-23*
