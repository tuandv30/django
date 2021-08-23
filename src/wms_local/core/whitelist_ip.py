import os
from functools import wraps
from rest_framework.response import Response


DEPLOY_ENV = os.environ.get("DEPLOY_ENV")


def check_whitelist(list_ip_address):
    """This decorator check HTTP_X_REAL_IP is in whitelist
    Args:
        list_ip_address ([str]): Whitelist IP Address
    """

    def inner_function(view_func):
        @wraps(view_func)
        def authorize(request, *args, **kwargs):
            if not list_ip_address or list_ip_address == ["*"] or not DEPLOY_ENV == "production":
                return view_func(request, *args, **kwargs)
            real_client_ip = request.META.get("HTTP_X_REAL_IP")
            if not real_client_ip:
                return view_func(request, *args, **kwargs)
            for valid_ip in list_ip_address:
                if real_client_ip == valid_ip or real_client_ip.startswith(
                        valid_ip):
                    return view_func(request, *args, **kwargs)
            response = "Invalid IP Address Access"
            return Response(status=401, data=response,
                            content_type='application/json')

        return authorize
    return inner_function
