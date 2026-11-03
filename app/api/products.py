from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.product import Product
from app.schemas.product_schema import ProductSchema, ProductUpdateSchema
from app.utils.decorators import role_required, validate_payload
from app.utils.exceptions import ResourceNotFoundError, ConflictError
from app.utils.pagination import paginate_query

products_bp = Blueprint("products", __name__)
product_schema = ProductSchema()
product_list_schema = ProductSchema(many=True)

@products_bp.route("", methods=["GET"])
@jwt_required()
def list_products():
    """List products with pagination and filtering."""
    query = Product.query

    search = request.args.get("search")
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%"))
        )

    category = request.args.get("category")
    if category:
        query = query.filter(Product.category.ilike(category))

    is_active = request.args.get("is_active")
    if is_active is not None:
        active_bool = is_active.lower() in ["true", "1", "yes"]
        query = query.filter(Product.is_active == active_bool)

    query = query.order_by(Product.name.asc())
    result = paginate_query(query, schema=product_list_schema)
    result["success"] = True
    return jsonify(result), 200


@products_bp.route("", methods=["POST"])
@role_required(["admin", "analyst"])
@validate_payload(ProductSchema)
def create_product():
    """Create a new product in catalog."""
    data = g.validated_data
    if Product.query.filter_by(sku=data["sku"].upper()).first():
        raise ConflictError(f"Product SKU '{data['sku']}' already exists.")

    data["sku"] = data["sku"].upper()
    product = Product(**data)
    db.session.add(product)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Product created successfully.",
        "product": product.to_dict()
    }), 201


@products_bp.route("/<int:product_id>", methods=["GET"])
@jwt_required()
def get_product(product_id):
    """Retrieve product by ID."""
    product = db.session.get(Product, product_id)
    if not product:
        raise ResourceNotFoundError("Product", product_id)

    return jsonify({
        "success": True,
        "product": product.to_dict()
    }), 200


@products_bp.route("/<int:product_id>", methods=["PUT"])
@role_required(["admin", "analyst"])
@validate_payload(ProductUpdateSchema)
def update_product(product_id):
    """Update product details."""
    product = db.session.get(Product, product_id)
    if not product:
        raise ResourceNotFoundError("Product", product_id)

    data = g.validated_data
    for field, val in data.items():
        if val is not None:
            setattr(product, field, val)

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Product updated successfully.",
        "product": product.to_dict()
    }), 200


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@role_required(["admin"])
def delete_product(product_id):
    """Delete product from catalog (Admin only)."""
    product = db.session.get(Product, product_id)
    if not product:
        raise ResourceNotFoundError("Product", product_id)

    db.session.delete(product)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Product {product_id} successfully deleted."
    }), 200
