# 🦞 龙虾军团 - CrewAI 实现方案

基于 CrewAI 的多 Agent 协作系统，帮你自动干活。

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
# requirements.txt
crewai>=0.70.0
qdrant-client>=1.7.0
redis>=5.0.0
openai>=1.0.0
anthropic>=0.18.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
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
