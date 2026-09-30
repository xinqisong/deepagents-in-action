"""主 Agent：通过 AsyncSubAgent 控制后台 researcher。"""

import os

from deepagents import AsyncSubAgent, create_deep_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4.1-mini"),
    api_key=os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("SILICONFLOW_API_BASE", "https://api.openai.com/v1"),
)

graph = create_deep_agent(
    model=model,
    system_prompt="""
你是 task06 的 supervisor，负责管理后台异步子 Agent。

规则：
1. 用户要求执行长时间研究、编码或迁移任务时，立即调用 start_async_task。
2. start_async_task 返回后，立刻把完整 task_id 告诉用户，不要在同一轮主动轮询。
3. 用户询问进度时，必须先调用 check_async_task 或 list_async_tasks；不能引用旧消息中的状态。
4. 用户要求修改任务时，调用 update_async_task；不要重新启动一个新任务。
5. 用户要求停止时，调用 cancel_async_task；必要时再 check 确认最终状态。
6. 始终保留完整 task_id，不要截断、缩写或改写。
7. 任务 success 只表示运行结束，不代表研究结论已经经过事实核验。
""",
    subagents=[
        AsyncSubAgent(
            name="researcher",
            description=(
                "适合需要多次搜索、综合资料或持续数分钟的后台研究任务；"
                "本实验会故意等待 8 秒，便于观察任务状态变化。"
            ),
            graph_id="researcher",
            url="http://127.0.0.1:2024",
        )
    ],
)

