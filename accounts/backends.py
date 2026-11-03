from axes.backends import AxesBackend as BaseAxesBackend

from accounts.utils import get_client_ip


class AxesBackend(BaseAxesBackend):
    """
    Custom AxesBackend that gracefully handles authentication calls where
    `request` is None (such as programmatic test client logins), and ensures
    request axes metadata is populated for signal handlers like `user_logged_in`.
    """

    def authenticate(self, request=None, username=None, password=None, **kwargs):
        if request is None:
            return None

        if not hasattr(request, "axes_ip_address"):
            request.axes_ip_address = get_client_ip(request)
            request.axes_user_agent = request.META.get("HTTP_USER_AGENT", "<unknown>")[:255]
            request.axes_path_info = request.META.get("PATH_INFO", "<unknown>")[:255]
            request.axes_http_accept = request.META.get("HTTP_ACCEPT", "<unknown>")[:1025]
            request.axes_attempt_time = None

        return super().authenticate(request=request, username=username, password=password, **kwargs)
