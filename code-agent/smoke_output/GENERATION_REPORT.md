# Generation Report – SpaceFractions

Generated at: 2026-10-27 00:57:38

---

## Status
- Early stop: No (completed normally)
- Files planned  : 10
- Files generated: 10
- Files missing  : 0

## Files Generated

- ✅ `main.py`
- ✅ `src/__init__.py`
- ✅ `src/models.py`
- ✅ `src/game.py`
- ✅ `src/ui.py`
- ✅ `src/question_bank.py`
- ✅ `data/questions.json`
- ✅ `tests/test_game.py`
- ✅ `requirements.txt`
- ✅ `README.md`

## Syntax Validation
- Passed : 7
- Failed : 0

## Test Results
- Status: ❌ Failed / Skipped

```
============================= test session starts =============================
collecting ... collected 0 items

============================ no tests ran in 0.01s ============================

```

## Token Usage & Cost
- Model              : deepseek-chat
- Total prompt tokens: 1,100
- Total output tokens: 2,200
- Total tokens       : 3,300
- Estimated cost     : $0.0027 USD
- Hard budget        : $1.00 USD

### Per-Step Breakdown

| Step | Tokens | Cost (USD) |
|------|--------|------------|
| planner:attempt1 | 300 | $0.0002 |
| generator:main.py | 300 | $0.0002 |
| generator:src/__init__.py | 300 | $0.0002 |
| generator:src/models.py | 300 | $0.0002 |
| generator:src/game.py | 300 | $0.0002 |
| generator:src/ui.py | 300 | $0.0002 |
| generator:src/question_bank.py | 300 | $0.0002 |
| generator:data/questions.json | 300 | $0.0002 |
| generator:tests/test_game.py | 300 | $0.0002 |
| generator:requirements.txt | 300 | $0.0002 |
| generator:README.md | 300 | $0.0002 |

---

## Assumptions and Deviations

The following assumptions were made during generation:

1. The target application is a Python Tkinter desktop application.
2. Web/server technology references (REST, Node.js, microservices, Kubernetes) were adapted to desktop-equivalent Python modules.
3. Database references were adapted to a local SQLite or JSON file.
4. Missing or empty sections in the architecture documents were handled gracefully.
5. Contradictions between the architecture documents (e.g., microservices vs desktop game) were resolved in favour of the desktop design.

_See the generated README.md for setup and run instructions._
