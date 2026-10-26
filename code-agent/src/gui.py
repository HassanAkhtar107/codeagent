"""
gui.py  –  Phase 5: Tkinter GUI for Code Agent
Features:
  - API key field (masked, with "Remember on this PC" checkbox)
  - Input file selectors (Architecture_Documentation.md, Architecture_View.md)
  - Output directory selector
  - Model name + budget config
  - "Generate Project" button + "Stop" button
  - Live log/progress panel (scrollable)
  - Live token/cost display
  - Dark-mode professional look
"""
from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

# Ensure src is importable when running as a .exe (PyInstaller)
_SRC_DIR = Path(__file__).parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from config import get_api_key, save_api_key, clear_api_key
from pipeline import create_pipeline
from llm_client import DEFAULT_MODEL
from cost_tracker import DEFAULT_HARD_BUDGET_USD


# ---------------------------------------------------------------------------
# Colour palette (dark-mode)
# ---------------------------------------------------------------------------
BG        = "#0f1117"
BG2       = "#1a1d27"
BG3       = "#252836"
ACCENT    = "#6c63ff"
ACCENT2   = "#a78bfa"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
ERROR     = "#ef4444"
FG        = "#e2e8f0"
FG_DIM    = "#94a3b8"
FONT_MONO = ("Consolas", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_H1   = ("Segoe UI", 18, "bold")
FONT_H2   = ("Segoe UI", 12, "bold")
FONT_BTN  = ("Segoe UI", 11, "bold")


class CodeAgentGUI(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Code Agent  –  AI Project Generator")
        self.configure(bg=BG)
        self.minsize(900, 680)
        self.geometry("1050x760")
        self._set_icon()

        # State
        self._stop_event = threading.Event()
        self._pipeline_thread: threading.Thread | None = None
        self._running = False

        # Path variables
        self._doc_var = tk.StringVar()
        self._view_var = tk.StringVar()
        self._out_var = tk.StringVar()
        self._key_var = tk.StringVar()
        self._remember_var = tk.BooleanVar(value=False)
        self._model_var = tk.StringVar(value=DEFAULT_MODEL)
        self._budget_var = tk.StringVar(value=str(DEFAULT_HARD_BUDGET_USD))
        self._show_key_var = tk.BooleanVar(value=False)

        # Pre-fill saved API key
        saved_key = get_api_key()
        if saved_key:
            self._key_var.set(saved_key)
            self._remember_var.set(True)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Header ────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG, pady=16)
        hdr.pack(fill=tk.X, padx=24)

        tk.Label(hdr, text="⚡ Code Agent", font=FONT_H1,
                 bg=BG, fg=ACCENT2).pack(side=tk.LEFT)
        tk.Label(hdr, text="  AI-powered desktop app generator",
                 font=FONT_UI, bg=BG, fg=FG_DIM).pack(side=tk.LEFT, pady=(6, 0))

        # ── Main content (left: config, right: log) ───────────────────
        content = tk.Frame(self, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 8))
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(content, bg=BG2, bd=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.configure(width=380)

        right = tk.Frame(content, bg=BG2, bd=0)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left_panel(left)
        self._build_right_panel(right)

        # ── Bottom status bar ─────────────────────────────────────────
        self._status_var = tk.StringVar(value="Ready")
        status_bar = tk.Frame(self, bg=BG3, pady=4)
        status_bar.pack(fill=tk.X, padx=0, pady=0)
        tk.Label(status_bar, textvariable=self._status_var,
                 font=("Consolas", 9), bg=BG3, fg=ACCENT2, anchor="w",
                 padx=12).pack(fill=tk.X)

    def _build_left_panel(self, parent: tk.Frame) -> None:
        """Build the configuration panel (left column)."""
        pad = {"padx": 16, "pady": 6}

        # Section: API Key
        self._section_label(parent, "🔑 DeepSeek API Key")
        key_frame = tk.Frame(parent, bg=BG2)
        key_frame.pack(fill=tk.X, **pad)

        self._key_entry = tk.Entry(
            key_frame, textvariable=self._key_var, show="•",
            font=FONT_MONO, bg=BG3, fg=FG, insertbackground=FG,
            relief=tk.FLAT, bd=4,
        )
        self._key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            key_frame, text="👁", font=("Segoe UI", 9),
            bg=BG3, fg=FG_DIM, relief=tk.FLAT, cursor="hand2",
            command=self._toggle_key_visibility,
        ).pack(side=tk.RIGHT, padx=(4, 0))

        tk.Checkbutton(
            parent, text="Remember on this PC",
            variable=self._remember_var,
            font=FONT_UI, bg=BG2, fg=FG_DIM,
            selectcolor=BG3, activebackground=BG2,
        ).pack(anchor="w", padx=16, pady=(0, 4))

        # Section: Input Files
        self._section_label(parent, "📄 Input Files")

        self._file_row(parent, "Architecture Documentation:", self._doc_var,
                       "md", self._browse_doc)
        self._file_row(parent, "Architecture View (PlantUML):", self._view_var,
                       "md", self._browse_view)

        # Section: Output
        self._section_label(parent, "📁 Output Directory")
        out_frame = tk.Frame(parent, bg=BG2)
        out_frame.pack(fill=tk.X, **pad)
        tk.Entry(out_frame, textvariable=self._out_var, font=FONT_MONO,
                 bg=BG3, fg=FG, insertbackground=FG,
                 relief=tk.FLAT, bd=4).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(out_frame, text="Browse…", font=FONT_UI,
                  bg=ACCENT, fg="white", relief=tk.FLAT, cursor="hand2",
                  command=self._browse_out, padx=6).pack(side=tk.RIGHT, padx=(4, 0))

        # Section: Advanced
        self._section_label(parent, "⚙️ Advanced Settings")

        adv = tk.Frame(parent, bg=BG2)
        adv.pack(fill=tk.X, padx=16, pady=4)

        tk.Label(adv, text="Model:", font=FONT_UI, bg=BG2, fg=FG_DIM,
                 width=10, anchor="w").grid(row=0, column=0, sticky="w", pady=3)
        tk.Entry(adv, textvariable=self._model_var, font=FONT_MONO,
                 bg=BG3, fg=FG, insertbackground=FG,
                 relief=tk.FLAT, bd=4, width=20).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        tk.Label(adv, text="Budget ($):", font=FONT_UI, bg=BG2, fg=FG_DIM,
                 width=10, anchor="w").grid(row=1, column=0, sticky="w", pady=3)
        tk.Entry(adv, textvariable=self._budget_var, font=FONT_MONO,
                 bg=BG3, fg=FG, insertbackground=FG,
                 relief=tk.FLAT, bd=4, width=10).grid(row=1, column=1, sticky="w", padx=(4, 0))
        adv.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = tk.Frame(parent, bg=BG2)
        btn_frame.pack(fill=tk.X, padx=16, pady=16)

        self._gen_btn = tk.Button(
            btn_frame, text="▶  Generate Project",
            font=FONT_BTN, bg=ACCENT, fg="white",
            relief=tk.FLAT, cursor="hand2",
            pady=10, command=self._start_generation,
        )
        self._gen_btn.pack(fill=tk.X, pady=(0, 8))

        self._stop_btn = tk.Button(
            btn_frame, text="⏹  Stop",
            font=FONT_BTN, bg=ERROR, fg="white",
            relief=tk.FLAT, cursor="hand2",
            pady=8, state=tk.DISABLED, command=self._stop_generation,
        )
        self._stop_btn.pack(fill=tk.X)

        # Cost display
        self._cost_var = tk.StringVar(value="Tokens: –  |  Cost: $–")
        tk.Label(parent, textvariable=self._cost_var,
                 font=("Consolas", 9), bg=BG2, fg=ACCENT2,
                 wraplength=340, justify="left", padx=16).pack(anchor="w", pady=(4, 0))

    def _build_right_panel(self, parent: tk.Frame) -> None:
        """Build the live log panel (right column)."""
        tk.Label(parent, text="📋 Live Log", font=FONT_H2,
                 bg=BG2, fg=FG, anchor="w").pack(fill=tk.X, padx=14, pady=(12, 4))

        self._log_text = scrolledtext.ScrolledText(
            parent, font=FONT_MONO, bg="#0a0c14", fg=FG,
            insertbackground=FG, relief=tk.FLAT,
            wrap=tk.WORD, state=tk.DISABLED,
            selectbackground=ACCENT,
        )
        self._log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Configure tags for coloured output
        self._log_text.tag_configure("info",    foreground=FG)
        self._log_text.tag_configure("success", foreground=SUCCESS)
        self._log_text.tag_configure("warning", foreground=WARNING)
        self._log_text.tag_configure("error",   foreground=ERROR)
        self._log_text.tag_configure("accent",  foreground=ACCENT2)
        self._log_text.tag_configure("dim",     foreground=FG_DIM)

        clr_btn = tk.Button(parent, text="Clear Log", font=FONT_UI,
                            bg=BG3, fg=FG_DIM, relief=tk.FLAT,
                            cursor="hand2", command=self._clear_log)
        clr_btn.pack(anchor="e", padx=8, pady=(0, 8))

    # ------------------------------------------------------------------
    # Helper widgets
    # ------------------------------------------------------------------

    def _section_label(self, parent: tk.Frame, text: str) -> None:
        tk.Label(parent, text=text, font=FONT_H2,
                 bg=BG2, fg=ACCENT2, anchor="w",
                 padx=16, pady=(14, 0)).pack(fill=tk.X)
        tk.Frame(parent, bg=BG3, height=1).pack(fill=tk.X, padx=16, pady=2)

    def _file_row(self, parent, label: str, var: tk.StringVar,
                  ext: str, command) -> None:
        tk.Label(parent, text=label, font=FONT_UI,
                 bg=BG2, fg=FG_DIM, anchor="w",
                 padx=16).pack(fill=tk.X)
        row = tk.Frame(parent, bg=BG2)
        row.pack(fill=tk.X, padx=16, pady=(2, 8))
        tk.Entry(row, textvariable=var, font=FONT_MONO,
                 bg=BG3, fg=FG, insertbackground=FG,
                 relief=tk.FLAT, bd=4).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row, text="Browse…", font=FONT_UI,
                  bg=ACCENT, fg="white", relief=tk.FLAT,
                  cursor="hand2", command=command, padx=6).pack(side=tk.RIGHT, padx=(4, 0))

    # ------------------------------------------------------------------
    # Browse callbacks
    # ------------------------------------------------------------------

    def _browse_doc(self) -> None:
        p = filedialog.askopenfilename(
            title="Select Architecture_Documentation.md",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")]
        )
        if p:
            self._doc_var.set(p)

    def _browse_view(self) -> None:
        p = filedialog.askopenfilename(
            title="Select Architecture_View.md",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")]
        )
        if p:
            self._view_var.set(p)

    def _browse_out(self) -> None:
        p = filedialog.askdirectory(title="Select Output Directory")
        if p:
            self._out_var.set(p)

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def _log(self, msg: str) -> None:
        """Thread-safe log append."""
        self.after(0, self._append_log, msg)

    def _append_log(self, msg: str) -> None:
        self._log_text.configure(state=tk.NORMAL)
        tag = self._pick_tag(msg)
        self._log_text.insert(tk.END, msg + "\n", tag)
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _pick_tag(self, msg: str) -> str:
        low = msg.lower()
        if "✓" in msg or "passed" in low or "success" in low:
            return "success"
        if "✗" in msg or "error" in low or "failed" in low or "fatal" in low:
            return "error"
        if "warning" in low or "budget" in low or "repair" in low:
            return "warning"
        if msg.startswith("==") or msg.startswith("--"):
            return "accent"
        if msg.startswith("[") and "dim" not in msg:
            return "info"
        return "dim"

    def _clear_log(self) -> None:
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.delete("1.0", tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _update_cost(self, status: str) -> None:
        self.after(0, self._cost_var.set, status)

    def _set_status(self, msg: str) -> None:
        self.after(0, self._status_var.set, msg)

    # ------------------------------------------------------------------
    # Key visibility toggle
    # ------------------------------------------------------------------

    def _toggle_key_visibility(self) -> None:
        if self._key_entry.cget("show") == "•":
            self._key_entry.configure(show="")
        else:
            self._key_entry.configure(show="•")

    # ------------------------------------------------------------------
    # Generation control
    # ------------------------------------------------------------------

    def _validate_inputs(self) -> bool:
        if not self._key_var.get().strip():
            messagebox.showerror("Missing API Key", "Please enter your DeepSeek API key.")
            return False
        if not self._doc_var.get().strip() or not Path(self._doc_var.get()).exists():
            messagebox.showerror("Missing File", "Please select a valid Architecture_Documentation.md file.")
            return False
        if not self._view_var.get().strip() or not Path(self._view_var.get()).exists():
            messagebox.showerror("Missing File", "Please select a valid Architecture_View.md file.")
            return False
        if not self._out_var.get().strip():
            messagebox.showerror("Missing Directory", "Please select an output directory.")
            return False
        try:
            budget = float(self._budget_var.get())
            if budget <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Budget", "Budget must be a positive number (e.g. 0.80).")
            return False
        return True

    def _start_generation(self) -> None:
        if self._running:
            return
        if not self._validate_inputs():
            return

        # Save API key if requested
        if self._remember_var.get():
            save_api_key(self._key_var.get().strip())
        else:
            clear_api_key()

        self._stop_event.clear()
        self._running = True
        self._gen_btn.configure(state=tk.DISABLED)
        self._stop_btn.configure(state=tk.NORMAL)
        self._clear_log()
        self._set_status("Running …")

        # Determine cache dir (sibling llm_cache/ of output)
        out_path = Path(self._out_var.get())
        cache_dir = out_path.parent / "llm_cache"

        pipeline = create_pipeline(
            api_key=self._key_var.get().strip(),
            model=self._model_var.get().strip() or DEFAULT_MODEL,
            doc_path=self._doc_var.get().strip(),
            view_path=self._view_var.get().strip(),
            output_dir=out_path,
            cache_dir=cache_dir,
            hard_budget_usd=float(self._budget_var.get()),
            log_callback=self._log,
            cost_callback=self._update_cost,
            stop_event=self._stop_event,
        )

        self._pipeline_thread = threading.Thread(
            target=self._run_pipeline,
            args=(pipeline,),
            daemon=True,
        )
        self._pipeline_thread.start()

    def _run_pipeline(self, pipeline) -> None:
        try:
            result = pipeline.run()
            if result.get("success"):
                self._set_status("✅  Generation complete!")
                self.after(0, messagebox.showinfo, "Done",
                           f"Project generated successfully!\n\n"
                           f"Output: {pipeline.output_dir}\n\n"
                           f"See GENERATION_REPORT.md for details.")
            else:
                err = result.get("error", "Unknown error")
                self._set_status(f"❌  Failed: {err[:80]}")
                self.after(0, messagebox.showerror, "Generation Failed", err)
        except Exception as e:
            self._log(f"[GUI] Unexpected error: {e}")
            self._set_status(f"❌  Error: {str(e)[:80]}")
        finally:
            self.after(0, self._on_pipeline_done)

    def _on_pipeline_done(self) -> None:
        self._running = False
        self._gen_btn.configure(state=tk.NORMAL)
        self._stop_btn.configure(state=tk.DISABLED)

    def _stop_generation(self) -> None:
        if self._running:
            self._stop_event.set()
            self._log("[GUI] Stop requested – finishing current file …")
            self._set_status("Stopping …")
            self._stop_btn.configure(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _set_icon(self) -> None:
        """Set window icon if available (no-op if not found)."""
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass

    def _on_close(self) -> None:
        if self._running:
            if not messagebox.askyesno(
                "Quit?",
                "Generation is running. Stop it and quit?",
            ):
                return
            self._stop_event.set()
        self.destroy()


def launch() -> None:
    app = CodeAgentGUI()
    app.mainloop()


if __name__ == "__main__":
    launch()
