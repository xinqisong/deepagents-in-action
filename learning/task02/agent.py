import os

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

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

agent = create_deep_agent(
    model=model,
    tools=[get_weather, calculator],
    system_prompt="""
    你是一个助手。
    用户询问天气时，调用 get_weather。
    用户提出数学计算时，调用 calculator。
    """,
)


result = agent.invoke(
    {
        "messages":[
            {
                "role": "user",
                "content": "请计算 123 乘以 45。"
            }
        ]
    }
)

print(result["messages"][-1].content)
