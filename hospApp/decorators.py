# hospApp/decorators.py

from functools import wraps

def page_view(view_func):
    """
    Marks a view as a PAGE VIEW.
    Only page views will be permission-checked by middleware.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        request.is_page_view = True
        return view_func(request, *args, **kwargs)
    return wrapper
