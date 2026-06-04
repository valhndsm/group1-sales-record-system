"""
=========================================================
utils.py
=========================================================
Utility helpers: PyInstaller resource path resolver and
reusable styled Tkinter widget factories.
=========================================================
"""

import os
import sys
import tkinter as tk
from .constants import (
    FONT_INPUT, FONT_BTN,
    CARD, TEXT, ACCENT, BORDER, BG,
)


# ── Resource Path ─────────────────────────────────────

def resource_path(relative: str) -> str:
    """
    Resolve a file path that works both in development
    and inside a PyInstaller-bundled executable.
    Resolves relative to the project root (where main.py lives),
    not the current working directory.
    """
    try:
        base = sys._MEIPASS          # type: ignore[attr-defined]
    except AttributeError:
        # Walk up from core/utils.py -> core/ -> project root
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


# ── Styled Widget Factories ───────────────────────────

def styled_entry(parent: tk.Widget, width: int = 22) -> tk.Entry:
    """Return a dark-themed text entry widget."""
    return tk.Entry(
        parent,
        font=FONT_INPUT,
        bg=CARD, fg=TEXT,
        insertbackground=ACCENT,
        relief="flat",
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        width=width,
    )


def styled_btn(
    parent: tk.Widget,
    text: str,
    command,
    color: str = ACCENT,
    fg: str = BG,
    width: int = 14,
) -> tk.Button:
    """Return a flat styled button with hover colour swap."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=FONT_BTN,
        bg=color, fg=fg,
        activebackground=TEXT,
        activeforeground=BG,
        relief="flat", bd=0,
        padx=12, pady=6,
        cursor="hand2",
        width=width,
    )
    btn.bind("<Enter>", lambda _: btn.config(bg=TEXT))
    btn.bind("<Leave>", lambda _: btn.config(bg=color))
    return btn
