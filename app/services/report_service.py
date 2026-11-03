import io
import csv
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from app.models.sale import Sale
from app.services.analytics_service import AnalyticsService

class ReportService:
    """Generates multi-sheet Excel workbooks and streaming CSV exports."""

    @staticmethod
    def generate_csv_report(sales_query) -> io.StringIO:
        """Stream filtered sales records to CSV."""
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "Transaction ID", "Sale Date", "Customer Code", "Customer Name",
            "Product SKU", "Product Name", "Category", "Region",
            "Quantity", "Unit Price", "Unit Cost", "Discount",
            "Total Revenue", "Total Cost", "Total Profit", "Status", "Payment Method"
        ]
        writer.writerow(headers)

        # Iterate in chunks to support memory efficiency
        for sale in sales_query.yield_per(500):
            cust_name = sale.customer.name if sale.customer else ""
            cust_code = sale.customer.customer_code if sale.customer else ""
            prod_name = sale.product.name if sale.product else ""
            prod_sku = sale.product.sku if sale.product else ""
            prod_cat = sale.product.category if sale.product else ""

            writer.writerow([
                sale.transaction_id,
                sale.sale_date.isoformat(),
                cust_code,
                cust_name,
                prod_sku,
                prod_name,
                prod_cat,
                sale.region,
                sale.quantity,
                sale.unit_price,
                sale.unit_cost,
                sale.discount,
                sale.total_revenue,
                sale.total_cost,
                sale.total_profit,
                sale.status,
                sale.payment_method,
            ])

        output.seek(0)
        return output

    @classmethod
    def generate_excel_workbook(cls, start_date=None, end_date=None, region=None) -> io.BytesIO:
        """
        Builds a styled multi-tab corporate Excel report:
        1. Executive Summary
        2. Monthly Growth Trends
        3. Regional Performance
        4. Product Catalog Performance
        5. Detailed Transactions
        """
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # Style definitions
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")  # Navy Blue
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
        bold_font = Font(name="Calibri", size=11, bold=True)
        thin_border = Border(
            left=Side(style="thin", color="E5E7EB"),
            right=Side(style="thin", color="E5E7EB"),
            top=Side(style="thin", color="E5E7EB"),
            bottom=Side(style="thin", color="E5E7EB")
        )

        def style_header_row(ws, row_idx=1):
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_idx, column=col)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        def autofit_columns(ws):
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value is not None:
                        max_len = max(max_len, len(str(cell.value)))
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # ----------------------------------------------------
        # Sheet 1: Executive Summary
        # ----------------------------------------------------
        ws1 = wb.create_sheet(title="Executive Summary")
        ws1.views.sheetView[0].showGridLines = True
        kpis = AnalyticsService.get_summary_kpis(start_date=start_date, end_date=end_date, region=region)

        ws1["A1"] = "Executive Sales & BI Summary Report"
        ws1["A1"].font = title_font
        ws1["A2"] = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws1["A2"].font = Font(italic=True, color="6B7280")

        summary_rows = [
            ("Metric", "Value"),
            ("Total Gross Revenue", f"${kpis['total_revenue']:,.2f}"),
            ("Total Cost of Goods Sold", f"${kpis['total_cost']:,.2f}"),
            ("Total Net Profit", f"${kpis['total_profit']:,.2f}"),
            ("Gross Profit Margin", f"{kpis['gross_profit_margin_percent']:.2f}%"),
            ("Total Units Sold", f"{kpis['total_units_sold']:,}"),
            ("Total Transactions Processed", f"{kpis['total_orders']:,}"),
            ("Average Order Value (AOV)", f"${kpis['average_order_value']:,.2f}"),
        ]

        for r_idx, (m_label, m_val) in enumerate(summary_rows, start=4):
            c1 = ws1.cell(row=r_idx, column=1, value=m_label)
            c2 = ws1.cell(row=r_idx, column=2, value=m_val)
            if r_idx == 4:
                c1.fill = header_fill
                c1.font = header_font
                c2.fill = header_fill
                c2.font = header_font
            else:
                c1.font = bold_font
                c1.border = thin_border
                c2.border = thin_border
                c2.alignment = Alignment(horizontal="right")

        autofit_columns(ws1)

        # ----------------------------------------------------
        # Sheet 2: Monthly Trends
        # ----------------------------------------------------
        ws2 = wb.create_sheet(title="Monthly Trends")
        ws2.views.sheetView[0].showGridLines = True
        monthly_data = AnalyticsService.get_monthly_growth_trends(start_date=start_date, end_date=end_date)

        m_headers = ["Period", "Year", "Month", "Revenue ($)", "Profit ($)", "Units Sold", "Orders", "MoM Revenue Growth (%)", "MoM Profit Growth (%)", "Margin (%)"]
        ws2.append(m_headers)
        style_header_row(ws2, 1)

        for row in monthly_data:
            ws2.append([
                row["period"], row["year"], row["month"],
                row["revenue"], row["profit"], row["units_sold"],
                row["order_count"], row["mom_revenue_growth_percent"],
                row["mom_profit_growth_percent"], row["profit_margin_percent"]
            ])
            for col_idx in range(1, 11):
                ws2.cell(row=ws2.max_row, column=col_idx).border = thin_border

        autofit_columns(ws2)

        # ----------------------------------------------------
        # Sheet 3: Regional Breakdown
        # ----------------------------------------------------
        ws3 = wb.create_sheet(title="Regional Performance")
        ws3.views.sheetView[0].showGridLines = True
        reg_data = AnalyticsService.get_regional_performance(start_date=start_date, end_date=end_date)

        r_headers = ["Region", "Revenue ($)", "Profit ($)", "Units Sold", "Orders", "Revenue Share (%)", "Profit Margin (%)"]
        ws3.append(r_headers)
        style_header_row(ws3, 1)

        for row in reg_data:
            ws3.append([
                row["region"], row["total_revenue"], row["total_profit"],
                row["units_sold"], row["order_count"],
                row["revenue_share_percent"], row["profit_margin_percent"]
            ])
            for col_idx in range(1, 8):
                ws3.cell(row=ws3.max_row, column=col_idx).border = thin_border

        autofit_columns(ws3)

        # ----------------------------------------------------
        # Sheet 4: Product Performance
        # ----------------------------------------------------
        ws4 = wb.create_sheet(title="Top Products")
        ws4.views.sheetView[0].showGridLines = True
        prod_data = AnalyticsService.get_top_products(limit=50, start_date=start_date, end_date=end_date)

        p_headers = ["SKU", "Product Name", "Category", "Revenue ($)", "Profit ($)", "Units Sold", "Orders", "Margin (%)"]
        ws4.append(p_headers)
        style_header_row(ws4, 1)

        for row in prod_data:
            ws4.append([
                row["sku"], row["name"], row["category"],
                row["total_revenue"], row["total_profit"],
                row["units_sold"], row["order_count"],
                row["profit_margin_percent"]
            ])
            for col_idx in range(1, 9):
                ws4.cell(row=ws4.max_row, column=col_idx).border = thin_border

        autofit_columns(ws4)

        # ----------------------------------------------------
        # Sheet 5: Raw Transactions (Sample or Filtered)
        # ----------------------------------------------------
        ws5 = wb.create_sheet(title="Sales Transactions")
        ws5.views.sheetView[0].showGridLines = True
        t_headers = ["Transaction ID", "Date", "Customer Code", "Customer Name", "Product SKU", "Product Name", "Region", "Qty", "Price ($)", "Discount", "Revenue ($)", "Profit ($)", "Status"]
        ws5.append(t_headers)
        style_header_row(ws5, 1)

        tx_query = AnalyticsService.apply_sales_filters(
            Sale.query, start_date=start_date, end_date=end_date, region=region
        ).order_by(Sale.sale_date.desc()).limit(1000)

        for s in tx_query.all():
            ws5.append([
                s.transaction_id, s.sale_date.isoformat(),
                s.customer.customer_code if s.customer else "",
                s.customer.name if s.customer else "",
                s.product.sku if s.product else "",
                s.product.name if s.product else "",
                s.region, s.quantity, s.unit_price, s.discount,
                s.total_revenue, s.total_profit, s.status
            ])
            for col_idx in range(1, 14):
                ws5.cell(row=ws5.max_row, column=col_idx).border = thin_border

        autofit_columns(ws5)

        # Save into in-memory stream
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output
