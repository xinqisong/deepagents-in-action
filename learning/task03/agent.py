import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


BASE_DIR = Path(__file__).resolve().parent
WORKSPACE = BASE_DIR / "workspace"
WORKSPACE.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

model = ChatOpenAI(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url=os.environ["SILICONFLOW_API_BASE"],
)

backend = FilesystemBackend(
    root_dir=str(WORKSPACE),
    virtual_mode=True,
)

agent = create_deep_agent(
    model=model,
    backend=backend,
    system_prompt="""
你正在学习 Deep Agents 第 3 章：虚拟文件系统。
请优先使用文件系统工具完成任务，不要把所有文件内容直接堆在最终回答中。
先观察目录，再按需读取和搜索；需要新建总结时使用 write_file，
需要局部修改时使用 edit_file。只能访问实验工作区，不能尝试读取工作区之外的路径。
最后说明你实际使用了哪些工具，以及 workspace 中发生了哪些变化。
""",
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
请完成一次虚拟文件系统练习：

1. 列出当前工作区中的文件；
2. 读取 lesson-source.md，并找出包含 Backend 或 context 的内容；
3. 将关键内容整理为 workspace/ch03-summary.md；
4. 再读取刚才的总结，检查是否遗漏；
5. 如果发现明显表述问题，只做一次精确的局部编辑；
6. 最后用中文汇报工具调用顺序、生成的文件和你对“文件系统如何帮助管理上下文”的理解。
""",
            }
        ]
    }
)

for message in result["messages"]:
    print("消息类型：", type(message).__name__)

    tool_calls = getattr(message, "tool_calls", [])

    if tool_calls:
        for call in tool_calls:
            print("模型调用工具：", call["name"])

    print("---")

print(result["messages"][-1].content)
