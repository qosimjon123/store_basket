from rest_framework import pagination
from rest_framework.response import Response
from urllib.parse import urlparse, parse_qs

def checkUrl(url):
    if url is None:
        return None

    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    page = query_params.get('page', [None])[0]
    return int(page) if page is not None else None



class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': checkUrl(self.get_next_link()),
                'previous': checkUrl(self.get_previous_link())
            },
            'count': self.page.paginator.num_pages,
            'results': data
        })