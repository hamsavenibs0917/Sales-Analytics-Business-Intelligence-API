from datetime import datetime
from flask import Blueprint, request, Response, send_file
from flask_jwt_extended import jwt_required
from app.models.sale import Sale
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/export/csv", methods=["GET"])
@jwt_required(optional=True)
def export_csv():
    """Export filtered sales data to CSV."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    region = request.args.get("region")
    status = request.args.get("status")

    query = AnalyticsService.apply_sales_filters(
        Sale.query, start_date=start_date, end_date=end_date, region=region, status=status
    ).order_by(Sale.sale_date.desc())

    csv_buffer = ReportService.generate_csv_report(query)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sales_report_{timestamp}.csv"

    return Response(
        csv_buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@reports_bp.route("/export/excel", methods=["GET"])
@jwt_required(optional=True)
def export_excel():
    """Export multi-tab executive BI report to Excel (.xlsx)."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    region = request.args.get("region")

    excel_buffer = ReportService.generate_excel_workbook(
        start_date=start_date, end_date=end_date, region=region
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sales_bi_report_{timestamp}.xlsx"

    return send_file(
        excel_buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )
