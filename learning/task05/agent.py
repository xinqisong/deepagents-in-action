"""Task 05 第 1 步：观察一次最小的子 Agent 委派。"""

import os

from deepagents import create_deep_agent
from deepagents.profiles import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    register_harness_profile,
)
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from tavily import TavilyClient


load_dotenv()


model = ChatOpenAI(
    model=os.environ["MODEL_NAME"],
    api_key=os.environ["SILICONFLOW_API_KEY"],
    base_url=os.environ["SILICONFLOW_API_BASE"],
)


# DeepAgents 默认还会自动加入 general-purpose。
# 这里先关闭它，确保本次实验只有我们定义的 researcher。
register_harness_profile(
    key=f"openai:{os.environ['MODEL_NAME']}",
    profile=HarnessProfile(
        general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
    ),
)


search_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


@tool
def internet_search(query: str, max_results: int = 5) -> str:
    """联网搜索课程主题，并返回标题、摘要和来源链接。"""

    result = search_client.search(query=query, max_results=max_results)
    rows = []
    for item in result.get("results", []):
        title = item.get("title", "")
        content = item.get("content", "")
        url = item.get("url", "")
        rows.append(
            "标题：" + title + chr(10)
            + "摘要：" + content + chr(10)
            + "来源：" + url
        )
    return (chr(10) + chr(10)).join(rows) or "没有找到搜索结果。"


research_subagent = {
    "name": "researcher",
    "description": "研究 DeepAgents 子 Agent 和上下文隔离，需要联网搜索资料并返回简洁摘要时使用。",
    "system_prompt": """
你是 researcher 子 Agent，负责研究 DeepAgents 第 5 章的概念。

执行要求：
1. 先使用 internet_search 搜索与问题最相关的课程资料；
2. 根据资料提炼核心结论；
3. 只返回不超过 200 字的摘要，不要返回工具原始内容或中间推理过程。
4. 输出格式必须包含：核心结论、适用场景、不适用场景、实际来源。
5. 每个来源必须写出搜索结果中的标题和完整 URL；如果没有真实 URL，明确写“没有找到可核验来源”，不要编造来源。
""",
    "tools": [internet_search],
}

fact_checker_subagent = {
    "name": "fact_checker",
    "description": "核验研究结论和来源 URL，发现无依据或夸大表述时指出",
    "system_prompt": """
你是事实核验专家。
检查 researcher 提供的结论：
1. 每个重要结论是否有来源；
2. 来源是否包含真实 URL；
3. 是否存在过度推断。
只返回核验结果和需要修正的地方。
""",
    "tools": [internet_search],
}


agent = create_deep_agent(
    model=model,
    system_prompt="""
你是主 Agent，也是一名协调者。

只要用户的问题涉及“子 Agent”或“上下文隔离”，必须使用 task 工具把问题委派给 researcher，
不要自己直接回答。收到 researcher 的结果后，用 3 个要点向用户总结，并明确说明答案来自子 Agent。
汇总时必须保留 researcher 返回的实际来源标题和完整 URL，不得把来源压缩成泛称。
""",
    subagents=[research_subagent, fact_checker_subagent],
)


result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "请解释为什么需要 Context Quarantine，以及子 Agent 适合处理什么任务。",
            }
        ]
    }
)


print("=== 调用轨迹摘要 ===")
for index, message in enumerate(result["messages"]):
    tool_calls = getattr(message, "tool_calls", []) or []
    called_tools = [call.get("name", "unknown") for call in tool_calls]
    print(
        f"{index}: {type(message).__name__}"
        f" | name={getattr(message, 'name', '') or '-'}"
        f" | tool_calls={called_tools or '-'}"
    )
    for call in tool_calls:
        if call.get("name") == "task":
            print(f"   task 参数: {call.get('args', {})}")
    if getattr(message, "name", "") == "task":
        print("   task 原始返回:")
        print(message.content)

print("\n=== 主 Agent 最终回答 ===")
print(result["messages"][-1].content)
