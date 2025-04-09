from django.http import HttpResponseForbidden
from functools import wraps

def admin_required(view_func):
    """
    Decorator to restrict access to users who are in the 'Admin' group.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is in the 'Admin' group
        if not request.user.groups.filter(name='Admin').exists():
            return HttpResponseForbidden("You are not allowed to view this page.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view