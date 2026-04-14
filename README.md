# CLI-DeepResearch

> A multi-agent deep research system powered by [LangGraph](https://github.com/langchain-ai/langgraph).
> 基于 LangGraph 的多智能体深度研究系统。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

CLI-DeepResearch automates the research lifecycle through a coordinated pipeline of four specialized agents:

```
User Query
    │
    ▼
┌─────────────┐     ┌──────────┐     ┌───────────────┐
│ Coordinator │────▶│ Planner  │────▶│ Human Review  │
│             │     │          │     │  (interrupt)  │
└─────────────┘     └──────────┘     └───────┬───────┘
                                             │ approved
                                             ▼
                                     ┌──────────────┐
                                     │  Researcher  │◀─┐
                                     │              │  │ loop
                                     └──────┬───────┘  │
                                            │           │
                                   need more research ──┘
                                            │ sufficient
                                            ▼
                                     ┌──────────────┐
                                     │  Rapporteur  │
                                     │   (report)   │
                                     └──────────────┘
```

**Agents:**

| Agent | Role |
|---|---|
| `Coordinator` | Classifies queries; routes simple responses or initialises research state |
| `Planner` | Decomposes the topic into subtasks; regenerates based on user feedback |
| `Researcher` | Executes subtasks against Tavily (web), arXiv (papers), or MCP endpoints |
| `Rapporteur` | Synthesises findings into a structured Markdown or HTML report |

**Human-in-the-loop** — the workflow pauses after planning so you can approve, modify, or cancel the plan before any searches begin.

---

## Quickstart

### 1. Install

```bash
git clone https://github.com/your-org/CLI-DeepresearchAgent.git
cd CLI-DeepresearchAgent

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e .
# or: pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` and fill in at least one LLM API key and your Tavily key:

```dotenv
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-...

TAVILY_API_KEY=tvly-...
```

### 3. Run

**Interactive mode** (menu-driven):
```bash
deepresearch
# or: python main.py
```

**Single query** (non-interactive):
```bash
deepresearch "What are the latest breakthroughs in fusion energy research?"
```

**With options:**
```bash
deepresearch "Quantum computing landscape 2025" \
  --provider openai \
  --model gpt-4o \
  --max-iterations 8 \
  --auto-approve \
  --output-format html \
  --output-dir ./reports
```

---

## CLI Reference

```
usage: deepresearch [QUERY] [OPTIONS]

positional arguments:
  QUERY                 Research topic (omit to enter interactive mode)

options:
  --provider            LLM backend: deepseek | openai | claude | gemini  (default: deepseek)
  --model               Model name (default: provider's recommended model)
  --max-iterations N    Max research subtask loops  (default: 5)
  --auto-approve        Skip the human plan-review step
  --output-dir PATH     Directory for saved reports  (default: ./outputs)
  --output-format FMT   markdown | html  (default: markdown)
  --show-steps          Print node-level debug info
  --interactive         Force interactive menu even when QUERY is supplied
  --version             Print version and exit
  -h, --help            Show this message
```

---

## Supported LLM Providers

| Provider | `--provider` value | Required env var |
|---|---|---|
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` |
| OpenAI | `openai` | `OPENAI_API_KEY` |
| Anthropic Claude | `claude` | `ANTHROPIC_API_KEY` |
| Google Gemini | `gemini` | `GOOGLE_API_KEY` |

---

## Supported Search Tools

| Tool | Scope | Config |
|---|---|---|
| [Tavily](https://tavily.com/) | Live web search | `TAVILY_API_KEY` |
| [arXiv](https://arxiv.org/) | Academic papers | no key needed |
| MCP endpoint | Custom / enterprise data | `MCP_SERVER_URL`, `MCP_API_KEY` |

---

## Project Structure

```
CLI-DeepresearchAgent/
├── main.py                  # Entry point (delegates to deepresearch.cli.main)
├── pyproject.toml           # Packaging & console_scripts entry point
├── requirements.txt         # Pinned dependencies
├── .env.example             # Environment variable template
└── deepresearch/            # Main package
    ├── __version__.py       # Single source of truth for version
    ├── agents/
    │   ├── base.py          # BaseAgent ABC (run / _generate / _load_prompt)
    │   ├── coordinator.py
    │   ├── planner.py
    │   ├── researcher.py
    │   └── rapporteur.py
    ├── cli/
    │   └── main.py          # argparse CLI + interactive menu
    ├── llm/
    │   ├── base.py          # BaseLLM ABC
    │   ├── factory.py       # LLMFactory with lazy provider loading
    │   ├── deepseek_llm.py
    │   ├── openai_llm.py
    │   ├── claude_llm.py
    │   └── gemini_llm.py
    ├── tools/
    │   ├── tavily_search.py
    │   ├── arxiv_search.py
    │   └── mcp_client.py
    ├── workflow/
    │   ├── state.py         # TypedDict workflow state
    │   ├── graph.py         # LangGraph graph + ResearchWorkflow class
    │   └── nodes.py         # Node functions (coordinator/planner/... -> state)
    ├── prompts/
    │   └── loader.py        # Jinja2 prompt template loader
    └── utils/
        ├── config.py        # Pydantic config + env loader
        └── logger.py
```

---

## Configuration Precedence

```
CLI flags  >  config.json (persisted via interactive menu)  >  .env  >  defaults
```

The interactive menu's **"Configure Settings"** option writes a `config.json` in the project root that is automatically loaded on the next run.

---

## Programmatic API

```python
from dotenv import load_dotenv
from deepresearch.llm.factory import LLMFactory
from deepresearch.agents import Coordinator, Planner, Researcher, Rapporteur
from deepresearch.workflow.graph import ResearchWorkflow

load_dotenv()

llm = LLMFactory.create_llm(provider="deepseek", api_key="sk-...", model="deepseek-chat")
workflow = ResearchWorkflow(
    coordinator=Coordinator(llm),
    planner=Planner(llm),
    researcher=Researcher(llm, tavily_api_key="tvly-..."),
    rapporteur=Rapporteur(llm),
)

result = workflow.run(
    query="What is the current state of quantum computing?",
    auto_approve=True,
    output_format="markdown",
)
print(result["final_report"])
```

For streaming output use `workflow.stream(...)` or `workflow.stream_interactive(...)`.

---

## Extending

### Add a custom LLM provider

```python
from deepresearch.llm.base import BaseLLM
from deepresearch.llm.factory import LLMFactory

class MyLLM(BaseLLM):
    def generate(self, prompt, **kwargs): ...
    def stream_generate(self, prompt, **kwargs): ...

LLMFactory.register_provider("myllm", MyLLM)
```

### Add a custom agent

Subclass `BaseAgent` and implement `run()`:

```python
from deepresearch.agents.base import BaseAgent

class FactChecker(BaseAgent):
    def run(self, state, **kwargs):
        # validate state["search_results"] ...
        return state
```

---

## License

MIT - see [LICENSE](LICENSE) for details.
