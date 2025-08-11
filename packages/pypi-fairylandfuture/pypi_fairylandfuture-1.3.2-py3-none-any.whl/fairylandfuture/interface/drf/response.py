# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-27 15:51:45 UTC+08:00
"""

import typing as t

from rest_framework.response import Response

from fairylandfuture.structures.http.response import ResponseStructure, ResponseFrozenStructure


class DRFResponseMixin:

    def _response(
        self,
        data: t.Union[ResponseStructure, ResponseFrozenStructure],
        headers: t.Optional[t.Dict[str, t.Any]] = None,
        content_type: t.Optional[str] = None,
        exception: bool = False,
    ):
        if not isinstance(data, (ResponseStructure, ResponseFrozenStructure)):
            raise TypeError("data must be an instance of ResponseStructure or ResponseFrozenStructure")

        if not content_type:
            content_type = "application/json"

        return Response(data=data.asdict, status=data.code, headers=headers, content_type=content_type, exception=exception)
