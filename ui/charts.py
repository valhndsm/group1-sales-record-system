"""
=========================================================
charts.py
=========================================================
ChartsPanel — a self-contained Tkinter frame that embeds
a Matplotlib figure with three switchable chart views:
  • Revenue Over Time  (bar + line)
  • By Category        (pie)
  • Top Products       (horizontal bar)
=========================================================
"""

import tkinter as tk
from tkinter import ttk
from collections import defaultdict
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.constants import (
    BG, SURFACE, CARD, TEXT, TEXT_MUTED, ACCENT, ACCENT2, ACCENT3,
    SUCCESS, CHART_PALETTE, FONT_LABEL,
)


class ChartsPanel(tk.Frame):
    """
    Embeddable frame that renders sales analytics charts.

    Usage
    -----
    panel = ChartsPanel(parent, records)
    panel.grid(...)
    panel.refresh(new_records)   # call whenever records change
    """

    _MODES = [
        ("revenue",  "Revenue Over Time"),
        ("category", "By Category"),
        ("top",      "Top Products"),
    ]

    _ADJUST = {
        "revenue":  dict(left=0.14, right=0.97, top=0.88, bottom=0.28),
        "category": dict(left=0.05, right=0.95, top=0.88, bottom=0.05),
        "top":      dict(left=0.28, right=0.88, top=0.88, bottom=0.12),
    }

    def __init__(self, parent: tk.Widget, records: list[dict], **kwargs):
        super().__init__(parent, bg=SURFACE, **kwargs)
        self._records = records
        self._mode_var = tk.StringVar(value="revenue")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_canvas()

    # ── Construction ──────────────────────────────────

    def _build_toolbar(self) -> None:
        bar = tk.Frame(self, bg=SURFACE, pady=4, padx=8)
        bar.grid(row=0, column=0, sticky="ew")

        tk.Label(bar, text="CHARTS", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(side="left")

        for value, label in self._MODES:
            rb = tk.Radiobutton(
                bar,
                text=label,
                variable=self._mode_var,
                value=value,
                command=self._redraw,
                font=FONT_LABEL,
                bg=SURFACE, fg=TEXT_MUTED,
                selectcolor=CARD,
                activebackground=SURFACE,
                activeforeground=ACCENT,
                indicatoron=0,
                relief="flat",
                padx=8, pady=3,
                cursor="hand2",
            )
            rb.pack(side="left", padx=4)

    def _build_canvas(self) -> None:
        # Fixed figure — TkAgg manages pixel dimensions automatically.
        # Never call set_size_inches inside a resize handler.
        self._fig = plt.figure(facecolor=BG, figsize=(8, 2.8), dpi=100)
        self._ax  = self._fig.add_subplot(111)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().grid(
            row=1, column=0, sticky="nsew", padx=4, pady=(0, 4)
        )

    # ── Public API ────────────────────────────────────

    def refresh(self, records: list[dict]) -> None:
        """Update the internal record list and redraw the active chart."""
        self._records = records
        self._redraw()

    # ── Internal Draw Dispatcher ──────────────────────

    def _redraw(self) -> None:
        # clf() + add_subplot() gives a truly clean axes each time.
        # ax.clear() leaves pie-chart state (equal aspect ratio, transforms)
        # which breaks bar/line charts when switching back.
        self._fig.clf()
        self._ax = self._fig.add_subplot(111)
        mode = self._mode_var.get()

        if not self._records:
            self._ax.text(
                0.5, 0.5, "No data yet",
                ha="center", va="center",
                transform=self._ax.transAxes,
                color=TEXT_MUTED, fontsize=10,
            )
            self._ax.set_facecolor(SURFACE)
            self._canvas.draw_idle()
            return

        draw_fn = {
            "revenue":  self._draw_revenue,
            "category": self._draw_category,
            "top":      self._draw_top_products,
        }
        draw_fn[mode]()
        self._fig.subplots_adjust(**self._ADJUST[mode])
        self._canvas.draw_idle()

    # ── Chart Renderers ───────────────────────────────

    def _draw_revenue(self) -> None:
        """Bar + line chart of monthly revenue."""
        by_month: dict[str, float] = defaultdict(float)
        for r in self._records:
            try:
                by_month[r["date"][:7]] += float(r["qty"]) * float(r["price"])
            except (KeyError, ValueError):
                pass

        if not by_month:
            return

        months = sorted(by_month)
        values = [by_month[m] for m in months]
        labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months]
        x      = range(len(months))

        bars = self._ax.bar(x, values, color=ACCENT, alpha=0.85, width=0.6, zorder=3)
        self._ax.plot(list(x), values, color=ACCENT3,
                      linewidth=1.5, marker="o", markersize=4, zorder=4)

        for bar, val in zip(bars, values):
            self._ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.02,
                f"₱{val:,.0f}",
                ha="center", va="bottom",
                fontsize=7, color=TEXT, fontweight="bold",
            )

        self._ax.set_xticks(list(x))
        self._ax.set_xticklabels(labels, rotation=30, ha="right")
        self._ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"₱{v:,.0f}")
        )
        self._ax.set_title("Monthly Revenue", color=TEXT)
        self._ax.grid(axis="y", zorder=0)
        self._ax.set_axisbelow(True)

    def _draw_category(self) -> None:
        """Pie chart of revenue share per category."""
        by_cat: dict[str, float] = defaultdict(float)
        for r in self._records:
            cat = r.get("category") or "Uncategorized"
            by_cat[cat] += float(r["qty"]) * float(r["price"])

        if not by_cat:
            return

        cats   = list(by_cat)
        values = [by_cat[c] for c in cats]
        colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(cats))]

        _, _, autotexts = self._ax.pie(
            values, labels=cats, autopct="%1.1f%%",
            colors=colors, startangle=140,
            wedgeprops={"edgecolor": BG, "linewidth": 1.5},
            textprops={"color": TEXT, "fontsize": 8},
        )
        for at in autotexts:
            at.set_color(BG)
            at.set_fontweight("bold")
            at.set_fontsize(7)

        self._ax.set_title("Revenue by Category", color=TEXT)

    def _draw_top_products(self) -> None:
        """Horizontal bar chart of top-8 products by revenue."""
        by_prod: dict[str, float] = defaultdict(float)
        for r in self._records:
            by_prod[r["product"]] += float(r["qty"]) * float(r["price"])

        if not by_prod:
            return

        top    = sorted(by_prod.items(), key=lambda x: x[1], reverse=True)[:8]
        labels = [p[0][:20] + ("…" if len(p[0]) > 20 else "") for p in top]
        values = [p[1] for p in top]
        colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(labels))]

        bars = self._ax.barh(range(len(labels)), values,
                             color=colors, alpha=0.85, height=0.6, zorder=3)

        for bar, val in zip(bars, values):
            self._ax.text(
                val + max(values) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"₱{val:,.0f}",
                va="center", fontsize=7, color=TEXT, fontweight="bold",
            )

        self._ax.set_yticks(range(len(labels)))
        self._ax.set_yticklabels(labels)
        self._ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"₱{v:,.0f}")
        )
        self._ax.set_title("Top Products by Revenue", color=TEXT)
        self._ax.invert_yaxis()
        self._ax.grid(axis="x", zorder=0)
        self._ax.set_axisbelow(True)
