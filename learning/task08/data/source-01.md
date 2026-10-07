# Task 01：AgentSeek research 模板

本资料摘自 `learning/task01/src/research_deepagent/agent.py` 和 `prompts.py`。

- 模板用 `create_deep_agent()` 创建主 Agent，并配置 `research-agent` 子 Agent。
- 主 Agent 负责规划、委派、综合研究结果和写最终报告。
- 研究子 Agent 使用 Tavily 搜索和 `think_tool`，向主 Agent 返回带来源的发现。
