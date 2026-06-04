"""
=========================================================
constants.py
=========================================================
Application-wide constants: color palette, font
definitions, file paths, and Matplotlib theme settings.
=========================================================
"""

import os
import matplotlib.pyplot as plt
from pathlib import Path

# ── Color Palette ─────────────────────────────────────
BG          = "#0f1117"
SURFACE     = "#1a1d27"
CARD        = "#22263a"
ACCENT      = "#f0c040"
ACCENT2     = "#e05c5c"
ACCENT3     = "#58CCED"
TEXT        = "#e8eaf0"
TEXT_MUTED  = "#7a7f9a"
BORDER      = "#2e3349"
SUCCESS     = "#4ecca3"
ROW_ALT     = "#1e2235"
WHITE       = "#ffffff"

CHART_PALETTE = [ACCENT, ACCENT3, ACCENT2, SUCCESS,
                 "#a78bfa", "#fb923c", "#34d399", "#60a5fa"]

# ── Font Definitions ──────────────────────────────────
FONT_SALES  = ("Segoe UI",    11)
FONT_TITLE  = ("Bahnschrift", 22, "bold")
FONT_LABEL  = ("Bahnschrift",  9, "bold")
FONT_INPUT  = ("Bahnschrift", 10)
FONT_BTN    = ("Bahnschrift", 10, "bold")
FONT_TABLE  = ("Bahnschrift", 10)
FONT_STAT   = ("Bahnschrift", 24, "bold")

# ── Storage Path ──────────────────────────────────────
APP_DIR   = Path(os.getenv("APPDATA", os.path.expanduser("~"))) / "SalesLedger"
APP_DIR.mkdir(exist_ok=True)
DATA_FILE = APP_DIR / "sales_data.json"

# ── Matplotlib Dark Theme ─────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    SURFACE,
    "axes.edgecolor":    BORDER,
    "axes.labelcolor":   TEXT_MUTED,
    "axes.titlecolor":   TEXT,
    "axes.titlesize":    10,
    "axes.titleweight":  "bold",
    "axes.titlepad":     10,
    "xtick.color":       TEXT_MUTED,
    "ytick.color":       TEXT_MUTED,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
    "grid.color":        BORDER,
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "legend.facecolor":  CARD,
    "legend.edgecolor":  BORDER,
    "legend.labelcolor": TEXT,
    "legend.fontsize":   8,
    "text.color":        TEXT,
    "font.family":       "sans-serif",
})
