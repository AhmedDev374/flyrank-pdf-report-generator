import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "reports"))
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_report_file(report_id: str, orders: list, summary: dict) -> str:
    """Renders the previously-queried data into a PDF file on disk and
    returns the path to the generated artifact."""
    file_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Orders Report", styles["Title"]))
    elements.append(
        Paragraph(f"Generated at: {datetime.utcnow().isoformat()} UTC", styles["Normal"])
    )
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph(f"Total Orders: {summary['total_orders']}", styles["Normal"]))
    elements.append(
        Paragraph(f"Total Revenue: ${summary['total_revenue']:.2f}", styles["Normal"])
    )
    elements.append(Spacer(1, 0.3 * inch))

    table_data = [["ID", "Customer", "Product", "Qty", "Unit Price", "Order Date"]]
    for order in orders:
        table_data.append(
            [
                str(order["id"]),
                order["customer_name"],
                order["product"],
                str(order["quantity"]),
                f"${order['unit_price']:.2f}",
                order["order_date"],
            ]
        )

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
            ]
        )
    )
    elements.append(table)

    doc.build(elements)
    return file_path
