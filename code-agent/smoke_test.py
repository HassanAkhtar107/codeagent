"""
smoke_test.py  –  Phase 7 dry-run: full pipeline with MockLLMClient
Run from code-agent/ directory:
    python smoke_test.py

Verifies that the full pipeline runs end-to-end, all expected files are
generated, the GENERATION_REPORT.md is written, and no errors occur.
No API key required (uses MockLLMClient).
"""
import sys
import io
import shutil
import threading
from pathlib import Path

# Force UTF-8 output on Windows (avoids cp1252 encode errors)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup paths
HERE = Path(__file__).parent
SRC = HERE / "src"
sys.path.insert(0, str(SRC))

from pipeline import create_pipeline
from llm_client import MockLLMClient

SAMPLES = HERE / "samples"
OUTPUT_DIR = HERE / "smoke_output"

# ------------------------------------------------------------------
# Clean previous output
# ------------------------------------------------------------------
if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
OUTPUT_DIR.mkdir()

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------
logs = []
def log(msg):
    print(msg)
    logs.append(msg)

cost_statuses = []
def cost_cb(status):
    cost_statuses.append(status)

stop = threading.Event()

# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------
print("=" * 60)
print("Code Agent – Phase 7 Smoke Test (MockLLMClient)")
print("=" * 60)

pipeline = create_pipeline(
    api_key="mock-key-not-real",
    model="deepseek-chat",
    doc_path=SAMPLES / "Architecture_Documentation.md",
    view_path=SAMPLES / "Architecture_View.md",
    output_dir=OUTPUT_DIR,
    cache_dir=None,
    hard_budget_usd=1.0,
    log_callback=log,
    cost_callback=cost_cb,
    stop_event=stop,
    llm_client=MockLLMClient(log_callback=log),
)

result = pipeline.run()

# ------------------------------------------------------------------
# Assertions
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("SMOKE TEST RESULTS")
print("=" * 60)

errors = []

# 1. Pipeline returned success
if not result.get("success"):
    errors.append(f"Pipeline reported failure: {result.get('error')}")
else:
    print("✅ Pipeline completed successfully")

# 2. Output directory is non-empty
generated = list(OUTPUT_DIR.rglob("*"))
generated_files = [f for f in generated if f.is_file()]
if not generated_files:
    errors.append("No files were generated in output directory")
else:
    print(f"✅ {len(generated_files)} files generated:")
    for f in sorted(generated_files):
        print(f"   {f.relative_to(OUTPUT_DIR)}")

# 3. GENERATION_REPORT.md exists
report_path = OUTPUT_DIR / "GENERATION_REPORT.md"
if not report_path.exists():
    errors.append("GENERATION_REPORT.md was not created")
else:
    print(f"✅ GENERATION_REPORT.md written ({report_path.stat().st_size} bytes)")
    # Print first 20 lines
    lines = report_path.read_text(encoding="utf-8").splitlines()
    print("\n--- Report Preview ---")
    for line in lines[:25]:
        print(f"  {line}")
    print("  ...")

# 4. Cost tracker accumulated something
if pipeline.cost_tracker.total_tokens == 0:
    errors.append("Cost tracker shows zero tokens (pipeline may not have called LLM)")
else:
    print(f"\n✅ Tokens used: {pipeline.cost_tracker.total_tokens:,}")
    print(f"✅ Estimated cost: ${pipeline.cost_tracker.total_cost_usd:.4f} (mock)")

# 5. main.py was generated
main_py = OUTPUT_DIR / "main.py"
if not main_py.exists():
    errors.append("main.py was not generated")
else:
    print(f"✅ main.py generated ({main_py.stat().st_size} bytes)")

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
print("\n" + "=" * 60)
if errors:
    print(f"❌ SMOKE TEST FAILED – {len(errors)} error(s):")
    for e in errors:
        print(f"   • {e}")
    sys.exit(1)
else:
    print("✅ ALL SMOKE TEST CHECKS PASSED")
    print(f"   Output directory: {OUTPUT_DIR}")
print("=" * 60)
