from rest_framework.pagination import PageNumberPagination


class ComputationsPagination(PageNumberPagination):
    page_size = 10
