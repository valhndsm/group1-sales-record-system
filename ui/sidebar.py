"""
=========================================================
sidebar.py
=========================================================
Sidebar — the right-hand panel containing:
  • Summary stat cards  (total revenue, transactions, top product)
  • Add / Edit record form with validation
  • Action buttons: Add, Update, Delete, Clear
=========================================================
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Callable

from core.constants import (
    BG, SURFACE, CARD, TEXT, TEXT_MUTED,
    ACCENT, ACCENT2, BORDER, SUCCESS, WHITE,
    FONT_LABEL, FONT_STAT,
)
from core.utils import styled_entry, styled_btn
from core.database import fmt_php


class Sidebar(tk.Frame):
    """
    Right-panel widget: statistics summary + record form.

    Callbacks
    ---------
    on_add(date, customer, product, category, qty, price)
    on_update(date, customer, product, category, qty, price)
    on_delete()
    """

    _FIELDS = [
        ("Date (YYYY-MM-DD)", "date"),
        ("Customer Name",     "customer"),
        ("Product",           "product"),
        ("Category",          "category"),
        ("Quantity",          "qty"),
        ("Unit Price (₱)",    "price"),
    ]

    def __init__(
        self,
        parent: tk.Widget,
        on_add:    Callable,
        on_update: Callable,
        on_delete: Callable[[], None],
        **kwargs,
    ):
        super().__init__(parent, bg=BG, **kwargs)
        self.columnconfigure(0, weight=1)

        self._on_add    = on_add
        self._on_update = on_update
        self._on_delete = on_delete

        self._build_stats()
        self._build_form()

    # ── Construction ──────────────────────────────────

    def _build_stats(self) -> None:
        frame = tk.Frame(self, bg=SURFACE, padx=12, pady=10)
        frame.pack(fill="x", pady=(0, 10))
        tk.Label(frame, text="SUMMARY", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor="w")

        self.stat_total = self._stat_card(frame, "TOTAL REVENUE", "₱0.00",  ACCENT)
        self.stat_sales = self._stat_card(frame, "TRANSACTIONS",  "0",       SUCCESS)
        self.stat_top   = self._stat_card(frame, "TOP PRODUCT",   "—",       ACCENT2)

    def _stat_card(self, parent: tk.Widget, label: str,
                   value: str, color: str) -> tk.Label:
        f = tk.Frame(parent, bg=CARD, padx=10, pady=8)
        f.pack(fill="x", pady=3)
        tk.Label(f, text=label, font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED).pack(anchor="w")
        lbl = tk.Label(f, text=value, font=FONT_STAT, bg=CARD, fg=color)
        lbl.pack(anchor="w")
        return lbl

    def _build_form(self) -> None:
        frame = tk.Frame(self, bg=SURFACE, padx=14, pady=14)
        frame.pack(fill="x")
        frame.columnconfigure(1, weight=1)

        tk.Label(frame, text="ADD / EDIT RECORD", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).grid(
            row=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        self._entries: dict[str, tk.Entry] = {}
        for i, (label, key) in enumerate(self._FIELDS, start=1):
            tk.Label(frame, text=label, font=FONT_LABEL,
                     bg=SURFACE, fg=TEXT_MUTED).grid(
                row=i, column=0, sticky="w", pady=3
            )
            e = styled_entry(frame, width=18)
            e.grid(row=i, column=1, sticky="ew", pady=3, padx=(6, 0))
            self._entries[key] = e

        btn_row = tk.Frame(frame, bg=SURFACE)
        btn_row.grid(row=len(self._FIELDS) + 1, columnspan=2,
                     pady=(12, 0), sticky="ew")

        styled_btn(btn_row, "✚ ADD",    self._handle_add,    ACCENT,  BG).pack(side="left", padx=(0, 4))
        styled_btn(btn_row, "✎ UPDATE", self._handle_update, SUCCESS, BG).pack(side="left", padx=4)
        styled_btn(btn_row, "✖ DELETE", self._on_delete,     ACCENT2, TEXT).pack(side="left", padx=4)
        styled_btn(btn_row, "⊘ CLEAR",  self.clear,          BORDER,  TEXT_MUTED).pack(side="left", padx=4)

        self._entries["date"].insert(0, datetime.today().strftime("%Y-%m-%d"))

    # ── Public API ────────────────────────────────────

    def update_stats(self, records: list[dict]) -> None:
        """Recompute and refresh the three stat cards."""
        from collections import defaultdict
        total = sum(float(r["qty"]) * float(r["price"]) for r in records)
        self.stat_total.config(text=fmt_php(total))
        self.stat_sales.config(text=str(len(records)))

        if records:
            by_prod: dict[str, float] = defaultdict(float)
            for r in records:
                by_prod[r["product"]] += float(r["qty"]) * float(r["price"])
            top = max(by_prod, key=by_prod.get)
            self.stat_top.config(text=top[:18] + ("…" if len(top) > 18 else ""))
        else:
            self.stat_top.config(text="—")

    def load_record(self, record: dict) -> None:
        """Populate form fields from an existing record dict."""
        mapping = {
            "date":     record["date"],
            "customer": record["customer"],
            "product":  record["product"],
            "category": record["category"],
            "qty":      str(record["qty"]),
            "price":    str(record["price"]),
        }
        for key, entry in self._entries.items():
            entry.delete(0, "end")
            entry.insert(0, mapping[key])

    def clear(self) -> None:
        """Reset all form fields to defaults."""
        for entry in self._entries.values():
            entry.delete(0, "end")
        self._entries["date"].insert(0, datetime.today().strftime("%Y-%m-%d"))

    # ── Validation ────────────────────────────────────

    def _get_form(self) -> tuple | None:
        """Validate and return form values, or show an error and return None."""
        try:
            date     = self._entries["date"].get().strip()
            customer = self._entries["customer"].get().strip()
            product  = self._entries["product"].get().strip()
            category = self._entries["category"].get().strip()
            qty      = int(self._entries["qty"].get().strip())
            price    = float(self._entries["price"].get().strip())
            datetime.strptime(date, "%Y-%m-%d")
            if not customer or not product:
                raise ValueError("Customer and Product are required.")
            if qty <= 0 or price <= 0:
                raise ValueError("Qty and Price must be positive.")
            return date, customer, product, category, qty, price
        except ValueError as exc:
            messagebox.showerror("Invalid Input", str(exc))
            return None

    # ── Button Handlers ───────────────────────────────

    def _handle_add(self) -> None:
        data = self._get_form()
        if data:
            self._on_add(*data)

    def _handle_update(self) -> None:
        data = self._get_form()
        if data:
            self._on_update(*data)
