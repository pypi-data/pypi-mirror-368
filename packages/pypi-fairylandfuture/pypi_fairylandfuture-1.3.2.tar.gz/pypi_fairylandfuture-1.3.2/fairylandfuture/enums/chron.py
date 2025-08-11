# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-08-18 00:55:09 UTC+08:00
"""

from fairylandfuture.core.superclass.enumerate import BaseEnum


class DateTimeEnum(BaseEnum):
    """
    Date time enum.
    """

    DATE = "%Y-%m-%d"
    TIME = "%H:%M:%S"
    DATETIME = "%Y-%m-%d %H:%M:%S"

    DATE_CN = "%Y年%m月%d日"
    TIME_CN = "%H时%M分%S秒"
    DATETIME_CN = "%Y年%m月%d日 %H时%M分%S秒"

    @property
    def value(self) -> str:
        return super().value


class TimeZoneEnum(BaseEnum):
    """
    Time zone enum.
    """

    Shanghai = "Asia/Shanghai"
    Beiing = "Asia/Shanghai"
    Singapore = "Asia/Singapore"

    @property
    def value(self) -> str:
        return super().value
