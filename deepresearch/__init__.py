"""
CLI-DeepResearch
~~~~~~~~~~~~~~~~

A multi-agent deep research system powered by LangGraph.

Supports multiple LLM backends (DeepSeek, OpenAI, Claude, Gemini) and
search tools (Tavily, arXiv, MCP) to produce structured research reports.

Basic usage::

    from deepresearch.workflow.graph import ResearchWorkflow
    from deepresearch.llm.factory import LLMFactory
    from deepresearch.agents import Coordinator, Planner, Researcher, Rapporteur

    llm = LLMFactory.create_llm(provider="deepseek", api_key="...", model="deepseek-chat")
    workflow = ResearchWorkflow(
        Coordinator(llm), Planner(llm), Researcher(llm), Rapporteur(llm)
    )
    result = workflow.run("What is the current state of quantum computing?")

:license: MIT
"""

from .__version__ import __version__, __title__, __description__

__all__ = ["__version__", "__title__", "__description__"]
