from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.analytics_service import AnalyticsService
from app.services.data_processor import DataProcessor
from app.models.sale import Sale

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_executive_summary():
    """
    Get executive KPI summary: Total Revenue, Profit, Cost, Margin %, Orders, Units, AOV.
    Filters: start_date, end_date, region
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    region = request.args.get("region")

    kpis = AnalyticsService.get_summary_kpis(start_date=start_date, end_date=end_date, region=region)
    return jsonify({
        "success": True,
        "data": kpis
    }), 200


@analytics_bp.route("/products/top", methods=["GET"])
@jwt_required()
def get_top_products():
    """
    Get top-selling products ranked by revenue, units_sold, or profit.
    Query params: limit (default 10), order_by (revenue|units_sold|profit|orders), start_date, end_date, category
    """
    limit = int(request.args.get("limit", 10))
    order_by = request.args.get("order_by", "revenue")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    category = request.args.get("category")

    results = AnalyticsService.get_top_products(
        limit=limit, order_by=order_by, start_date=start_date, end_date=end_date, category=category
    )
    return jsonify({
        "success": True,
        "count": len(results),
        "data": results
    }), 200


@analytics_bp.route("/products/categories", methods=["GET"])
@jwt_required()
def get_category_performance():
    """Get sales and margin breakdown by product category."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    results = AnalyticsService.get_category_performance(start_date=start_date, end_date=end_date)
    return jsonify({
        "success": True,
        "data": results
    }), 200


@analytics_bp.route("/regions", methods=["GET"])
@jwt_required()
def get_regional_breakdown():
    """Get sales, profit, and revenue contribution percentages by sales region."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    results = AnalyticsService.get_regional_performance(start_date=start_date, end_date=end_date)
    return jsonify({
        "success": True,
        "data": results
    }), 200


@analytics_bp.route("/trends/monthly", methods=["GET"])
@jwt_required()
def get_monthly_growth_trends():
    """Get chronological monthly sales trends with Month-over-Month (MoM) % growth."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    results = AnalyticsService.get_monthly_growth_trends(start_date=start_date, end_date=end_date)
    return jsonify({
        "success": True,
        "data": results
    }), 200


@analytics_bp.route("/trends/yearly", methods=["GET"])
@jwt_required()
def get_yearly_growth_trends():
    """Get chronological yearly sales trends with Year-over-Year (YoY) % growth."""
    results = AnalyticsService.get_yearly_growth_trends()
    return jsonify({
        "success": True,
        "data": results
    }), 200


@analytics_bp.route("/customers/top", methods=["GET"])
@jwt_required()
def get_top_customers():
    """Get highest value customers by total spend and transaction frequency."""
    limit = int(request.args.get("limit", 10))
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    results = AnalyticsService.get_top_customers(limit=limit, start_date=start_date, end_date=end_date)
    return jsonify({
        "success": True,
        "count": len(results),
        "data": results
    }), 200


@analytics_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_summary_statistics():
    """
    Get summary statistics (mean, median, standard deviation, quartiles, IQR)
    computed via Pandas and NumPy.
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    region = request.args.get("region")

    query = AnalyticsService.apply_sales_filters(
        Sale.query, start_date=start_date, end_date=end_date, region=region
    )
    stats = DataProcessor.compute_summary_statistics(query)
    return jsonify({
        "success": True,
        "data": stats
    }), 200
