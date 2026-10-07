"""OpenAI-compatible model configuration matching Task 01's environment names."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from course_brief_agent.tools import PROJECT_ROOT


def build_model() -> ChatOpenAI:
    load_dotenv(PROJECT_ROOT / ".env")
    provider = os.getenv("AGENTSEEK_MODEL_PROVIDER", "openai")
    if provider != "openai":
        raise ValueError("本 demo 使用 Task 01 模板的 OpenAI-compatible 配置：AGENTSEEK_MODEL_PROVIDER=openai")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(f"请在 {PROJECT_ROOT / '.env'} 配置 OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE") or None
    extra_body = {}
    if base_url and urlsplit(base_url).hostname == "api.deepseek.com":
        extra_body["thinking"] = {"type": "disabled"}
    return ChatOpenAI(
        model=os.getenv("AGENTSEEK_MODEL", "gpt-4.1-mini"),
        api_key=api_key,
        base_url=base_url,
        extra_body=extra_body,
        timeout=60,
        max_retries=0,
    )
