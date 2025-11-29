from rest_framework.pagination import CursorPagination


class PhotoCursorPagination(CursorPagination):
    """
    Cursor-based pagination for photos.
    
    Provides efficient pagination for large photo collections without
    exposing the total count or requiring offset calculations.
    
    Query Parameters:
    - cursor: The pagination cursor (provided in response)
    - page_size: Number of items per page (default: 20, max: 100)
    
    Example:
        GET /api/photos/?page_size=50
        GET /api/photos/?cursor=cD0yMDIxLTAxLTAxVDAwOjAwOjAwWg%3D%3D
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_size_query_description = 'Number of results to return per page'
    max_page_size = 100
    cursor_query_param = 'cursor'
    cursor_query_description = 'The pagination cursor'
    ordering = '-created_at'
    template = 'rest_framework/pagination/numbers.html'
