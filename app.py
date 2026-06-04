"""
=========================================================
app.py
=========================================================
SalesApp — the root Tk window.

Responsibilities
----------------
• Build the header, left panel (table + charts), and
  right panel (sidebar).
• Wire callbacks between the UI panels and the data layer.
• Own the single source of truth: self.records.
• Display transient status notifications.

All visual widgets live in ui/; all data access lives in
core/; this file only coordinates them.
=========================================================
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from core          import load_data, save_data, next_id, seed_demo, resource_path
from core.constants import (
    BG, SURFACE, TEXT_MUTED, WHITE,
    FONT_TITLE, FONT_SALES, FONT_LABEL, ACCENT,
)
from ui import ChartsPanel, SalesTable, Sidebar

try:
    from PIL import Image, ImageTk
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


class SalesApp(tk.Tk):
    """
    Main application window.
    Composes ChartsPanel, SalesTable, and Sidebar.
    """

    def __init__(self):
        super().__init__()
        self.title("SALES LEDGER")
        self.configure(bg=BG)
        self.geometry("1180x820")
        self.minsize(900, 700)
        self.resizable(True, True)

        self._load_icon()

        self.records: list[dict] = load_data()
        self.selected_id: int | None = None

        self._build_ui()
        self._refresh_all()

    # ── Icon ──────────────────────────────────────────

    def _load_icon(self) -> None:
        try:
            icon = tk.PhotoImage(file=resource_path("assets/logo1.png"))
            self.iconphoto(True, icon)
        except Exception:
            pass

    # ── Layout ────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    def _build_header(self) -> None:
        hdr = tk.Frame(self, bg=SURFACE, pady=16)
        hdr.pack(fill="x")

        if _PIL_AVAILABLE:
            try:
                img = Image.open(resource_path("assets/logo2.png")).resize((32, 32))
                self._logo = ImageTk.PhotoImage(img)
                tk.Label(hdr, image=self._logo, bg=SURFACE).pack(
                    side="left", padx=(28, 8)
                )
            except Exception:
                pass

        tk.Label(hdr, text="SALES LEDGER", font=FONT_TITLE,
                 bg=SURFACE, fg=WHITE).pack(side="left", padx=5)
        tk.Label(hdr, text="SALES RECORD SYSTEM",
                 font=FONT_SALES, bg=SURFACE, fg=TEXT_MUTED).pack(side="left", padx=4)

    def _build_left(self, parent: tk.Widget) -> None:
        left = tk.Frame(parent, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(0, weight=2)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        self.table = SalesTable(
            left,
            records=self.records,
            on_select=self._on_row_select,
            on_delete=self._handle_delete,
        )
        self.table.grid(row=0, column=0, sticky="nsew")

        self.charts = ChartsPanel(left, self.records)
        self.charts.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

    def _build_right(self, parent: tk.Widget) -> None:
        self.sidebar = Sidebar(
            parent,
            on_add=self._handle_add,
            on_update=self._handle_update,
            on_delete=self._handle_delete,
        )
        self.sidebar.grid(row=0, column=1, sticky="nsew")

    # ── Data Refresh ──────────────────────────────────

    def _refresh_all(self) -> None:
        """Push the current record list to every panel."""
        self.table.refresh(self.records)
        self.sidebar.update_stats(self.records)
        self.charts.refresh(self.records)

    # ── CRUD Callbacks ────────────────────────────────

    def _handle_add(self, date, customer, product, category, qty, price) -> None:
        # Duplicate check
        for r in self.records:
            if (r["date"] == date
                    and r["customer"].lower() == customer.lower()
                    and r["product"].lower()  == product.lower()):
                messagebox.showwarning(
                    "Duplicate Record",
                    "This sales record already exists.",
                )
                return

        rec = {
            "id": next_id(self.records),
            "date": date, "customer": customer,
            "product": product, "category": category,
            "qty": qty, "price": price,
        }
        self.records.append(rec)
        save_data(self.records)
        self._refresh_all()
        self.sidebar.clear()
        self.table.clear_selection()
        self.selected_id = None
        self._flash(f"Record #{rec['id']} added.")

    def _handle_update(self, date, customer, product, category, qty, price) -> None:
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a row to update.")
            return
        if not messagebox.askyesno("Confirm Update",
                                    "Are you sure you want to update this record?"):
            return
        for r in self.records:
            if (r["date"] == date
                    and r["customer"].lower() == customer.lower()
                    and r["product"].lower()  == product.lower()):
                messagebox.showwarning(
                    "Duplicate Record",
                    "This sales record already exists.",
                )
            if r["id"] == self.selected_id:
                r.update(
                    date=date, customer=customer, product=product,
                    category=category, qty=qty, price=price,
                )
                break
        save_data(self.records)
        self._refresh_all()
        self._flash(f"Record #{self.selected_id} updated.")

    def _handle_delete(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a row to delete.")
            return
        if not messagebox.askyesno("Confirm", f"Delete record #{self.selected_id}?"):
            return
        self.records = [r for r in self.records if r["id"] != self.selected_id]
        save_data(self.records)
        self.selected_id = None
        self.sidebar.clear()
        self.table.clear_selection()
        self._refresh_all()
        self._flash("Record deleted.")

    # ── Row Selection ─────────────────────────────────

    def _on_row_select(self, record_id: int) -> None:
        record = next((r for r in self.records if r["id"] == record_id), None)
        if record:
            self.selected_id = record_id
            self.sidebar.load_record(record)

    # ── Status Bar ────────────────────────────────────

    def _flash(self, msg: str) -> None:
        if not hasattr(self, "_status_lbl"):
            self._status_lbl = tk.Label(
                self, text="", font=FONT_LABEL, bg=ACCENT, fg=BG, pady=4
            )
        self._status_lbl.config(text=f"  ✓  {msg}  ")
        self._status_lbl.pack(side="bottom", fill="x")
        self.after(2500, self._status_lbl.pack_forget)
