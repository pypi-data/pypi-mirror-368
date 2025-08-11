# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-08-18 00:56:07 UTC+08:00
"""

from fairylandfuture.core.superclass.enumerate import BaseEnum


class EncodingEnum(BaseEnum):
    """
    Encoding enum.
    """

    UTF8 = "UTF-8"
    GBK = "GBK"
    GB2312 = "GB2312"
    GB18030 = "GB18030"

    @property
    def value(self) -> str:
        return super().value
