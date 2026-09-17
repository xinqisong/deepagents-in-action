# Task 01：Research DeepAgent

这是课程学习的第一个代码记录，来源于 `agentseek create deepagents/research` 生成的研究 Agent 项目。

## 学习目标

- 熟悉 DeepAgents 项目结构和 AgentSeek 生命周期。
- 理解 `create_deep_agent()`、工具调用和 research sub-agent。
- 使用 LangGraph API 与前端观察 Agent 的流式执行过程。
- 记录模型 provider、工具和运行环境配置。

## 目录

```text
task01/
├── .agentseek/              # AgentSeek 生命周期配置
├── frontend/                # Vite + React 前端
├── src/research_deepagent/  # DeepAgent 后端代码
├── .env.example             # 环境变量模板，不包含密钥
├── langgraph.json           # LangGraph 图入口
├── pyproject.toml           # Python 依赖
└── uv.lock                  # 锁定依赖版本
```

## 独立运行

在本目录执行：

```bash
cp .env.example .env
# 编辑 .env，填写模型和 TAVILY_API_KEY
uv sync
npm install --prefix frontend
uv run agentseek-api dev
```

前端另开一个终端启动：

```bash
npm run dev --prefix frontend
```

默认后端地址是 `http://127.0.0.1:2024`，前端地址是
`http://127.0.0.1:5174`。

## 学习笔记

### 当前理解

`create_deep_agent()` 在模型之上提供 DeepAgents 的 Harness 能力；本项目的主 Agent 使用 Tavily 搜索和思考工具，并可以把研究主题委派给 `research-agent` 子 Agent。

### 当前模型配置

模型配置通过环境变量注入，主要入口是
`src/research_deepagent/agent.py`。不要把真实 `.env` 提交到 Git。

### 实验记录

- 待补充：启动服务并完成一次研究任务。
- 待补充：记录一次 Tavily 工具调用和一次子 Agent 委派。
- 待补充：记录模型配置、输出效果和遇到的问题。

### 下一步

- [ ] 完成一次端到端运行
- [ ] 阅读课程第 2 章并补充自己的理解
- [ ] 对比 `ChatOpenAI`、`init_chat_model` 与 OpenAI-compatible provider
