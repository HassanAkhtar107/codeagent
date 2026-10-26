# DESIGN.md – Code Agent Architecture & Design Notes

## 1. Overview

Code Agent is a Windows desktop application that reads architecture documentation and PlantUML diagrams, then uses an LLM (DeepSeek) to automatically generate a complete, runnable desktop application. It is inspired by Claude Code's agent loop architecture.

---

## 2. Research Summary (Reference Repos)

### 2.1 how-claude-code-works (Windy3f3f3f3f)
Key ideas borrowed:
- **Agent loop pattern**: Read context → Plan (think) → Act (tool call) → Observe → Repeat
- **Context engineering**: Send only the relevant slice of context per call, never the full document every time. We implement this as "focused prompts" with JSON slices.
- **Tool layer abstraction**: `write_file`, `read_file`, `list_dir`, `run_command` are explicit tools with sandboxing.
- **System prompt discipline**: Separate system prompts per role (planner, generator, repair agent).
- **Retry with error feedback**: On tool/LLM failure, re-send the error + failing content for a self-repair attempt.

### 2.2 claw-code (ultraworkers)
Key ideas borrowed:
- **Agent-managed artefacts**: The agent writes files to an output directory, not to a shared mutable state.
- **Minimal human intervention**: The pipeline runs autonomously end-to-end.
- **Structured output validation**: Plan JSON is validated before proceeding to generation.

### 2.3 anthropics/claude-code
Key ideas borrowed:
- **Phase separation**: Planning and generation are clearly separate phases. The plan is a stable JSON document used throughout generation.
- **Interface-only context**: When generating file B that depends on file A, only A's class/function signatures are sent (not A's full content). This keeps token usage low.
- **Sandboxed execution**: Commands run only inside the output directory with a strict timeout.

---

## 3. Architecture

```
main.py
  └─ src/
       ├─ gui.py              # Tkinter GUI (Phase 5)
       ├─ pipeline.py         # Orchestrator connecting all phases
       ├─ llm_client.py       # DeepSeek API client + MockLLMClient
       ├─ cost_tracker.py     # Token counting, cost estimation, budget guard
       ├─ reporter.py         # GENERATION_REPORT.md writer
       ├─ config.py           # API key persistence (~/.code_agent_config.json)
       └─ agent/
            ├─ parser/
            │    ├─ doc_parser.py    # Phase 1: Parses Architecture_Documentation.md
            │    └─ view_parser.py   # Phase 1: Parses Architecture_View.md (PlantUML)
            ├─ planner/
            │    └─ planner.py       # Phase 2: LLM → JSON project plan
            ├─ generator/
            │    └─ generator.py     # Phase 3: File-by-file generation agent loop
            ├─ tools/
            │    ├─ file_tools.py    # write_file, read_file, list_dir (sandboxed)
            │    └─ run_tool.py      # run_command (sandboxed subprocess)
            └─ validator/
                 └─ validator.py     # Phase 4: py_compile + pytest + LLM repair
```

---

## 4. Agent Loop (Generator Phase)

```
for each file in plan:
  1. Build focused prompt:
     - Project summary (≤400 chars)
     - Relevant component JSON slices
     - Interfaces of already-generated dependencies (signatures only)
  2. Call LLM → file content
  3. Strip markdown fences
  4. Write to disk (sandboxed)
  5. Extract interface summary of new file
  6. Check budget; stop if exceeded
```

---

## 5. Cost Control Strategy

| Technique | Detail |
|-----------|--------|
| Focused prompts | Only JSON slices, not raw markdown |
| Interface-only context | Dependency summaries, not full file content |
| Short system prompts | Fixed, concise, role-specific |
| Low temperature | 0.2 for code generation (deterministic) |
| Disk cache | SHA-256 keyed by prompt; repeated runs are free |
| Per-call max_tokens | Capped at 3000 for file generation, 2048 for planning |
| Hard budget guard | Default $0.80; stops gracefully at limit |
| Live cost display | GUI shows running token count and USD cost |

Estimated cost for a full Space Fractions run (~10 files):
- Planning: ~$0.01
- Generation (10 files × ~1500 tokens avg): ~$0.15–$0.25
- Validation + repair: ~$0.05–$0.10
- **Total: ~$0.25–$0.40** (well under $1.00)

---

## 6. Desktop-First Enforcement

The planner explicitly strips web-technology files and ensures:
- `main.py` as entry point (Tkinter)
- No `server.js`, `wsgi.py`, `manage.py`, `package.json`
- Local file (JSON/SQLite) instead of server database
- Python modules/classes instead of microservices

---

## 7. Robustness

- **Missing sections**: Parsed as empty lists/strings; the LLM is told to make reasonable assumptions.
- **Contradictions**: If architecture mentions microservices + desktop game, the agent notes this in README "Assumptions and Deviations".
- **API errors**: Exponential backoff (2s, 4s, 8s), max 3 retries.
- **Stop button**: Uses `threading.Event` checked between each file.
- **Background thread**: GUI never blocks; all pipeline work is in a daemon thread.

---

## 8. PyInstaller Packaging

```
pyinstaller --onefile --windowed --name CodeAgent main.py
```

All stdlib modules (tkinter, json, re, threading, subprocess, pathlib) are included by default. Only external dependency is `openai`.
