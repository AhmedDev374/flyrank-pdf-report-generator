import os
import random
import sqlite3
from datetime import date, timedelta

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app_data.db"))


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the application data table and seeds it with sample
    data on first run, so there is data available to query."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            order_date TEXT NOT NULL
        );
        """
    )
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM orders;")
    count = cur.fetchone()[0]
    if count == 0:
        _seed_sample_data(conn)

    conn.close()


def _seed_sample_data(conn):
    customers = ["Alice Smith", "Bob Jones", "Carol Lee", "David Kim", "Emma Brown"]
    products = [
        ("Wireless Mouse", 19.99),
        ("Mechanical Keyboard", 79.99),
        ("USB-C Hub", 34.50),
        ("Monitor Stand", 45.00),
        ("Webcam", 59.99),
    ]

    start_date = date.today() - timedelta(days=30)
    rows = []
    for _ in range(25):
        customer = random.choice(customers)
        product, price = random.choice(products)
        quantity = random.randint(1, 5)
        order_date = (start_date + timedelta(days=random.randint(0, 30))).isoformat()
        rows.append((customer, product, quantity, price, order_date))

    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO orders (customer_name, product, quantity, unit_price, order_date)
        VALUES (?, ?, ?, ?, ?);
        """,
        rows,
    )
    conn.commit()
