from datetime import datetime
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from app.extensions import db
from app.models.sale import Sale
from app.models.customer import Customer
from app.models.product import Product
from app.schemas.sale_schema import SaleCreateSchema, SaleUpdateSchema
from app.services.data_processor import DataProcessor
from app.utils.decorators import role_required, validate_payload
from app.utils.exceptions import ResourceNotFoundError, ConflictError, ValidationError, FileProcessingError
from app.utils.pagination import paginate_query

sales_bp = Blueprint("sales", __name__)

@sales_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def list_sales():
    """
    List sales records with pagination and multi-parameter filtering.
    Filters: start_date, end_date, region, product_id, customer_id, status, min_amount, max_amount, sort_by, order
    """
    query = Sale.query

    # Apply date filters
    start_date = request.args.get("start_date")
    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Sale.sale_date >= parsed_start)
        except ValueError:
            raise ValidationError("Invalid start_date format. Expected YYYY-MM-DD.")

    end_date = request.args.get("end_date")
    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Sale.sale_date <= parsed_end)
        except ValueError:
            raise ValidationError("Invalid end_date format. Expected YYYY-MM-DD.")

    # Apply category/region/status filters
    region = request.args.get("region")
    if region:
        query = query.filter(Sale.region.ilike(f"%{region}%"))

    status = request.args.get("status")
    if status:
        query = query.filter(Sale.status.ilike(status))

    customer_id = request.args.get("customer_id")
    if customer_id:
        query = query.filter(Sale.customer_id == int(customer_id))

    product_id = request.args.get("product_id")
    if product_id:
        query = query.filter(Sale.product_id == int(product_id))

    # Numeric revenue filters
    min_amount = request.args.get("min_amount")
    if min_amount:
        query = query.filter(Sale.total_revenue >= float(min_amount))

    max_amount = request.args.get("max_amount")
    if max_amount:
        query = query.filter(Sale.total_revenue <= float(max_amount))

    # Sorting
    sort_by = request.args.get("sort_by", "sale_date")
    order = request.args.get("order", "desc").lower()

    sort_columns = {
        "sale_date": Sale.sale_date,
        "total_revenue": Sale.total_revenue,
        "total_profit": Sale.total_profit,
        "quantity": Sale.quantity,
        "created_at": Sale.created_at,
    }
    col = sort_columns.get(sort_by, Sale.sale_date)
    query = query.order_by(desc(col) if order == "desc" else asc(col))

    result = paginate_query(query, transform=lambda s: s.to_dict(include_relations=True))
    result["success"] = True
    return jsonify(result), 200


@sales_bp.route("", methods=["POST"])
@jwt_required()
@validate_payload(SaleCreateSchema)
def create_sale():
    """Create a single sales record with calculated revenue and profit."""
    data = g.validated_data

    # Check for duplicate transaction_id
    if Sale.query.filter_by(transaction_id=data["transaction_id"]).first():
        raise ConflictError(f"Transaction ID '{data['transaction_id']}' already exists.")

    customer = db.session.get(Customer, data["customer_id"])
    if not customer:
        raise ResourceNotFoundError("Customer", data["customer_id"])

    product = db.session.get(Product, data["product_id"])
    if not product:
        raise ResourceNotFoundError("Product", data["product_id"])

    user_id = get_jwt_identity()

    # Determine unit cost
    unit_cost = data.get("unit_cost")
    if unit_cost is None:
        unit_cost = product.unit_cost

    sale = Sale(
        transaction_id=data["transaction_id"],
        customer_id=customer.id,
        product_id=product.id,
        user_id=int(user_id) if user_id and str(user_id).isdigit() else None,
        quantity=data["quantity"],
        unit_price=data["unit_price"],
        unit_cost=unit_cost,
        discount=data.get("discount", 0.0),
        sale_date=data["sale_date"],
        region=data["region"],
        payment_method=data.get("payment_method", "Credit Card"),
        status=data.get("status", "Completed"),
    )
    sale.calculate_totals()

    db.session.add(sale)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Sales record created successfully.",
        "sale": sale.to_dict(include_relations=True)
    }), 201


@sales_bp.route("/<int:sale_id>", methods=["GET"])
@jwt_required()
def get_sale(sale_id):
    """Retrieve a single sales record by ID."""
    sale = db.session.get(Sale, sale_id)
    if not sale:
        raise ResourceNotFoundError("Sales record", sale_id)

    return jsonify({
        "success": True,
        "sale": sale.to_dict(include_relations=True)
    }), 200


@sales_bp.route("/<int:sale_id>", methods=["PUT"])
@jwt_required()
@validate_payload(SaleUpdateSchema)
def update_sale(sale_id):
    """Update a sales record and recalculate financial aggregates."""
    sale = db.session.get(Sale, sale_id)
    if not sale:
        raise ResourceNotFoundError("Sales record", sale_id)

    data = g.validated_data
    for field in ["quantity", "unit_price", "unit_cost", "discount", "sale_date", "region", "payment_method", "status"]:
        if field in data and data[field] is not None:
            setattr(sale, field, data[field])

    # Re-calculate totals based on updated values
    sale.calculate_totals()
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Sales record updated successfully.",
        "sale": sale.to_dict(include_relations=True)
    }), 200


@sales_bp.route("/<int:sale_id>", methods=["DELETE"])
@role_required(["admin"])
def delete_sale(sale_id):
    """Delete a sales record (Admin only)."""
    sale = db.session.get(Sale, sale_id)
    if not sale:
        raise ResourceNotFoundError("Sales record", sale_id)

    db.session.delete(sale)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Sales record {sale_id} successfully deleted."
    }), 200


@sales_bp.route("/upload", methods=["POST"])
@role_required(["admin", "analyst"])
def upload_sales():
    """
    Bulk upload sales dataset via CSV or Excel (.xlsx, .xls).
    Cleans data, detects duplicates, creates missing catalog entities, and bulk persists records.
    """
    if "file" not in request.files:
        raise ValidationError("No file uploaded. Please supply a 'file' parameter in form-data.")

    file = request.files["file"]
    if not file or file.filename == "":
        raise ValidationError("No file selected for upload.")

    user_id = get_jwt_identity()

    # Step 1: Read into DataFrame
    df = DataProcessor.read_file_to_dataframe(file)

    # Step 2: Clean and validate
    cleaned_df, stats = DataProcessor.clean_and_validate(df)

    # Step 3: Ingest and persist
    final_stats = DataProcessor.ingest_sales_dataframe(
        cleaned_df, stats, user_id=int(user_id) if user_id and str(user_id).isdigit() else None
    )

    return jsonify({
        "success": True,
        "message": "Sales dataset processed successfully.",
        "statistics": final_stats
    }), 200
