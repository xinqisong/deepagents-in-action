"""一个故意较慢的后台子 Agent，用来稳定观察异步生命周期。"""

import asyncio

from langgraph.graph import END, START, MessagesState, StateGraph


async def slow_research(state: MessagesState) -> dict[str, list[dict[str, str]]]:
    """模拟长任务；收到 update 时，最新指令会成为最后一条消息。"""

    last_message = state["messages"][-1] if state["messages"] else None
    latest_instruction = getattr(last_message, "content", None) or "没有收到任务说明。"

    # await asyncio.sleep(8)
    await asyncio.sleep(20)
    return {
        "messages": [
            {
                "role": "ai",
                "content": (
                    "[researcher finished after 8s]\n"
                    f"latest instruction: {latest_instruction}\n"
                    "summary: background async work can be checked, updated, "
                    "cancelled, and listed by the supervisor."
                ),
            }
        ]
    }


builder = StateGraph(MessagesState)
builder.add_node("slow_research", slow_research)
builder.add_edge(START, "slow_research")
builder.add_edge("slow_research", END)
graph = builder.compile()
