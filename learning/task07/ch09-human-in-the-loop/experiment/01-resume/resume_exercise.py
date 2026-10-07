"""真实模型审批练习：读取 task07/.env，只填写 main() 中的 decisions。"""

import os
from pathlib import Path
from urllib.parse import urlsplit

# 本练习只观察本地状态，不上报 tracing。
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from deepagents import create_deep_agent
from dotenv import dotenv_values
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


def build_model():
    # 按脚本位置寻找配置，从仓库根目录或 IDE 运行均可。
    env_path = Path(__file__).resolve().parents[3] / ".env"
    settings = dotenv_values(env_path)
    required = ("MODEL_NAME", "SILICONFLOW_API_KEY", "SILICONFLOW_API_BASE")
    missing = [key for key in required if not settings.get(key)]
    if missing:
        raise RuntimeError(f"请在 {env_path} 填写：{', '.join(missing)}")

    # 变量名称沿用上一章，实际服务商由 API_BASE 决定。
    base_url = settings["SILICONFLOW_API_BASE"]
    extra_body = {}
    if urlsplit(base_url).hostname == "api.deepseek.com":
        # 本课只练 HITL，不处理思考模式的 reasoning_content 回传。
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
        """模拟记录一次偏好更新，不写入真实 Store。"""
        executed_calls.append({"key": key, "value": value})
        return "模拟更新完成"

    agent = create_deep_agent(
        model=build_model(),
        tools=[update_preference],
        system_prompt=(
            "这是单次工具审批教学实验。用户要求保存语言偏好时，"
            "直接调用且只调用一次 update_preference(key='language', value='中文')。"
            "不使用文件工具、子 Agent 或其他工具。"
            "工具执行成功后简短报告结果并结束；若被拒绝，不重试，说明未修改并结束。"
        ),
        interrupt_on={
            "update_preference": {"allowed_decisions": ["approve", "reject"]}
        },
        checkpointer=InMemorySaver(),
    )
    config = {
        "configurable": {"thread_id": "ch09-resume-01"},
        "recursion_limit": 20,
    }
    return agent, config, executed_calls


def main():
    decision = {"type": "approve"}
    decisions = [decision]

    agent, config, executed_calls = build_exercise()
    print("正在请求真实模型，等待工具审批中断……", flush=True)
    paused = agent.invoke(
        {"messages": [{"role": "user", "content": "请把语言偏好保存为中文。"}]},
        config=config,
        version="v2",
    )
    print("暂停后，中断数量：", len(paused.interrupts))
    print("暂停后，执行记录：", executed_calls)
    if not paused.interrupts:
        print("模型本轮没有产生审批中断，请检查回复与执行记录：")
        print(paused.value["messages"][-1].content)
        return
    print("待审批动作：", paused.interrupts[0].value["action_requests"])

    snapshot = agent.get_state(config)
    print("下一步待执行节点：", snapshot.next)
    print("待处理任务：", snapshot.tasks)

    if decisions is None:
        print("请填写 decisions 后重新运行；每次运行都会重新创建本轮练习。")
        return

    resumed = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,
        version="v2",
    )
    finished = agent.get_state(config)
    print("恢复后待执行节点：", finished.next)
    print("恢复后待处理任务：", finished.tasks)
    print("恢复后，中断数量：", len(resumed.interrupts))
    print("恢复后，执行记录：", executed_calls)
    if resumed.interrupts:
        print("模型又提出了需要审批的动作；尚未结束，请把输出发给老师一起检查。")


if __name__ == "__main__":
    main()
