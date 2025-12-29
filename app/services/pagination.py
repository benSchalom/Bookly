from flask import request
# ecrit par l'iA
def paginate(query, page=None, per_page=None):
    """
    Pagine une query SQLAlchemy
    
    Args:
        query: Query SQLAlchemy
        page: Numéro de page (défaut depuis request.args)
        per_page: Items par page (défaut depuis request.args)
    
    Returns:
        dict avec items, total, page, pages, has_next, has_prev
    """
    # Récupérer params si pas fournis
    if page is None:
        page = request.args.get('page', 1, type=int)
    if per_page is None:
        per_page = request.args.get('per_page', 20, type=int)
    
    # Limites
    page = max(1, page)  # Minimum page 1
    per_page = min(max(1, per_page), 100)  # Entre 1 et 100
    
    # Paginer
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }