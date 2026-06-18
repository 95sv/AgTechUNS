import math


def paginar(items: list, page: int, limit: int) -> dict:
    total = len(items)
    total_pages = max(1, math.ceil(total / limit))
    start = (page - 1) * limit
    return {
        "data": items[start: start + limit],
        "pagination": {"page": page, "limit": limit, "total": total, "total_pages": total_pages},
    }
