"""Inspect pending human-in-the-loop actions before deciding."""

from demo import TenantContext, agent


def main() -> None:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请读取 shared 和 personal Skill，尝试修改两个 Skill，"
                        "然后把权限观察报告写入 /reports/policy.md。"
                    ),
                }
            ]
        },
        context=TenantContext(org_id="org-acme", user_id="alice"),
        config={"configurable": {"thread_id": "task06-ch07-store-permissions-inspect"}},
    )
    interrupts = result.get("__interrupt__", [])
    for interrupt in interrupts:
        for action in interrupt.value.get("action_requests", []):
            print(action["name"], action["args"].get("file_path"))


if __name__ == "__main__":
    main()
