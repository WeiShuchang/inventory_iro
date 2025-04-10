from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

class AdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Redirect unauthenticated users trying to access admin paths
        if request.path.startswith('/administrator'):
            if not request.user.is_authenticated:
                return redirect('landing_url')  # Redirect to landing page
            elif not request.user.is_staff:
                return redirect('landing_url')  # Redirect non-admin users

        return self.get_response(request)

class PreventBackHistoryMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        """
        Add headers to prevent browser caching and enable no-store behavior,
        similar to Laravel's middleware.
        """
        response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 'Sat, 26 Jul 1997 05:00:00 GMT'  # Expire in the past

        return response
    
class AdminLoginRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_path = reverse('login_url')  # Replace 'login_url' with your login view name

        if request.path == login_path:
            if request.user.is_authenticated and request.user.is_staff:
                return redirect('administrator_dashboard')  # Replace with your admin dashboard URL name

        return self.get_response(request)

