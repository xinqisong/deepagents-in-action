# Task 07：长期记忆与 CompositeBackend

本目录对应课程第 8 章“长期记忆——让 Agent 拥有跨对话的记忆”。学习目标不是背 API，而是亲眼区分：

- `Checkpointer`：同一个 `thread_id` 内的短期状态；
- `Store`：跨线程、按 namespace 隔离的长期数据；
- `CompositeBackend`：按虚拟路径把临时文件和持久化记忆路由到不同后端。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch08-long-term-memory/>

官方主资料：

<https://docs.langchain.com/oss/python/deepagents/memory>

## 当前分支

本章实验分支是 `learning/task07`。Git 不允许使用带空格的 `learning task07` 作为分支名，因此采用了等价的层级命名。

## 文件说明

```text
task07/
├── README.md
├── MISSION.md
├── RESOURCES.md
├── NOTES.md
├── learning.md                         # 分阶段学习计划与验收标准
├── pyproject.toml                      # 本章独立依赖声明
├── experiment/
│   ├── README.md
│   ├── observations.md                 # 每次实验的观察记录模板
│   ├── 01-checkpointer/                # thread-scoped 短期记忆
│   ├── 02-store/                       # cross-thread 长期存储与 namespace
│   └── 03-composite-backend/           # 下一步：路径路由与 Deep Agent
├── lessons/
│   └── 0001-memory-boundaries.html    # 第一课：先分清两种记忆
├── reference/
│   └── long-term-memory-reference.html
└── learning-records/
    └── README.md                       # 完成实验后再写正式学习记录
```

## 从这里开始

先读 [第一课](lessons/0001-memory-boundaries.html)，然后运行两个不需要模型密钥的基础实验：

```bash
cd learning/task07
uv sync
uv run python experiment/01-checkpointer/checkpointer_demo.py
uv run python experiment/02-store/store_demo.py
```

把输出和自己的解释写进 [观察记录](experiment/observations.md)。完成后再进入 `learning.md` 的 Session 2，配置模型并实验 `CompositeBackend`。

不要把真实 `.env`、数据库 URI 或 LangSmith 密钥提交到仓库。
