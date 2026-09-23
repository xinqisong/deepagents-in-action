# Task 04：任务规划与中间件

本目录对应课程第 4 章“任务规划与分解——让 Agent 学会拆解复杂任务”。本次实操跳过已经学过的虚拟文件系统，改用一个网站首页设计案例：Agent 先规划调研、信息架构和设计 brief，再通过多次搜索完成方案。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch04-task-planning/>

## 文件说明

```text
task04/
├── agent.py              # TodoListMiddleware + internet_search 网站设计案例
├── learning.md           # 知识总结、学习路线和实验记录
├── pyproject.toml        # Python 依赖
├── .env.example          # 环境变量模板，不包含密钥
└── workspace/            # 学习过程中的手动笔记和资料
```

## 开始运行

在本目录执行：

```bash
cp .env.example .env
# 编辑 .env，填写模型配置、模型 API Key 和 Tavily API Key
uv sync
uv run python agent.py
```

本案例会进行互联网搜索，不会自动修改仓库文件。不要把真实的 `.env`、私钥或生产配置提交到 Git。

## 本次实验

`agent.py` 按文章示例的结构使用：

- `TodoListMiddleware` 注入 `write_todos` 工具、`todos` 状态和规划提示词；
- `internet_search` 提供网站设计资料搜索能力；
- Agent 为中文课程网站规划首页信息架构和设计 brief；
- 最终输出验收清单，并区分任务状态和仍需人工判断的设计结论。

重点观察：任务列表是进度协议，不是质量证明；即使所有任务显示 `completed`，也必须检查搜索来源、设计方案和验收标准是否可靠。
