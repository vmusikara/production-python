# Run this with: python sales_report.py
# (You have to be sitting inside this exact folder for it to work.)

from helpers import read_sales_rows, total_revenue_by_store

# Hardcoded - this "works on my machine" because the file happens to be
# sitting right here. Move this script anywhere else, or try to import it
# from another project, and watch what happens.
SALES_FILE = "sample_data/sales_sample.csv"


def main():
    rows = read_sales_rows(SALES_FILE)
    totals = total_revenue_by_store(rows)
    print("Revenue by store:")
    for store, total in sorted(totals.items()):
        print(f"  {store}: ${total:.2f}")


if __name__ == "__main__":
    main()
