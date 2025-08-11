# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-28 17:15:09 UTC+08:00
"""

from django.http import HttpRequest


class DjangoRequestToolkit:

    @classmethod
    def get_client_ip(cls, request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip

    @classmethod
    def get_user_agent(cls, request: HttpRequest) -> str:
        return request.META.get("HTTP_USER_AGENT", "")

    @classmethod
    def is_ajax_request(cls, request: HttpRequest) -> bool:
        return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

    @classmethod
    def build_absolute_uri(cls, request: HttpRequest, path: str) -> str:
        return request.build_absolute_uri(path)
