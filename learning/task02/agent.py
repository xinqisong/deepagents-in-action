import os

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

load_dotenv()

model = ChatOpenAI(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url=os.environ["SILICONFLOW_API_BASE"],
)

def get_weather(city: str) -> str:
    """查询指定城市天气。"""
    return f"[TOOL_CALLED] {city}：今天晴天，气温 25°C。"

def calculator(a: float, b: float, operation: str) -> float:
    """执行两个数字的基本四则运算。operation 只能是 +、-、*、/。"""

    if operation == "+":
        return a + b
    if operation == "-":
        return a - b
    if operation == "*":
        return a * b
    if operation == "/":
        if b == 0:
            raise ValueError("除数不能为 0")
        return a / b

    raise ValueError("不支持的运算符")

def internet_search(query: str, max_results: int = 3) -> str:
    """搜索互联网并返回标题、链接和摘要。"""

    client = TavilyClient(
        api_key=os.environ["TAVILY_API_KEY"]
    )

    response = client.search(
        query=query,
        max_results=max_results,
    )

    results = []

    for item in response.get("results", []):
        results.append(
            f"标题：{item.get('title')}\n"
            f"链接：{item.get('url')}\n"
            f"摘要：{item.get('content')}"
        )

    return "\n\n".join(results)

agent = create_deep_agent(
    model=model,
    tools=[get_weather, calculator, internet_search],
    system_prompt="""
    你是一个助手。
    用户询问天气时，调用 get_weather。
    用户提出数学计算时，调用 calculator。
    涉及网络信息或最新资料时，必须调用 internet_search。
    """,
)


result = agent.invoke(
    {
        "messages":[
            {
                "role": "user",
                "content": "请搜索 DeepAgents 官方资料，并总结它的主要功能，同时提供来源链接。"
            }
        ]
    }
)

print(result["messages"][-1].content)
