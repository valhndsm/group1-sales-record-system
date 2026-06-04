"""
=========================================================
table.py
=========================================================
SalesTable — a self-contained Tkinter frame that wraps
the Treeview, search entry, filter dropdown, and the
Export CSV button into one reusable panel.
=========================================================
"""

import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from typing import Callable

from core.constants import (
    BG, SURFACE, CARD, TEXT, TEXT_MUTED, ACCENT, ACCENT2, ACCENT3,
    BORDER, ROW_ALT, FONT_LABEL, FONT_TABLE,
)
from core.utils import styled_entry, styled_btn
from core.database import fmt_php


class SalesTable(tk.Frame):
    """
    Searchable, filterable, sortable sales data table.

    Callbacks
    ---------
    on_select(record_id: int)   — fired when a row is selected
    on_delete()                 — fired when <Delete> key is pressed
    """

    _COLUMNS  = ("ID", "Date", "Customer", "Product", "Category", "Qty", "Unit Price", "Total")
    _WIDTHS   = (40,   90,     175,        175,        100,        50,    90,           90)
    _CENTER   = {"ID", "Qty", "Unit Price", "Total"}



    def __init__(
        self,
        parent: tk.Widget,
        records: list[dict],
        on_select: Callable[[int], None],
        on_delete: Callable[[], None],
        **kwargs,
    ):
        super().__init__(parent, bg=BG, **kwargs)
        self._records   = records
        self._on_select = on_select
        self._on_delete = on_delete

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.refresh())

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_searchbar()
        self._build_treeview()

    # ── Construction ──────────────────────────────────

    def _build_searchbar(self) -> None:
        sf = tk.Frame(self, bg=SURFACE, pady=8, padx=10)
        sf.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        styled_btn(sf, "⬇ EXPORT CSV", self._export_csv, ACCENT2, TEXT, 14).pack(
            side="right", padx=4
        )
        tk.Label(sf, text="SEARCH", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(side="left", padx=(0, 8))
        entry = styled_entry(sf, width=30)
        entry.config(textvariable=self._search_var)
        entry.pack(side="left")

    def _build_treeview(self) -> None:
        tf = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        tf.grid(row=1, column=0, sticky="nsew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Sales.Treeview",
                         background=SURFACE, fieldbackground=SURFACE,
                         foreground=TEXT, font=FONT_TABLE,
                         rowheight=28, borderwidth=0)
        style.configure("Sales.Treeview.Heading",
                         background=CARD, foreground=ACCENT3,
                         font=FONT_LABEL, relief="flat", borderwidth=0)
        style.map("Sales.Treeview",
                   background=[("selected", ACCENT3)],
                   foreground=[("selected", BG)])
        style.layout("Sales.Treeview",
                      [("Sales.Treeview.treearea", {"sticky": "nswe"})])

        self.tree = ttk.Treeview(
            tf,
            columns=self._COLUMNS,
            show="headings",
            style="Sales.Treeview",
            selectmode="browse",
        )
        for col, w in zip(self._COLUMNS, self._WIDTHS):
            self.tree.heading(col, text=col,
                               command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w,
                              anchor="center" if col in self._CENTER else "w")

        self.tree.tag_configure("alt", background=ROW_ALT)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self._handle_select)
        self.tree.bind("<Delete>", lambda _: self._on_delete())

    # ── Public API ────────────────────────────────────

    def refresh(self, records: list[dict] | None = None) -> None:
        """Repopulate the table, optionally with a new record list."""
        if records is not None:
            self._records = records

        query = self._search_var.get().lower().strip()

        self.tree.delete(*self.tree.get_children())
        row_i = 0
        for r in self._records:
            vals = (
                r["id"], r["date"], r["customer"], r["product"],
                r["category"], r["qty"],
                fmt_php(r["price"]),
                fmt_php(float(r["qty"]) * float(r["price"])),
            )
            if query and not any(query in str(v).lower() for v in vals):
                continue
            tag = "alt" if row_i % 2 else ""
            self.tree.insert("", "end", iid=str(r["id"]), values=vals, tags=(tag,))
            row_i += 1

    def clear_selection(self) -> None:
        self.tree.selection_remove(*self.tree.selection())

    # ── Sorting ───────────────────────────────────────

    _SORT_KEY_MAP = {
        "ID": "id", "Date": "date", "Customer": "customer",
        "Product": "product", "Category": "category",
        "Qty": "qty", "Unit Price": "price", "Total": "total",
    }

    def _sort_by(self, col: str) -> None:
        key = self._SORT_KEY_MAP.get(col, col.lower())
        if key == "total":
            self._records.sort(key=lambda r: float(r["qty"]) * float(r["price"]))
        elif key in ("qty", "price", "id"):
            self._records.sort(key=lambda r: float(r.get(key, 0)))
        else:
            self._records.sort(key=lambda r: str(r.get(key, "")).lower())
        self.refresh()

    # ── Select Handler ────────────────────────────────

    def _handle_select(self, _event=None) -> None:
        sel = self.tree.selection()
        if sel:
            self._on_select(int(sel[0]))

    # ── Export ────────────────────────────────────────

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"sales_{datetime.today().strftime('%Y%m%d')}.csv",
        )
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ID", "Date", "Customer", "Product",
                         "Category", "Qty", "Unit Price", "Total"])
            for r in self._records:
                w.writerow([
                    r["id"], f"'{r['date']}", r["customer"], r["product"],
                    r["category"], r["qty"], r["price"],
                    float(r["qty"]) * float(r["price"]),
                ])
        messagebox.showinfo("Exported", f"Saved to:\n{path}")
