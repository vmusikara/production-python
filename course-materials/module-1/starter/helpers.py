import csv


def read_sales_rows(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def total_revenue_by_store(rows):
    totals = {}
    for row in rows:
        store = row["store_id"]
        qty = int(row["quantity"])
        price = float(row["unit_price"])
        totals[store] = totals.get(store, 0.0) + qty * price
    return totals
