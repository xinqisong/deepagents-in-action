# 实验 4：Agent 写入长期记忆，再由新 thread 读取

这个实验首次需要真实模型，因为要观察 Agent 是否真的调用 edit_file 修改记忆文件。

准备：

1. 在 task07 目录创建 .env；
2. 填写模型和 API 配置；
3. 不要把 .env 提交到 Git。

运行：

    cd learning/task07
    cp .env.example .env
    uv sync
    uv run python experiment/04-memory-write/write_and_read_demo.py

实验分成三份证据：

1. 第一轮请求明确要求“记住”；
2. Python 直接从 Store 读取并断言内容，证明写入确实发生；
3. 第二轮使用全新的 thread_id，观察 Agent 是否使用这份长期记忆。

如果模型回复“已记住”但 Store 断言失败，实验应判定为失败；模型的自然语言不是持久化证据。
