"""
=========================================================
SALES LEDGER - SALES RECORD SYSTEM
=========================================================

Authors: 
Leon James Tan (Project Manager) 
Val Medalla (Software Developer)
Mark Daniel Abellar (Software Developer)  
Aaron Gregorio Tamayo (Client) 
Steve Ligson (Quality Assurance Specialist)

Language    : Python
GUI Library : Tkinter
Database    : JSON File Storage
Charts      : Matplotlib
Version     : 1.0

Description:
A desktop-based Sales Record System used to record,
manage, search, update, delete, and analyze sales
transactions. The application provides data visualization
through charts and supports exporting records to CSV files.

Features:
- Add sales records
- Update existing records
- Delete records
- Search and filter records
- Revenue analytics charts
- Category revenue distribution
- Top products analysis
- CSV export functionality
- Local JSON database storage

Storage Location:
%APPDATA%/SalesLedger/sales_data.json

=========================================================
"""

# Import Required Libraries
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Import Matplotlib for Data Visualization
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

'''
Application Styling and Theme Configuration:
Defines colors, fonts, and visual appearance of the system.
'''
# Color Palette
BG          = "#0f1117"
SURFACE     = "#1a1d27"
CARD        = "#22263a"
ACCENT      = "#f0c040"
ACCENT3     = "#58CCED"
ACCENT2     = "#e05c5c"
TEXT        = "#e8eaf0"
TEXT_MUTED  = "#7a7f9a"
BORDER      = "#2e3349"
SUCCESS     = "#4ecca3"
ROW_ALT     = "#1e2235"
WHITE       = "#ffffff"

# Font Definitions
FONT_SALES  = ("Segoe UI", 11)
FONT_TITLE  = ("Bahnschrift", 22, "bold")
FONT_LABEL  = ("Bahnschrift", 9, "bold")
FONT_INPUT  = ("Bahnschrift", 10)
FONT_BTN    = ("Bahnschrift", 10, "bold")
FONT_TABLE  = ("Bahnschrift", 10)
FONT_STAT   = ("Bahnschrift", 24, "bold")

'''
--------------------------------------------------------
Local Database Configuration					 
--------------------------------------------------------
The application stores all sales records inside a JSON
file located in the user's AppData folder.
-------------------------------------------------------- 
'''

APP_DIR = Path(os.getenv("APPDATA")) / "SalesLedger"
APP_DIR.mkdir(exist_ok=True)

DATA_FILE = APP_DIR / "sales_data.json"

'''
Matplotlib Theme Settings:
Applies the application's dark theme to all charts.
'''
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

'''
Resource File Handler:
Retrieves paths for images and icons, including support
for executable builds created with PyInstaller.
'''
def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)

'''
Data Management Functions:
Handles loading, saving, formatting, and ID generation.
'''
# Load Sales Records from JSON File.
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

# Save Sales Records from JSON File.
def save_data(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)

# Generate the Next Available Record ID.
def next_id(records):
    return max((r["id"] for r in records), default=0) + 1

# Format numbers as Philippine Peso Currency.
def fmt_php(val):
    return f"₱{float(val):,.2f}"

'''
Custom Widget Styling Functions:
Creates reusable styled input fields and buttons.
'''
# Create a Styled Text Entry Field.
def styled_entry(parent, width=22):
    e = tk.Entry(parent, font=FONT_INPUT, bg=CARD, fg=TEXT,
                 insertbackground=ACCENT, relief="flat",
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT, width=width)
    return e

# Create a Styled Button with Hover Effects.
def styled_btn(parent, text, command, color=ACCENT, fg=BG, width=14):
    b = tk.Button(parent, text=text, command=command,
                  font=FONT_BTN, bg=color, fg=fg,
                  activebackground=TEXT, activeforeground=BG,
                  relief="flat", bd=0, padx=12, pady=6,
                  cursor="hand2", width=width)
    b.bind("<Enter>", lambda e: b.config(bg=TEXT))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b

