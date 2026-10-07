"""真实模型演示：同一个工具仅在公开保存时触发审批。"""

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


def run_case(visibility: str):
    saved_drafts = []

    @tool
    def save_draft(visibility: str) -> str:
        """模拟按可见范围保存草稿，只写内存记录。"""
        saved_drafts.append(visibility)
        return "模拟保存完成"

    def needs_approval(request) -> bool:
        return request.tool_call["args"].get("visibility") == "public"

    agent = create_deep_agent(
        model=build_model(),
        tools=[save_draft],
        system_prompt=(
            "这是条件审批教学实验。直接且只调用一次 "
            f"save_draft(visibility='{visibility}')。"
            "不使用文件工具、子 Agent 或其他工具。执行后简短报告并结束。"
        ),
        interrupt_on={
            "save_draft": {
                "allowed_decisions": ["approve", "reject"],
                "when": needs_approval,
            }
        },
        checkpointer=InMemorySaver(),
    )
    config = {
        "configurable": {"thread_id": f"ch09-when-{visibility}"},
        "recursion_limit": 20,
    }
    paused = agent.invoke(
        {"messages": [{"role": "user", "content": f"请将草稿保存为 {visibility}。"}]},
        config=config,
        version="v2",
    )
    print(f"{visibility}：首次中断数={len(paused.interrupts)}，保存记录={saved_drafts}")
    if visibility == "public" and len(paused.interrupts) == 1:
        print("公开保存的待审批动作：", paused.interrupts[0].value["action_requests"])
        resumed = agent.invoke(
            Command(resume={"decisions": [{"type": "approve"}]}),
            config=config,
            version="v2",
        )
        print(f"{visibility}：恢复后中断数={len(resumed.interrupts)}，保存记录={saved_drafts}")


def main():
    run_case("private")
    run_case("public")


if __name__ == "__main__":
    main()
