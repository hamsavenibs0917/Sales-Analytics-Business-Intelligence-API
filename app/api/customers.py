from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.customer import Customer
from app.schemas.customer_schema import CustomerSchema, CustomerUpdateSchema
from app.utils.decorators import role_required, validate_payload
from app.utils.exceptions import ResourceNotFoundError, ConflictError
from app.utils.pagination import paginate_query

customers_bp = Blueprint("customers", __name__)
customer_schema = CustomerSchema()
customer_list_schema = CustomerSchema(many=True)

@customers_bp.route("", methods=["GET"])
@jwt_required()
def list_customers():
    """List customers with pagination and filtering."""
    query = Customer.query

    search = request.args.get("search")
    if search:
        query = query.filter(
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.customer_code.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )

    region = request.args.get("region")
    if region:
        query = query.filter(Customer.region.ilike(f"%{region}%"))

    segment = request.args.get("segment")
    if segment:
        query = query.filter(Customer.segment.ilike(segment))

    query = query.order_by(Customer.created_at.desc())
    result = paginate_query(query, schema=customer_list_schema)
    result["success"] = True
    return jsonify(result), 200


@customers_bp.route("", methods=["POST"])
@jwt_required()
@validate_payload(CustomerSchema)
def create_customer():
    """Create a new customer profile."""
    data = g.validated_data
    if Customer.query.filter_by(customer_code=data["customer_code"]).first():
        raise ConflictError(f"Customer code '{data['customer_code']}' already exists.")

    customer = Customer(**data)
    db.session.add(customer)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Customer created successfully.",
        "customer": customer.to_dict()
    }), 201


@customers_bp.route("/<int:customer_id>", methods=["GET"])
@jwt_required()
def get_customer(customer_id):
    """Retrieve customer by ID."""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        raise ResourceNotFoundError("Customer", customer_id)

    return jsonify({
        "success": True,
        "customer": customer.to_dict()
    }), 200


@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@jwt_required()
@validate_payload(CustomerUpdateSchema)
def update_customer(customer_id):
    """Update customer details."""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        raise ResourceNotFoundError("Customer", customer_id)

    data = g.validated_data
    for field, val in data.items():
        if val is not None:
            setattr(customer, field, val)

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Customer updated successfully.",
        "customer": customer.to_dict()
    }), 200


@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@role_required(["admin"])
def delete_customer(customer_id):
    """Delete customer and related sales (Admin only)."""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        raise ResourceNotFoundError("Customer", customer_id)

    db.session.delete(customer)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Customer {customer_id} successfully deleted."
    }), 200
