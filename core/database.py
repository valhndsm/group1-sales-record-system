"""
=========================================================
database.py
=========================================================
Data layer: load/save JSON records, ID generation,
currency formatting, and demo data seeding.
=========================================================
"""

import os
import json
from .constants import DATA_FILE


# ── Load / Save ───────────────────────────────────────

def load_data() -> list[dict]:
    """Load all sales records from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []


def save_data(records: list[dict]) -> None:
    """Persist all sales records to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)


# ── Helpers ───────────────────────────────────────────

def next_id(records: list[dict]) -> int:
    """Return the next available record ID."""
    return max((r["id"] for r in records), default=0) + 1


def fmt_php(val) -> str:
    """Format a numeric value as Philippine Peso currency."""
    return f"₱{float(val):,.2f}"


# ── Demo Data ─────────────────────────────────────────

DEMO_RECORDS = [
    {"id": 1, "date": "2025-01-10", "customer": "Leon James Tan",
     "product": "Office Chair",        "category": "Furniture",    "qty": 2,  "price": 4500},
    {"id": 2, "date": "2025-01-12", "customer": "Aaron Gregorio Tamayo",
     "product": "Mechanical Keyboard", "category": "Electronics",  "qty": 3,  "price": 1800},
    {"id": 3, "date": "2025-01-15", "customer": "Val Medalla",
     "product": "LED Monitor 24\"",    "category": "Electronics",  "qty": 1,  "price": 8500},
    {"id": 4, "date": "2025-02-01", "customer": "Steve Ligason",
     "product": "Notebook A4 (pack)",  "category": "Supplies",     "qty": 10, "price": 250},
    {"id": 5, "date": "2025-02-14", "customer": "Mark Daniel Abellar",
     "product": "Standing Desk",       "category": "Furniture",    "qty": 1,  "price": 12000},
]


def seed_demo() -> None:
    """Write demo records only if no data file exists yet."""
    if not os.path.exists(DATA_FILE):
        save_data(DEMO_RECORDS)
