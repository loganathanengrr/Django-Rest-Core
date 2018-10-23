from rest_framework import pagination

class ProjectAPIPagination(pagination.LimitOffsetPagination):
    default_limit   = 15
    max_limit       = 20

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000