"""Run a real-model research brief and decide whether to simulate publication."""

from __future__ import annotations

import argparse
from uuid import uuid4

from langgraph.types import Command

from course_brief_agent.agent import build_agent
from course_brief_agent.model import build_model
from course_brief_agent.offline_model import ScriptedModel
from course_brief_agent.tools import PROJECT_ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline", action="store_true", help="使用固定脚本模型，不需要 API Key"
    )
    args = parser.parse_args()
    thread_id = f"task08-{uuid4()}"
    published_dir = PROJECT_ROOT / "published" / thread_id
    agent = build_agent(
        ScriptedModel() if args.offline else build_model(),
        published_dir=published_dir,
    )
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 35}
    paused = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请根据两份本地课程资料制作《研究 Agent 的委派与安全发布》简报。"
                        "先请 research-agent 查证，再提交简报供我审批发布。"
                    ),
                }
            ]
        },
        config=config,
        version="v2",
    )
    messages = paused.value["messages"]
    delegated = any(
        call.get("name") == "task"
        for message in messages
        for call in getattr(message, "tool_calls", [])
    )
    findings = [
        str(message.content)
        for message in messages
        if getattr(message, "name", None) == "task"
    ]
    print("同步委派：", "已发生" if delegated else "未观察到")
    if findings:
        print("research-agent 返回：\n", findings[-1])
    if not delegated or not findings:
        print("本轮没有完成可验证的子 Agent 查证；停止审批。")
        return

    if len(paused.interrupts) != 1:
        print(f"预期一个发布审批中断，实际得到 {len(paused.interrupts)} 个。")
        if not paused.interrupts:
            print("最后回复：", messages[-1].content)
        return
    review = paused.interrupts[0].value
    actions = review.get("action_requests", [])
    if len(actions) != 1 or actions[0].get("name") != "publish_brief":
        print("待审批动作不符合预期：", actions)
        return
    arguments = actions[0].get("args", actions[0].get("arguments", {}))
    print("\n=== 待审简报 ===")
    print("标题：", arguments.get("title"))
    print(arguments.get("body"))
    print("审批前发布文件数：", len(list(published_dir.glob("*.md"))))

    choice = input("输入 approve 批准；直接回车或输入 reject 拒绝：").strip().lower()
    while choice not in {"", "approve", "reject"}:
        choice = input("请输入 approve 或 reject：").strip().lower()
    decision = {"type": "approve" if choice == "approve" else "reject"}
    if decision["type"] == "reject":
        decision["message"] = "简报本轮不发布，请结束。"
    resumed = agent.invoke(
        Command(resume={"decisions": [decision]}),
        config=config,
        version="v2",
    )
    print("恢复后中断数量：", len(resumed.interrupts))
    print("恢复后发布文件数：", len(list(published_dir.glob("*.md"))))
    if resumed.interrupts:
        print("又出现待审批动作；本脚本不会自动继续。")
    else:
        print("最终回复：", resumed.value["messages"][-1].content)


if __name__ == "__main__":
    main()
