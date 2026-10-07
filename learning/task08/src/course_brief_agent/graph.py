"""Graph entry point for langgraph.json, analogous to Task 01's graph export."""

from course_brief_agent.agent import build_agent
from course_brief_agent.model import build_model

graph = build_agent(build_model())
