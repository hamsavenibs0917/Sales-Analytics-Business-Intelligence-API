from flask import request, current_app

def get_pagination_params():
    """Extract and validate page and per_page query parameters."""
    try:
        page = int(request.args.get("page", current_app.config.get("DEFAULT_PAGE", 1)))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    try:
        per_page = int(request.args.get("per_page", current_app.config.get("DEFAULT_PER_PAGE", 20)))
        max_per_page = current_app.config.get("MAX_PER_PAGE", 100)
        if per_page < 1:
            per_page = 1
        elif per_page > max_per_page:
            per_page = max_per_page
    except (ValueError, TypeError):
        per_page = 20

    return page, per_page


def paginate_query(query, schema=None, transform=None):
    """
    Execute pagination on a SQLAlchemy query and return a structured dictionary.
    
    :param query: SQLAlchemy Query object
    :param schema: Marshmallow Schema instance (with many=True) for serialization
    :param transform: Optional lambda or callable to transform each entity
    """
    page, per_page = get_pagination_params()
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    if schema:
        items = schema.dump(paginated.items)
    elif transform:
        items = [transform(item) for item in paginated.items]
    else:
        items = [item.to_dict() if hasattr(item, "to_dict") else item for item in paginated.items]

    return {
        "items": items,
        "pagination": {
            "page": paginated.page,
            "per_page": paginated.per_page,
            "total_items": paginated.total,
            "total_pages": paginated.pages,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev,
        }
    }
