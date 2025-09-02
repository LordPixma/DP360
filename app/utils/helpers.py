
def paginate(query, page: int = 1, per_page: int = 20):
    return query.limit(per_page).offset((page - 1) * per_page)
