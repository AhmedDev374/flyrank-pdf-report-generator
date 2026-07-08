from app.database import get_db_connection


def get_all_orders():
    """Queries the application data that will be rendered into the report."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, customer_name, product, quantity, unit_price, order_date
        FROM orders
        ORDER BY order_date ASC;
        """
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_summary():
    """Derives summary figures from the queried data."""
    orders = get_all_orders()
    total_orders = len(orders)
    total_revenue = sum(o["quantity"] * o["unit_price"] for o in orders)
    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
    }
