"""Exercise real DeepAgents delegation and approval with a scripted chat model."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from langgraph.types import Command

from course_brief_agent.agent import build_agent
from course_brief_agent.offline_model import BRIEF_BODY, BRIEF_TITLE, ScriptedModel
from course_brief_agent.tools import make_publish_tool, read_course_source


def check(decision: str) -> None:
    with TemporaryDirectory(prefix=f"task08-{decision}-") as directory:
        published_dir = Path(directory) / "published"
        model = ScriptedModel()
        agent = build_agent(model, published_dir=published_dir)
        config = {"configurable": {"thread_id": f"offline-{decision}"}}
        paused = agent.invoke(
            {"messages": [{"role": "user", "content": "查证并发布简报"}]},
            config=config,
            version="v2",
        )
        assert model.calls == 5, model.calls
        assert len(paused.interrupts) == 1, paused.interrupts
        assert not list(published_dir.glob("*.md")), "审批前已经发布"
        messages = paused.value["messages"]
        assert any(
            getattr(message, "name", None) == "task"
            and "source-01.md" in str(message.content)
            for message in messages
        ), "主 Agent 没有收到 researcher 的查证结果"
        assert not any(
            getattr(message, "name", None) == "read_course_source" for message in messages
        ), "研究子 Agent 的内部工具消息泄漏到主 Agent 上下文"
        assert paused.interrupts[0].value["action_requests"][0]["name"] == "publish_brief"

        choice = {"type": decision}
        if decision == "reject":
            choice["message"] = "离线验证拒绝发布"
        resumed = agent.invoke(
            Command(resume={"decisions": [choice]}),
            config=config,
            version="v2",
        )
        assert not resumed.interrupts, resumed.interrupts
        files = list(published_dir.glob("*.md"))
        assert len(files) == (1 if decision == "approve" else 0), files
        if decision == "approve":
            make_publish_tool(published_dir).invoke(
                {"title": BRIEF_TITLE, "body": BRIEF_BODY}
            )
            assert list(published_dir.glob("*.md")) == files, "重复请求产生了第二份文件"
    print(f"PASS: {decision}，同步委派已完成，审批边界正确")


if __name__ == "__main__":
    assert "未知 source_id" in read_course_source.invoke({"source_id": "../.env"})
    check("approve")
    check("reject")
