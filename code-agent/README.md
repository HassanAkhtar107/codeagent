# Code Agent

> **AI-powered desktop application generator** — reads your architecture documents and automatically generates a complete, runnable Python desktop application.

---

## What It Does

Code Agent is a Windows desktop application (Python + Tkinter) that:

1. **Reads** two architecture input files:
   - `Architecture_Documentation.md` — written architecture (components, requirements, tech stack, API specs, DB schema, testing, etc.)
   - `Architecture_View.md` — PlantUML diagrams (use case, class, state, sequence, activity, etc.)

2. **Generates** a complete project via the DeepSeek LLM API:
   - Full source code (Python + Tkinter)
   - `requirements.txt`
   - `README.md` (with "Assumptions and Deviations")
   - `tests/` (pytest)
   - `GENERATION_REPORT.md` (files, cost, test results)

3. **Validates** all generated Python files with `py_compile` and `pytest`, auto-repairing errors via LLM (max 2 repair attempts per file).

---

## Prerequisites

- **Windows 10/11** (for the .exe) or Python 3.10+ (to run from source)
- **DeepSeek API Key** — get one free at [platform.deepseek.com](https://platform.deepseek.com)

---

## Installation & Run (From Source)

```bash
# 1. Clone the repo
git clone https://github.com/HassanAkhtar107/codeagent.git
cd codeagent/code-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the GUI
python main.py
```

---

## Build the .exe (Windows)

```batch
cd code-agent
build_exe.bat
# Output: dist/CodeAgent.exe (double-click, no Python required)
```

---

## Usage

1. **Enter your DeepSeek API Key** (optionally check "Remember on this PC")
2. **Select** `Architecture_Documentation.md`
3. **Select** `Architecture_View.md`
4. **Choose** an empty output directory
5. **Click "Generate Project"** and watch the live log
6. When done, open the output directory — your project is ready to run!

---

## Running Tests (Code Agent's Own Tests)

```bash
cd code-agent
pytest tests/ -v
```

All tests use a `MockLLMClient` — **no API spend** during testing.

---

## Repository Structure

```
code-agent/
├── main.py                  # Entry point
├── src/
│   ├── gui.py               # Tkinter GUI
│   ├── pipeline.py          # Orchestrator
│   ├── llm_client.py        # DeepSeek API client + Mock
│   ├── cost_tracker.py      # Token/cost tracking
│   ├── reporter.py          # GENERATION_REPORT.md
│   ├── config.py            # API key persistence
│   └── agent/
│       ├── parser/          # Markdown + PlantUML parsers
│       ├── planner/         # LLM project planner
│       ├── generator/       # File-by-file generator
│       ├── tools/           # file_tools, run_tool (sandboxed)
│       └── validator/       # py_compile + pytest + repair
├── tests/                   # Unit + integration tests
├── samples/                 # Sample Space Fractions input files
├── docs/DESIGN.md           # Architecture & design notes
├── requirements.txt
└── build_exe.bat            # PyInstaller build script
```

---

## Cost Notes

| Phase | Estimated Cost |
|-------|---------------|
| Planning (1 call) | ~$0.01 |
| Generation (10 files) | ~$0.15–$0.25 |
| Validation + repair | ~$0.05–$0.10 |
| **Total** | **~$0.25–$0.40** |

- Hard budget default: **$0.80** (configurable in the GUI)
- All prompts use **temperature 0.2** for deterministic code output
- Disk **response cache** — repeated runs on the same inputs are free
- DeepSeek pricing: **$0.27/1M input tokens**, **$1.10/1M output tokens** (deepseek-chat)

---

## Limitations

- The generated application is always a **Python Tkinter desktop app**, even if the architecture docs describe a web app.
- Web-technology file paths (`server.js`, `wsgi.py`, `manage.py`) are automatically removed and replaced with desktop equivalents.
- Test generation quality depends on LLM output; the validator repairs common syntax errors but cannot guarantee all tests pass.
- The validator runs `pytest` inside the generated project — tests that require external services will be skipped.

---

## Security

- **API keys are never stored in code or the repo.**
- The key is saved (optionally) to `~/.code_agent_config.json` on the local machine only.
- All generated files are sandboxed to the chosen output directory.
- `run_command` has a 60-second timeout and runs only inside the output directory.

---

## License

MIT
