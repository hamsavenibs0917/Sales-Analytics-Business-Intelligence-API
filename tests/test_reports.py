import io
import openpyxl
from datetime import date
from app.extensions import db
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale

def setup_report_data():
    """Seed sample data for report generation."""
    c = Customer(customer_code="CUST-REP-1", name="Report Customer", region="Central", segment="Enterprise")
    p = Product(sku="SKU-REP-1", name="Report Product", category="Office Supplies", unit_cost=30.0, unit_price=70.0)
    db.session.add_all([c, p])
    db.session.commit()

    s = Sale(
        transaction_id="TX-REP-1", customer_id=c.id, product_id=p.id,
        quantity=10, unit_price=70.0, unit_cost=30.0, discount=0.0,
        sale_date=date(2026, 3, 1), region="Central", payment_method="Credit Card", status="Completed"
    )
    s.calculate_totals()
    db.session.add(s)
    db.session.commit()


def test_export_csv(client, user_headers):
    """Test exporting sales records as a CSV stream."""
    setup_report_data()

    res = client.get("/api/v1/reports/export/csv", headers=user_headers)
    assert res.status_code == 200
    assert "text/csv" in res.content_type
    assert "attachment; filename=" in res.headers.get("Content-Disposition", "")
    content = res.data.decode("utf-8")
    assert "Transaction ID" in content
    assert "TX-REP-1" in content
    assert "Report Customer" in content


def test_export_excel_workbook(client, user_headers):
    """Test exporting styled multi-sheet Excel workbook."""
    setup_report_data()

    res = client.get("/api/v1/reports/export/excel", headers=user_headers)
    assert res.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res.content_type
    assert "attachment; filename=" in res.headers.get("Content-Disposition", "")

    # Parse in-memory Excel file to verify valid openpyxl workbook structure
    wb = openpyxl.load_workbook(io.BytesIO(res.data))
    sheet_names = wb.sheetnames
    assert "Executive Summary" in sheet_names
    assert "Monthly Trends" in sheet_names
    assert "Regional Performance" in sheet_names
    assert "Top Products" in sheet_names
    assert "Sales Transactions" in sheet_names

    summary_sheet = wb["Executive Summary"]
    assert summary_sheet["A1"].value == "Executive Sales & BI Summary Report"
