"""同批两个工具审批：根据实际 action_requests 顺序填写 decisions。"""

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
    executed_calls = []

    @tool
    def update_preference(key: str, value: str) -> str:
        """模拟更新一项偏好，只记录到内存。"""
        executed_calls.append({"key": key, "value": value})
        return "模拟更新完成"

    agent = create_deep_agent(
        model=build_model(),
        tools=[update_preference],
        system_prompt=(
            "这是同批工具审批教学实验。请在同一轮模型回复中一次性提出恰好两个工具调用："
            "update_preference(key='language', value='中文') 和 "
            "update_preference(key='theme', value='深色')。"
            "不要等待第一个工具的结果再提出第二个，也不要调用其他工具。"
            "审批后，已拒绝的调用不要重试；只简短报告结果并结束。"
        ),
        interrupt_on={
            "update_preference": {"allowed_decisions": ["approve", "reject"]}
        },
        checkpointer=InMemorySaver(),
    )
    config = {
        "configurable": {"thread_id": "ch09-batch-02"},
        "recursion_limit": 20,
    }
    return agent, config, executed_calls


def main():
    # 按实际 action_requests 顺序填写：批准 language，拒绝 theme。
    decisions = [
    {"type": "approve"},
    {"type": "reject", "message": "保持原主题"},
    ]

    agent, config, executed_calls = build_exercise()
    print("正在请求真实模型，等待同批两个审批动作……", flush=True)
    paused = agent.invoke(
        {"messages": [{"role": "user", "content": "请将语言改为中文，主题改为深色。"}]},
        config=config,
        version="v2",
    )
    print("暂停后，中断数量：", len(paused.interrupts))
    print("暂停后，执行记录：", executed_calls)
    if len(paused.interrupts) != 1:
        print("本轮未得到单个审批批次；请把实际输出发给老师。")
        return

    interrupt_value = paused.interrupts[0].value
    actions = interrupt_value["action_requests"]
    reviews = interrupt_value["review_configs"]
    for index, (action, review) in enumerate(zip(actions, reviews, strict=True)):
        print(f"动作 {index}：{action['name']} {action['args']}")
        print(f"动作 {index} 可选决定：{review['allowed_decisions']}")

    if len(actions) != 2:
        print("真实模型本轮没有一次提出两个待审批动作；请把动作列表发给老师。")
        return
    if decisions is None:
        print("请按上面的动作顺序填写 decisions，再重新运行。")
        return

    resumed = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,
        version="v2",
    )
    print("恢复后，中断数量：", len(resumed.interrupts))
    print("恢复后，执行记录：", executed_calls)
    if resumed.interrupts:
        print("模型再次提出审批动作；请把实际输出发给老师。")


if __name__ == "__main__":
    main()
