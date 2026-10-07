"""Fixed local evidence and a local-only simulated publication action."""

from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_core.tools import tool

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "data"
SOURCE_IDS = ("source-01.md", "source-02.md")


@tool
def list_course_sources() -> str:
    """List the two local course sources available to the research agent."""
    return "\n".join(SOURCE_IDS)


@tool
def read_course_source(source_id: str) -> str:
    """Read one listed local source by source_id, such as source-01.md."""
    if source_id not in SOURCE_IDS:
        return f"未知 source_id：{source_id}。请先调用 list_course_sources。"
    return f"source_id: {source_id}\n{(SOURCE_DIR / source_id).read_text(encoding='utf-8')}"


def make_publish_tool(published_dir: Path):
    """Bind simulated publication to one run's output directory."""

    @tool
    def publish_brief(title: str, body: str) -> str:
        """Publish a reviewed course brief to a local Markdown file after approval."""
        title = title.strip()
        body = body.strip()
        if not title or not body:
            raise ValueError("标题和正文不能为空")
        if any(source_id not in body for source_id in SOURCE_IDS):
            raise ValueError("正文必须引用 source-01.md 和 source-02.md")
        contents = f"# {title}\n\n{body}\n"
        digest = hashlib.sha256(contents.encode("utf-8")).hexdigest()[:16]
        published_dir.mkdir(parents=True, exist_ok=True)
        target = published_dir / f"brief-{digest}.md"
        if not target.exists():
            target.write_text(contents, encoding="utf-8")
        return f"模拟发布完成：{target}"

    return publish_brief
