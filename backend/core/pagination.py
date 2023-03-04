from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Постраничная пагинация.
    Количество элементов на странице задается через параметр запроса limit.
    """
    page_size_query_param = 'limit'
