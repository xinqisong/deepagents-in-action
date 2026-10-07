# Task 07：长期记忆与 Human-in-the-Loop

本目录包含课程第 8 章“长期记忆——让 Agent 拥有跨对话的记忆”和第 9 章“Human-in-the-Loop”。第 8 章的学习目标不是背 API，而是亲眼区分：

- `Checkpointer`：同一个 `thread_id` 内的短期状态；
- `Store`：跨线程、按 namespace 隔离的长期数据；
- `CompositeBackend`：按虚拟路径把临时文件和持久化记忆路由到不同后端。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/>

官方主资料：

<https://docs.langchain.com/oss/python/deepagents/memory>

## 当前进度

| 章节 | 学习内容 | 状态 |
| --- | --- | --- |
| [第 8 章：长期记忆](learning.md) | Checkpointer、Store、namespace、CompositeBackend 与跨对话读写 | 已完成本地实验与知识总结 |
| [第 9 章：Human-in-the-Loop](ch09-human-in-the-loop/learning.md) | 工具审批、暂停恢复、批量决策、节点重放与幂等；条件审批、并行中断 ID 和子 Agent 审批 | 核心审批流程已验证；后三项由教师演示通过，自定义 Middleware、文件权限、输入验证和异常传播待实践 |

## 当前分支

这两章的实验保存在 `learning/task07` 分支。

## 文件入口

- 第 8 章：[学习计划](learning.md)、[实验](experiment/README.md)、[知识总结](reference/long-term-memory-summary.md)、[学习记录](learning-records/README.md)
- 第 9 章：[学习计划与课程入口](ch09-human-in-the-loop/learning.md)、[边界速查](ch09-human-in-the-loop/reference/hitl-boundaries.html)、[资源与版本记录](ch09-human-in-the-loop/RESOURCES.md)

## 第 8 章实验入口

先读 [第一课](lessons/0001-memory-boundaries.html)，然后运行两个不需要模型密钥的基础实验：

```bash
cd learning/task07
uv sync
uv run python experiment/01-checkpointer/checkpointer_demo.py
uv run python experiment/02-store/store_demo.py
```

本章的实验与学习记录已完成；上述命令可用于重新观察 Checkpointer 与 Store 的边界。

## 第 9 章实验入口

从[第 9 章学习计划](ch09-human-in-the-loop/learning.md)进入课程。已验证的核心演示是[模拟发布审批](ch09-human-in-the-loop/experiment/05-capstone/capstone_exercise.py)；条件审批、并行中断 ID 和子 Agent 审批的独立演示也列在该计划中。

不要把真实 `.env`、数据库 URI 或 LangSmith 密钥提交到仓库。
