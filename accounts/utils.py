from ipware import get_client_ip as ipware_get_client_ip


def get_client_ip(request):
    """
    Extracts the true client IP address from request headers (such as X-Forwarded-For
    set by Nginx/reverse proxy) using python-ipware, falling back to REMOTE_ADDR.
    """
    client_ip, _ = ipware_get_client_ip(request)
    if client_ip:
        return str(client_ip)
    return request.META.get("REMOTE_ADDR")
