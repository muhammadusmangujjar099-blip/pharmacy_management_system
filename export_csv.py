
import csv
import os
import sqlite3
from datetime import datetime

DB_FILE = "pharmacy.db"
OUT_DIR = "exports"


def write_csv(path, headers, rows):
    # utf-8-sig => Excel mein naam sahi dikhte hain
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  {path}  ({len(rows)} rows)")


def main():
    if not os.path.exists(DB_FILE):
        print(f"'{DB_FILE}' nahi mili. Pehle app ek dafa chalayein ya seed_data.py run karein.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    print("Tables export ho rahi hain:")
    tables = [
        r[0]
        for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    ]
    for table in tables:
        cur.execute(f'SELECT * FROM "{table}"')
        headers = [d[0] for d in cur.description]
        write_csv(os.path.join(OUT_DIR, f"{table}_{stamp}.csv"), headers, cur.fetchall())

    print("\nDetailed reports export ho rahi hain:")
    cur.execute(
        """
        SELECT b.bill_no, b.bill_date, COALESCE(c.name, '-'), m.name,
               i.quantity, i.unit_price, i.total_price, b.total_amount
        FROM sale_items i
        JOIN sale_bills b ON b.id = i.bill_id
        LEFT JOIN customers c ON c.id = b.customer_id
        LEFT JOIN medicines m ON m.id = i.medicine_id
        ORDER BY b.bill_date, b.bill_no
        """
    )
    write_csv(
        os.path.join(OUT_DIR, f"sales_report_{stamp}.csv"),
        ["Bill No", "Date", "Customer", "Medicine", "Qty", "Unit Price", "Line Total", "Bill Total"],
        cur.fetchall(),
    )

    cur.execute(
        """
        SELECT b.bill_no, b.bill_date, COALESCE(s.name, '-'), m.name,
               i.quantity, i.unit_price, i.total_price, b.total_amount
        FROM purchase_items i
        JOIN purchase_bills b ON b.id = i.bill_id
        LEFT JOIN suppliers s ON s.id = b.supplier_id
        LEFT JOIN medicines m ON m.id = i.medicine_id
        ORDER BY b.bill_date, b.bill_no
        """
    )
    write_csv(
        os.path.join(OUT_DIR, f"purchase_report_{stamp}.csv"),
        ["Bill No", "Date", "Supplier", "Medicine", "Qty", "Unit Price", "Line Total", "Bill Total"],
        cur.fetchall(),
    )

    conn.close()
    print(f"\nHo gaya! Sari files '{OUT_DIR}/' folder mein hain.")


if __name__ == "__main__":
    main()
