"""
=========================================================
main.py  —  Application Entry Point
=========================================================
Run this file to launch the Sales Ledger:

    python main.py

=========================================================
"""

from core.database import seed_demo
from app import SalesApp


def main() -> None:
    seed_demo()
    app = SalesApp()
    app.mainloop()


if __name__ == "__main__":
    main()
