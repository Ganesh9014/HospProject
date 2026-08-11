from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import logout


class AutoLogoutMiddleware:
    """
    Logs out users after a period of inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip anonymous users
        if not request.user.is_authenticated:
            return self.get_response(request)

        timeout = getattr(settings, 'AUTO_LOGOUT_DELAY', 500)

        last_activity = request.session.get('last_activity')

        if last_activity:
            elapsed_time = (
                timezone.now() - timezone.datetime.fromisoformat(last_activity)
            ).total_seconds()

            if elapsed_time > timeout:
                logout(request)
                request.session.flush()
                return redirect('login')

        request.session['last_activity'] = timezone.now().isoformat()
        return self.get_response(request)


# hospApp/middleware.py — add this new middleware
from django.http import HttpResponse


class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response