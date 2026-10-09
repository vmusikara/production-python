"""Core sales-report logic.

Notice this module knows nothing about the CLI, argv, or hardcoded
paths. It takes a path in, and gives data back. That separation is what
makes it testable without touching a filesystem full of magic assumptions,
and reusable from anywhere - a script, a test, a future pipeline step -
not just from one specific folder on one specific machine.
"""

import csv
from pathlib import Path


def read_sales_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def total_revenue_by_store(rows: list[dict[str, str]]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for row in rows:
        store = row["store_id"]
        qty = int(row["quantity"])
        price = float(row["unit_price"])
        totals[store] = totals.get(store, 0.0) + qty * price
    return totals
