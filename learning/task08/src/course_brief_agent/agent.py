"""Adapt the AgentSeek research coordinator/researcher graph for approval."""

from __future__ import annotations

from pathlib import Path

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

from course_brief_agent.prompts import COORDINATOR_PROMPT, RESEARCHER_PROMPT
from course_brief_agent.tools import (
    PROJECT_ROOT,
    list_course_sources,
    make_publish_tool,
    read_course_source,
)


def build_agent(model, *, published_dir: Path | None = None, checkpointer=None):
    """Build the synchronous research flow and approval-gated publish tool."""
    return create_deep_agent(
        model=model,
        tools=[make_publish_tool(published_dir or PROJECT_ROOT / "published" / "service")],
        system_prompt=COORDINATOR_PROMPT,
        subagents=[
            {
                "name": "research-agent",
                "description": "查证两份本地课程资料，返回带 source_id 的事实供主 Agent 写简报。",
                "system_prompt": RESEARCHER_PROMPT,
                "tools": [list_course_sources, read_course_source],
            }
        ],
        interrupt_on={
            "publish_brief": {"allowed_decisions": ["approve", "reject"]}
        },
        checkpointer=checkpointer if checkpointer is not None else InMemorySaver(),
    )
