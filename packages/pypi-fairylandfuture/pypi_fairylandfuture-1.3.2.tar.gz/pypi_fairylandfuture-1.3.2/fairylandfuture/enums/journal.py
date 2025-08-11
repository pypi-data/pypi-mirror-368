# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-08-18 00:56:51 UTC+08:00
"""

from fairylandfuture.core.superclass.enumerate import BaseEnum


class LogLevelEnum(BaseEnum):
    """
    Log level Enum.
    """

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @property
    def value(self) -> str:
        return super().value
