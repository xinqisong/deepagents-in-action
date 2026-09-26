# Task 05：子 Agent 与上下文隔离

本目录对应课程第 5 章“子 Agent 与上下文隔离——让 Agent 学会委派”。

课程原文：

<https://datawhalechina.github.io/deepagents-in-action/chapters/ch05-subagents/>

## 学习方式

本章按小实验推进，每次只增加一个概念：

1. 最小委派：主 Agent 调用一个 `researcher` 子 Agent；
2. 上下文隔离：观察子 Agent 的工具调用不会全部堆进主 Agent；
3. 字典方式配置：理解 `name`、`description`、`system_prompt` 和工具继承；
4. 多子 Agent 协作：再增加专业分工；
5. `CompiledSubAgent` 和结构化输出：最后再处理复杂工作流和 JSON 契约。

本章的最小委派、上下文隔离、CompiledSubAgent、多子 Agent 顺序协作和结构化 JSON 校验实验已经完成；下一步学习异步子 Agent与并行编排。

## 当前文件

```text
task05/
├── agent.py                    # researcher 与 fact_checker 委派实验
├── url_branch_demo.py          # URL 路由、抓取、证据提取和结构化结果
├── compiled_subagent_demo.py   # 将编译图接入 DeepAgents
├── learning.md                 # 完整学习记录、问题与实验清单
├── pyproject.toml    # Python 依赖
└── .env.example      # 环境变量模板，不包含密钥
```

## 开始运行

在仓库根目录执行：

```bash
cd learning/task05
cp .env.example .env
# 编辑 .env，填写模型名称、API Key 和 Base URL
uv sync
uv run python agent.py
uv run python url_branch_demo.py
timeout 120s uv run python compiled_subagent_demo.py
```

不要把真实的 `.env`、API Key 或其他私密配置提交到 Git。

详细学习过程、问题记录和下一步计划见 `learning.md`。
