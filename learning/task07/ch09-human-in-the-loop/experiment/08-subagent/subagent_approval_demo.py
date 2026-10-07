"""真实模型演示：发布工具只交给子 Agent，并在子 Agent 内审批。"""

import os
from pathlib import Path
from urllib.parse import urlsplit

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from deepagents import create_deep_agent
from dotenv import dotenv_values
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


def build_model():
    env_path = Path(__file__).resolve().parents[3] / ".env"
    settings = dotenv_values(env_path)
    required = ("MODEL_NAME", "SILICONFLOW_API_KEY", "SILICONFLOW_API_BASE")
    missing = [key for key in required if not settings.get(key)]
    if missing:
        raise RuntimeError(f"请在 {env_path} 填写：{', '.join(missing)}")

    base_url = settings["SILICONFLOW_API_BASE"]
    extra_body = {}
    if urlsplit(base_url).hostname == "api.deepseek.com":
        extra_body["thinking"] = {"type": "disabled"}
    return ChatOpenAI(
        model=settings["MODEL_NAME"],
        api_key=settings["SILICONFLOW_API_KEY"],
        base_url=base_url,
        extra_body=extra_body,
        timeout=60,
        max_retries=0,
    )


def build_exercise():
    published_drafts = []

    @tool
    def publish_draft(title: str) -> str:
        """模拟公开发布草稿，只记录到内存。"""
        published_drafts.append(title)
        return "模拟发布完成"

    agent = create_deep_agent(
        model=build_model(),
        tools=[],
        system_prompt=(
            "这是子 Agent 审批教学实验。你不能直接发布。"
            "收到发布请求后，只调用一次 task 工具，"
            "subagent_type='publisher'，description 明确要求子 Agent 调用"
            "publish_draft(title='项目进度报告')。"
            "子 Agent 返回后简短报告结果并结束，不要使用其他工具。"
        ),
        subagents=[
            {
                "name": "publisher",
                "description": "模拟发布报告草稿；由子 Agent 内的审批策略保护发布工具。",
                "system_prompt": (
                    "你是发布子 Agent。接到项目进度报告发布任务后，"
                    "直接且只调用一次 publish_draft(title='项目进度报告')。"
                    "工具被拒绝时不要重试。不要使用其他工具。"
                ),
                "tools": [publish_draft],
                "interrupt_on": {
                    "publish_draft": {"allowed_decisions": ["approve", "reject"]}
                },
            }
        ],
        checkpointer=InMemorySaver(),
    )
    config = {"configurable": {"thread_id": "ch09-subagent-08"}, "recursion_limit": 30}
    return agent, config, published_drafts


def main():
    agent, config, published_drafts = build_exercise()
    paused = agent.invoke(
        {"messages": [{"role": "user", "content": "请发布项目进度报告草稿。"}]},
        config=config,
        version="v2",
    )
    print("暂停后中断数量：", len(paused.interrupts))
    print("暂停后模拟发布记录：", published_drafts)
    if not paused.interrupts:
        print("本轮没有审批中断；模型最后回复：", paused.value["messages"][-1].content)
        return

    for item in paused.interrupts:
        print("待审批动作：", item.value.get("action_requests", item.value))
    resumed = agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,
        version="v2",
    )
    print("恢复后中断数量：", len(resumed.interrupts))
    print("恢复后模拟发布记录：", published_drafts)


if __name__ == "__main__":
    main()
