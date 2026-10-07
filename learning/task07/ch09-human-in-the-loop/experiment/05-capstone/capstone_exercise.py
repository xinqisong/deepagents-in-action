"""综合练习：为模拟发布配置审批，分别验证批准与拒绝。"""

import argparse
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


def build_exercise(approval_policy):
    published_drafts = []

    @tool
    def publish_draft(title: str) -> str:
        """模拟公开发布一份草稿，只追加到内存记录。"""
        published_drafts.append(title)
        return "模拟发布完成"

    agent = create_deep_agent(
        model=build_model(),
        tools=[publish_draft],
        system_prompt=(
            "这是工具审批教学实验。用户要求公开发布草稿时，"
            "调用且只调用一次 publish_draft(title='项目进度报告')。"
            "不要调用文件工具、子 Agent 或其他工具。"
            "若工具被拒绝，不重试，说明草稿未发布并结束。"
            "若工具成功，简短报告结果并结束。"
        ),
        interrupt_on=approval_policy,
        checkpointer=InMemorySaver(),
    )
    config = {"configurable": {"thread_id": "ch09-capstone-05"}, "recursion_limit": 20}
    return agent, config, published_drafts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("decision", choices=("approve", "reject"))
    selected = parser.parse_args().decision

    approval_policy = {
        "publish_draft": {"allowed_decisions": ["approve", "reject"]}
    }

    agent, config, published_drafts = build_exercise(approval_policy)
    paused = agent.invoke(
        {"messages": [{"role": "user", "content": "请公开发布项目进度报告草稿。"}]},
        config=config,
        version="v2",
    )
    print("暂停后，中断数量：", len(paused.interrupts))
    print("暂停后，模拟发布记录：", published_drafts)
    if len(paused.interrupts) != 1:
        print("未得到预期的单个审批中断；请检查策略和模型本轮回复。")
        return

    review = paused.interrupts[0].value
    print("待审批动作：", review["action_requests"])
    print("可选决定：", review["review_configs"])
    if len(review["action_requests"]) != 1:
        print("本轮待审批动作不是一个；请根据实际输出检查。")
        return

    decision = {"type": selected}
    if selected == "reject":
        decision["message"] = "不要公开发布这份草稿。"
    resumed = agent.invoke(
        Command(resume={"decisions": [decision]}),
        config=config,
        version="v2",
    )
    print("恢复后，中断数量：", len(resumed.interrupts))
    print("恢复后，模拟发布记录：", published_drafts)


if __name__ == "__main__":
    main()
