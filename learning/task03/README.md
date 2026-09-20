# Task 03：虚拟文件系统与上下文管理

本目录对应课程第 3 章“虚拟文件系统 — Deep Agents 的 Context Engineering 核心”。本次学习的目标不是记住几个文件工具，而是理解：Agent 如何把中间结果放到上下文之外，需要时再检索回来。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/>

## 文件说明

```text
task03/
├── agent.py              # 使用 FilesystemBackend 的最小实验
├── learning.md           # 本次学习总结、路线和实验记录
├── pyproject.toml        # Python 依赖
├── .env.example          # 环境变量模板，不包含密钥
└── workspace/            # Agent 的虚拟文件系统根目录
    └── lesson-source.md  # 实验用的初始资料
```

## 开始运行

在本目录执行：

```bash
cp .env.example .env
# 编辑 .env，填写模型配置和 API Key
uv sync
uv run python agent.py
```

实验运行后，Agent 生成或修改的文件会出现在 `workspace/` 中。这个目录是专门为实验准备的工作区，不要把真实的 `.env`、私钥或生产配置放进去。

## 本次实验

`agent.py` 使用：

- `FilesystemBackend` 将 Agent 的文件操作限制在 `workspace/`。
- `virtual_mode=True` 开启路径沙箱，避免通过 `..` 越出根目录。
- 一个要求 Agent 列目录、读取资料、搜索关键词、写入总结并再次读取的任务。

完成基础实验后，按照 `learning.md` 继续对比 `StateBackend`、`StoreBackend`、`CompositeBackend`，并记录安全边界。