'''
Main Application Class:
Controls the entire Sales Ledger GUI and functionality.
'''
class SalesApp(tk.Tk):

    '''
    Application Initialization:
    Loads data, sets up window, and builds UI.
    '''
    def __init__(self):
        super().__init__()
        self.title("SALES LEDGER")
        self.configure(bg=BG)
        self.geometry("1180x820")
        self.minsize(900, 700)
        try:
            icon = tk.PhotoImage(file=resource_path("logo1.png"))
            self.iconphoto(True, icon)
        except Exception:
            pass
        self.resizable(True, True)

        self.records = load_data()
        self.selected_id = None
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.refresh_table())

        self._build_ui()
        self.refresh_table()
        self.refresh_stats()
        self.refresh_charts()

    '''
    Main User Interface Layout:
    Creates header, body, and main screen structure.
    '''
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, pady=16)
        hdr.pack(fill="x")

        try:
            logo_img = Image.open(resource_path("logo2.png"))
            logo_img = logo_img.resize((32, 32))
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(hdr, image=self.logo, bg=SURFACE).pack(side="left", padx=(28, 8))
        except Exception:
            pass

        tk.Label(hdr, text="SALES LEDGER", font=FONT_TITLE,
                 bg=SURFACE, fg=WHITE).pack(side="left", padx=5)
        tk.Label(hdr, text="SALES RECORD SYSTEM",
                 font=FONT_SALES, bg=SURFACE, fg=TEXT_MUTED).pack(side="left", padx=4)

        # Body split
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    '''
    Left Panel:
    Contains search bar, sales table, and charts.
    '''
    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.rowconfigure(1, weight=2)
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        # Search Bar
        sf = tk.Frame(left, bg=SURFACE, pady=8, padx=10)
        sf.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tk.Label(sf, text="SEARCH", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(side="left", padx=(0, 8))
        se = styled_entry(sf, width=30)
        se.pack(side="left")
        se.config(textvariable=self._search_var)
        export_btn = styled_btn(sf, "⬇ EXPORT CSV", self.export_csv, ACCENT2, TEXT, 14)
        export_btn.pack(side="right", padx=4)

        # Table
        tf = tk.Frame(left, bg=BORDER, padx=1, pady=1)
        tf.grid(row=1, column=0, sticky="nsew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)

        cols = ("ID", "Date", "Customer", "Product", "Category", "Qty", "Unit Price", "Total")
        style = ttk.Style(self)
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
        style.layout("Sales.Treeview", [("Sales.Treeview.treearea", {"sticky": "nswe"})])

        self.tree = ttk.Treeview(tf, columns=cols, show="headings",
                                  style="Sales.Treeview", selectmode="browse")
        widths = [40, 90, 175, 175, 100, 50, 90, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w, anchor="center" if col in ("ID","Qty","Total","Unit Price") else "w")
        self.tree.tag_configure("alt", background=ROW_ALT)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Delete>", lambda e: self.delete_record())

        # Charts Panel
        chart_outer = tk.Frame(left, bg=SURFACE)
        chart_outer.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        chart_outer.columnconfigure(0, weight=1)
        chart_outer.rowconfigure(1, weight=1)

        # Chart Type Buttons
        ctrl = tk.Frame(chart_outer, bg=SURFACE, pady=4, padx=8)
        ctrl.grid(row=0, column=0, sticky="ew")
        tk.Label(ctrl, text="CHARTS", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(side="left")

        self._chart_mode = tk.StringVar(value="revenue")
        for val, lbl in [("revenue", "Revenue Over Time"),
                         ("category", "By Category"),
                         ("top", "Top Products")]:
            rb = tk.Radiobutton(ctrl, text=lbl, variable=self._chart_mode,
                                value=val, command=self.refresh_charts,
                                font=FONT_LABEL, bg=SURFACE, fg=TEXT_MUTED,
                                selectcolor=CARD, activebackground=SURFACE,
                                activeforeground=ACCENT, indicatoron=0,
                                relief="flat", padx=8, pady=3,
                                cursor="hand2")
            rb.pack(side="left", padx=4)

        self._fig = plt.figure(facecolor=BG, figsize=(8, 2.8), dpi=100)
        self._ax  = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._fig, master=chart_outer)
        self._canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))

    '''
    Right Panel:
    Contains summary statistics and record form.
    '''
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        # Statistics
        stats_frame = tk.Frame(right, bg=SURFACE, padx=12, pady=10)
        stats_frame.pack(fill="x", pady=(0, 10))
        tk.Label(stats_frame, text="SUMMARY", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).pack(anchor="w")
        self.stat_total = self._stat_card(stats_frame, "TOTAL REVENUE", "₱0.00", ACCENT)
        self.stat_sales = self._stat_card(stats_frame, "TRANSACTIONS", "0", SUCCESS)
        self.stat_top   = self._stat_card(stats_frame, "TOP PRODUCT", "—", ACCENT2)

        # Text Forms
        form_frame = tk.Frame(right, bg=SURFACE, padx=14, pady=14)
        form_frame.pack(fill="x")
        tk.Label(form_frame, text="ADD / EDIT RECORD", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_MUTED).grid(row=0, columnspan=2,
                                                  sticky="w", pady=(0, 10))
        fields = [
            ("Date (YYYY-MM-DD)", "date"),
            ("Customer Name",     "customer"),
            ("Product",           "product"),
            ("Category",          "category"),
            ("Quantity",          "qty"),
            ("Unit Price (₱)",    "price"),
        ]
        self._entries = {}
        for i, (label, key) in enumerate(fields, start=1):
            tk.Label(form_frame, text=label, font=FONT_LABEL,
                     bg=SURFACE, fg=TEXT_MUTED).grid(row=i, column=0, sticky="w", pady=3)
            e = styled_entry(form_frame, width=18)
            e.grid(row=i, column=1, sticky="ew", pady=3, padx=(6, 0))
            self._entries[key] = e
        form_frame.columnconfigure(1, weight=1)

        btn_row = tk.Frame(form_frame, bg=SURFACE)
        btn_row.grid(row=len(fields)+1, columnspan=2, pady=(12, 0), sticky="ew")
        styled_btn(btn_row, "✚ ADD",    self.add_record,    ACCENT,  BG).pack(side="left", padx=(0,4))
        styled_btn(btn_row, "✎ UPDATE", self.update_record, SUCCESS, BG).pack(side="left", padx=4)
        styled_btn(btn_row, "✖ DELETE", self.delete_record, ACCENT2, TEXT).pack(side="left", padx=4)
        styled_btn(btn_row, "⊘ CLEAR",  self.clear_form,    BORDER,  TEXT_MUTED).pack(side="left", padx=4)

        self._entries["date"].insert(0, datetime.today().strftime("%Y-%m-%d"))

    '''
    Statistic Card Creator:
    Creates reusable summary cards.
    '''
    def _stat_card(self, parent, label, value, color):
        f = tk.Frame(parent, bg=CARD, padx=10, pady=8)
        f.pack(fill="x", pady=3)
        tk.Label(f, text=label, font=FONT_LABEL, bg=CARD, fg=TEXT_MUTED).pack(anchor="w")
        lbl = tk.Label(f, text=value, font=FONT_STAT, bg=CARD, fg=color)
        lbl.pack(anchor="w")
        return lbl

    '''
    Chart Management Section:
    Handles chart creation and visualization updates.
    '''
    # Refresh Currently Selected Chart.
    def refresh_charts(self):
        self._fig.clf()
        self._ax = self._fig.add_subplot(111)
        mode = self._chart_mode.get()

        if not self.records:
            self._ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                          transform=self._ax.transAxes, color=TEXT_MUTED, fontsize=10)
            self._ax.set_facecolor(SURFACE)
            self._canvas.draw_idle()
            return

        if mode == "revenue":
            self._draw_revenue_chart()
            self._fig.subplots_adjust(left=0.14, right=0.97, top=0.88, bottom=0.28)
        elif mode == "category":
            self._draw_category_chart()
            self._fig.subplots_adjust(left=0.05, right=0.95, top=0.88, bottom=0.05)
        elif mode == "top":
            self._draw_top_products_chart()
            self._fig.subplots_adjust(left=0.28, right=0.88, top=0.88, bottom=0.12)

        self._canvas.draw_idle()

    '''
    Revenue Chart:
    Displays monthly revenue trends.
    '''
     # Group Revenue by Month
    def _draw_revenue_chart(self):
        # Group revenue by month
        by_month = defaultdict(float)
        for r in self.records:
            try:
                month = r["date"][:7]  # "YYYY-MM"
                by_month[month] += float(r["qty"]) * float(r["price"])
            except Exception:
                pass

        if not by_month:
            return

        months = sorted(by_month.keys())
        values = [by_month[m] for m in months]
        labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months]

        x = range(len(months))
        bars = self._ax.bar(x, values, color=ACCENT, alpha=0.85, width=0.6, zorder=3)

        # Line Overlay
        self._ax.plot(list(x), values, color=ACCENT3, linewidth=1.5,
                      marker="o", markersize=4, zorder=4)

        # Value Labels on Bars
        for bar, val in zip(bars, values):
            self._ax.text(bar.get_x() + bar.get_width() / 2,
                          bar.get_height() + max(values) * 0.02,
                          f"₱{val:,.0f}", ha="center", va="bottom",
                          fontsize=7, color=TEXT, fontweight="bold")

        self._ax.set_xticks(list(x))
        self._ax.set_xticklabels(labels, rotation=30, ha="right")
        self._ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"₱{v:,.0f}"))
        self._ax.set_title("Monthly Revenue", color=TEXT)
        self._ax.grid(axis="y", zorder=0)
        self._ax.set_axisbelow(True)

    '''
    Category Pie Chart:
    Shows revenue distribution by category.
    '''
    def _draw_category_chart(self):
        by_cat = defaultdict(float)
        for r in self.records:
            cat = r.get("category", "Uncategorized") or "Uncategorized"
            by_cat[cat] += float(r["qty"]) * float(r["price"])

        if not by_cat:
            return

        cats   = list(by_cat.keys())
        values = [by_cat[c] for c in cats]

        palette = [ACCENT, ACCENT3, ACCENT2, SUCCESS,
                   "#a78bfa", "#fb923c", "#34d399", "#60a5fa"]
        colors = [palette[i % len(palette)] for i in range(len(cats))]

        wedges, texts, autotexts = self._ax.pie(
            values, labels=cats, autopct="%1.1f%%",
            colors=colors, startangle=140,
            wedgeprops={"edgecolor": BG, "linewidth": 1.5},
            textprops={"color": TEXT, "fontsize": 8})
        for at in autotexts:
            at.set_color(BG)
            at.set_fontweight("bold")
            at.set_fontsize(7)

        self._ax.set_title("Revenue by Category", color=TEXT)

    '''
    Top Products Chart:
    Displays highest earning products.
    '''
    def _draw_top_products_chart(self):
        by_prod = defaultdict(float)
        for r in self.records:
            by_prod[r["product"]] += float(r["qty"]) * float(r["price"])

        if not by_prod:
            return

        # Top Products
        sorted_prods = sorted(by_prod.items(), key=lambda x: x[1], reverse=True)[:8]
        labels = [p[0][:20] + ("…" if len(p[0]) > 20 else "") for p in sorted_prods]
        values = [p[1] for p in sorted_prods]

        # Horizontal Bar Chart
        palette = [ACCENT, ACCENT3, SUCCESS, ACCENT2,
                   "#a78bfa", "#fb923c", "#34d399", "#60a5fa"]
        colors = [palette[i % len(palette)] for i in range(len(labels))]

        y = range(len(labels))
        bars = self._ax.barh(list(y), values, color=colors, alpha=0.85,
                             height=0.6, zorder=3)

        for bar, val in zip(bars, values):
            self._ax.text(val + max(values) * 0.01,
                          bar.get_y() + bar.get_height() / 2,
                          f"₱{val:,.0f}", va="center",
                          fontsize=7, color=TEXT, fontweight="bold")

        self._ax.set_yticks(list(y))
        self._ax.set_yticklabels(labels)
        self._ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"₱{v:,.0f}"))
        self._ax.set_title("Top Products by Revenue", color=TEXT)
        self._ax.invert_yaxis()
        self._ax.grid(axis="x", zorder=0)
        self._ax.set_axisbelow(True)

    '''
    Table Management Section:
    Handles displaying and interacting with records.
    '''
    # Update Table Contents and Apply Search Filter.    
    def refresh_table(self, *_):
        query = self._search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for i, r in enumerate(self.records):
            vals = (r["id"], r["date"], r["customer"], r["product"],
                    r["category"], r["qty"], fmt_php(r["price"]),
                    fmt_php(float(r["qty"]) * float(r["price"])))
            if query and not any(query in str(v).lower() for v in vals):
                continue
            tag = "alt" if i % 2 else ""
            self.tree.insert("", "end", iid=str(r["id"]), values=vals, tags=(tag,))

    # Update Summary Statistics.
    def refresh_stats(self):
        total = sum(float(r["qty"]) * float(r["price"]) for r in self.records)
        self.stat_total.config(text=fmt_php(total))
        self.stat_sales.config(text=str(len(self.records)))
        if self.records:
            by_prod = defaultdict(float)
            for r in self.records:
                by_prod[r["product"]] += float(r["qty"]) * float(r["price"])
            top = max(by_prod, key=by_prod.get)
            self.stat_top.config(text=top[:18] + ("…" if len(top) > 18 else ""))
        else:
            self.stat_top.config(text="—")

    # Load Selected Record into Form Fields.
    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        rid = int(sel[0])
        r = next((x for x in self.records if x["id"] == rid), None)
        if not r:
            return
        self.selected_id = rid
        mapping = {"date": r["date"], "customer": r["customer"],
                   "product": r["product"], "category": r["category"],
                   "qty": str(r["qty"]), "price": str(r["price"])}
        for k, e in self._entries.items():
            e.delete(0, "end")
            e.insert(0, mapping[k])

    '''
    Form Validation Section:
    Ensures user input is valid before processing.
    '''
    # Validate and Retrieve Form Data.
    def _get_form(self):
        try:
            date     = self._entries["date"].get().strip()
            customer = self._entries["customer"].get().strip()
            product  = self._entries["product"].get().strip()
            category = self._entries["category"].get().strip()
            qty      = int(self._entries["qty"].get().strip())
            price    = float(self._entries["price"].get().strip())
            datetime.strptime(date, "%Y-%m-%d")
            if not customer or not product:
                raise ValueError("Customer and Product required")
            if qty <= 0 or price <= 0:
                raise ValueError("Qty and Price must be positive")
            return date, customer, product, category, qty, price
        except ValueError as ex:
            messagebox.showerror("Invalid Input", str(ex))
            return None

    '''
    CRUD Operations:
    Create, Read, Update, and Delete sales records.
    '''
    # Add a New Sales Record.
    def add_record(self):
        d = self._get_form()
        if not d:
            return
        date, customer, product, category, qty, price = d
        for r in self.records:
            if (r["date"] == date and
                r["customer"].lower() == customer.lower() and
                r["product"].lower() == product.lower()):
                messagebox.showwarning(
            "Duplicate Record",
            "This sales record already exists."
                )
                return
        rec = {"id": next_id(self.records), "date": date,
               "customer": customer, "product": product,
               "category": category, "qty": qty, "price": price}
        self.records.append(rec)
        save_data(self.records)
        self.refresh_table()
        self.refresh_stats()
        self.refresh_charts()
        self.clear_form()
        self._flash_status(f"Record #{rec['id']} added.")

    # Update the Selected Sales Record.
    def update_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a row to update.")
            return
        d = self._get_form()
        if not d:
            return

        if not messagebox.askyesno(
            "Confirm Update",
            "Are you sure you want to update this record?"
        ):
            return

        _, customer, product, category, qty, price = d
        date = datetime.today().strftime("%Y-%m-%d")
        for r in self.records:
            if r["id"] == self.selected_id:
                r.update(date=date, customer=customer, product=product,
                          category=category, qty=qty, price=price)
                break
        save_data(self.records)
        self.refresh_table()
        self.refresh_stats()
        self.refresh_charts()
        self._flash_status(f"Record #{self.selected_id} updated.")

    # Delete the Selected Sales Record.
    def delete_record(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a row to delete.")
            return
        if not messagebox.askyesno("Confirm", f"Delete record #{self.selected_id}?"):
            return
        self.records = [r for r in self.records if r["id"] != self.selected_id]
        save_data(self.records)
        self.selected_id = None
        self.clear_form()
        self.refresh_table()
        self.refresh_stats()
        self.refresh_charts()
        self._flash_status("Record deleted.")

    '''
    Form Utilities:
    Handles clearing and resetting form fields.
    '''
    # Reset Form Fields and Clear Selection.
    def clear_form(self):
        self.selected_id = None
        for e in self._entries.values():
            e.delete(0, "end")
        self._entries["date"].insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.tree.selection_remove(*self.tree.selection())

    # Export Sales Records to a CSV File.
    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"sales_{datetime.today().strftime('%Y%m%d')}.csv")
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ID","Date","Customer","Product","Category","Qty","Unit Price","Total"])
            for r in self.records:
                w.writerow([r["id"], f"'{r['date']}", r["customer"], r["product"],
                             r["category"], r["qty"], r["price"],
                             float(r["qty"]) * float(r["price"])])
        messagebox.showinfo("Exported", f"Saved to:\n{path}")

    # Sort Table Data by Selected Column.
    def _sort_by(self, col):
        col_map = {"ID":"id","Date":"date","Customer":"customer","Product":"product",
                   "Category":"category","Qty":"qty","Unit Price":"price","Total":"total"}
        key = col_map.get(col, col.lower())
        if key == "total":
            self.records.sort(key=lambda r: float(r["qty"]) * float(r["price"]))
        elif key in ("qty", "price", "id"):
            self.records.sort(key=lambda r: float(r.get(key, 0)))
        else:
            self.records.sort(key=lambda r: str(r.get(key, "")).lower())
        self.refresh_table()

    '''
    Status Notifications:
    Displays temporary success messages.
    '''
    # Show a Temporary Status Message.
    def _flash_status(self, msg):
        if not hasattr(self, "_status_lbl"):
            self._status_lbl = tk.Label(self, text="", font=FONT_LABEL,
                                         bg=ACCENT, fg=BG, pady=4)
        self._status_lbl.config(text=f"  ✓  {msg}  ")
        self._status_lbl.pack(side="bottom", fill="x")
        self.after(2500, lambda: self._status_lbl.pack_forget())

'''
Demo Data Generator:
Creates sample records when no data file exists.
'''
def seed_demo():
    if os.path.exists(DATA_FILE):
        return
    demo = [
        {"id":1,"date":"2025-01-10","customer":"Leon James Tan","product":"Office Chair","category":"Furniture","qty":2,"price":4500},
        {"id":2,"date":"2025-01-12","customer":"Aaron Gregorio Tamayo","product":"Mechanical Keyboard","category":"Electronics","qty":3,"price":1800},
        {"id":3,"date":"2025-01-15","customer":"Val Medalla","product":"LED Monitor 24\"","category":"Electronics","qty":1,"price":8500},
        {"id":4,"date":"2025-02-01","customer":"Steve Ligason","product":"Notebook A4 (pack)","category":"Supplies","qty":10,"price":250},
        {"id":5,"date":"2025-02-14","customer":"Mark Daniel Abellar","product":"Standing Desk","category":"Furniture","qty":1,"price":12000},
    ]
    save_data(demo)

'''
Application Entry Point:
Starts the program when executed directly.
'''
if __name__ == "__main__":
    seed_demo()
    app = SalesApp()
    app.mainloop()
