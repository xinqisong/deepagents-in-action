# Task 06：异步子 Agent 与并行编排

本目录对应课程第 6 章“异步子 Agent——让主 Agent 同时驱动多个子任务”。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/>

章节源码：

<https://github.com/datawhalechina/deepagents-in-action/blob/main/content/ch06-async-subagents.md>

## 本章要解决的问题

task05 的同步 `task` 委派适合“交给专家，然后等待结果”。如果子任务需要几分钟、需要中途追加约束，或者用户还想继续和主 Agent 对话，主 Agent 就不应该被同步调用阻塞。

本章学习 `AsyncSubAgent`：主 Agent 启动后台任务后立即拿到完整 `task_id`，随后根据用户请求查询、追加指令、取消或列出任务。

## 文件说明

```text
task06/
├── README.md
├── learning.md                         # 知识地图、琐碎要点、学习计划和验收标准
├── pyproject.toml                      # 本章独立依赖
├── .env.example                        # 环境变量模板，不含密钥
├── langgraph.json                      # supervisor + researcher 的服务注册
├── run_demo.py                         # 使用 LangGraph SDK 验证生命周期
├── graphs/
│   ├── researcher.py                   # 故意延迟 8 秒的后台子 Agent
│   └── supervisor.py                   # 配置 AsyncSubAgent 的主 Agent
├── reference/
│   └── async-subagents-reference.html  # 可打印速查页
├── lessons/
│   └── 0001-async-lifecycle.html       # 第一课：先建立生命周期心智模型
└── assets/
    └── reference.css                   # 参考页和课程页共用样式
```

## 开始实验

先复制环境变量模板并填写模型和 LangSmith 配置：

```bash
cd learning/task06
cp .env.example .env
uv sync
```

启动本地 Agent Server。`--n-jobs-per-worker 4` 是为了给 supervisor 和后台 researcher 留出并发槽位：

```bash
uv run langgraph dev --n-jobs-per-worker 4
```

另开终端运行 SDK 验证脚本：

```bash
cd learning/task06
uv run python run_demo.py
```

预期观察到：第一次请求很快返回任务 ID；随后可以查询 `running`，追加指令；等待几秒后再次查询，状态变为 `success`。

## 重要边界

- 本章的“异步”不是把 Python 函数改成 `async def` 就结束，而是 Agent Protocol 服务上的后台任务生命周期。
- `AsyncSubAgent` 需要 `name`、`description`、`graph_id`；`graph_id` 必须和 `langgraph.json` 的注册名一致。
- 不写 `url` 是同部署 ASGI；写 `url` 是远程 HTTP。先学 ASGI，再学习拆分部署。
- 当前本地 `deepagents==0.7.19` 的类型说明强调：省略 `url` 的 ASGI 传输需要异步父入口，例如 `ainvoke`；同步 `invoke` 适用于有 URL 的可访问 Agent Protocol 服务。
- 任务完成只说明运行生命周期结束，不说明研究结论正确；仍要做内容验收、来源核对或人工审核。
- 永远保留完整 `task_id`，不要从旧消息猜状态；回答进度前先 `check_async_task` 或 `list_async_tasks`。
- `cancelled`、`interrupted` 不要混为一个层次：取消工具可以先返回/缓存 `cancelled`，而后续 check 读取服务端 run 或 tracing 时可能观察到 `interrupted`。排障时同时记录 task/thread/run ID 和状态来源。

