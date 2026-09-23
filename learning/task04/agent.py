import os
from typing import Literal

from langchain_openai import ChatOpenAI
from tavily import TavilyClient

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents.middleware import TodoListMiddleware


load_dotenv()

model = ChatOpenAI(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url=os.environ["SILICONFLOW_API_BASE"],
)

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(query: str, max_results: int = 5) -> dict:
    """搜索互联网获取最新的网站设计资料。"""
    return tavily_client.search(query, max_results=max_results)


agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    middleware=[TodoListMiddleware()],
    system_prompt="""
你是一位专业的网站设计研究员。
面对复杂的网站设计任务时，你会：
1. 先用 write_todos 制定研究计划
2. 逐步执行每个步骤，及时更新进度
3. 将搜索结果整理到研究结论中
4. 最终输出完整的网站首页设计方案
""",
)


result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
请为一个面向 Agent 开发者的中文课程网站设计首页方案。

要求：
1. 先规划任务步骤；
2. 调研 3 个可靠的网站设计或技术教育网站资料来源；
3. 提炼首页的信息架构、视觉层级、核心区块和主要 CTA；
4. 给出一份可交给前端开发的首页设计 brief；
5. 最后列出验收清单，并说明哪些任务状态已经完成、哪些结论仍需要人工判断。
6. 如果调研过程中发现品牌定位、商业模式或真实数据等关键前提缺失，请动态增加一个“整理待业务方确认事项”的任务，不要把未确认信息当成事实。
""",
            }
        ]
    }
)

print(result["messages"][-1].content)
