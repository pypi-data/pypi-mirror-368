# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-08-18 01:05:53 UTC+08:00
"""

import time

from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from dateutil.relativedelta import relativedelta

from fairylandfuture.enums.chron import DateTimeEnum, TimeZoneEnum
from fairylandfuture.toolkit.tools.validator.validators import ParamsValidator
from fairylandfuture.core.superclass.validators import Validator


class DateTimeToolkit:
    """
    Data and time module
    """

    TIMEZONE: str = TimeZoneEnum.Shanghai.value

    @classmethod
    def date(cls, _format: Optional[str] = None) -> str:
        """
        Get the current date.

        :param _format: Date format.
        :type _format: str
        :return: Current date
        :rtype: str
        """
        if not _format:
            _format = DateTimeEnum.DATE.value

        return datetime.now().date().strftime(_format)

    @classmethod
    def date_shanghai(cls, _format: Optional[str] = None) -> str:
        """
        Get the current date in shanghai time zone.

        :param _format: Date format.
        :type _format: str
        :return: Current date in shanghai time zone.
        :rtype: str
        """
        if not _format:
            _format = DateTimeEnum.DATE.value

        return datetime.now(tz=timezone(timedelta(hours=8), name=cls.TIMEZONE)).date().strftime(_format)

    @classmethod
    def time(cls, _fromat: Optional[str] = None) -> str:
        """
        Get the current time.

        :param _fromat: Time format.
        :type _fromat: str
        :return: Current time
        :rtype: str
        """
        if not _fromat:
            _fromat = DateTimeEnum.TIME.value

        return datetime.now().time().strftime(_fromat)

    @classmethod
    def time_shanghai(cls, _fromat: Optional[str] = None) -> str:
        """
        Get the current time in shanghai time zone.

        :param _fromat: Time format.
        :type _fromat: str
        :return: Current time in shanghai time zone.
        :rtype: str
        """
        if not _fromat:
            _fromat = DateTimeEnum.TIME.value

        return datetime.now(tz=timezone(timedelta(hours=8), name=cls.TIMEZONE)).time().strftime(_fromat)

    @classmethod
    def datetime(cls, _format: Optional[str] = None) -> str:
        """
        Get the current datetime_str.

        :param _format: Datetime format.
        :type _format: str
        :return: Current datetime_str
        :rtype: str
        """
        if not _format:
            _format = DateTimeEnum.DATETIME.value

        return datetime.now().strftime(_format)

    @classmethod
    def datetime_shanghai(cls, _format: Optional[str] = None) -> str:
        """
        Get the current datetime_str in shanghai time zone.

        :param _format: Datetime format.
        :type _format: str
        :return: Current datetime_str in shanghai time zone.
        :rtype: str
        """
        if not _format:
            _format = DateTimeEnum.DATETIME.value

        return datetime.now(tz=timezone(timedelta(hours=8), name=cls.TIMEZONE)).strftime(_format)

    @classmethod
    def timestamp(cls, ms: bool = False, n: Optional[int] = None) -> int:
        """
        Get the current timestamp.

        :return: Current timestamp.
        :rtype: int
        """
        validator = ParamsValidator(
            {
                "ms": Validator(required=False, typedef=bool),
                "n": Validator(required=False, typedef=(int, type(None)))
            }
        )
        validator.validate({"ms": ms, "n": n})

        if ms:
            return round(time.time() * 1000)
        if n:
            return round(time.time()) * (10 ** (n - 10))

        return round(time.time())

    @classmethod
    def timestamp_to_datetime(cls, timestamp: Union[int, float], _format: Optional[str] = None) -> str:
        """
        Convert timestamp to datetime_str.

        :param timestamp: Timestamp.
        :type timestamp: int or float
        :param _format: Datetime format.
        :type _format: str
        :return: Formatted datetime_str string.
        :rtype: str
        """
        validator = ParamsValidator(
            {
                "timestamp": Validator(required=True, typedef=(int, float)),
            }
        )
        validator.validate({"timestamp": timestamp})

        if len(str(int(timestamp))) == 13:
            timestamp /= 1000

        if not _format:
            _format = DateTimeEnum.DATETIME.value

        return datetime.fromtimestamp(timestamp).strftime(_format)

    @classmethod
    def datetime_to_timestamp(cls, dt_string: str, ms: bool = False, n: Optional[int] = None, _format: Optional[str] = None) -> int:
        """
        Convert datetime to timestamp.

        :param dt_string: Datetime string.
        :type dt_string: str
        :param ms: Whether to include mss.
        :type ms: bool
        :param n: Number of decimal places for the timestamp.
        :type n: int or None
        :param _format: Datetime format.
        :type _format: str
        :return: Timestamp.
        :rtype: int
        """
        validator = ParamsValidator(
            {
                "dt_string": Validator(required=True, typedef=str),
                "ms": Validator(required=False, typedef=bool),
                "n": Validator(required=False, typedef=(int, type(None))),
                "_format": Validator(required=False, typedef=(str, type(None)))
            }
        )
        validator.validate({"dt_string": dt_string, "ms": ms, "n": n, "_format": _format})

        if not _format:
            _format = DateTimeEnum.DATETIME.value

        timestamp = datetime.strptime(dt_string, _format).timestamp()

        if ms:
            return int(timestamp * 1000)
        if n:
            return int(timestamp * (10 ** (n - 10)))

        return int(timestamp)

    @classmethod
    def yesterday(cls, _format: Optional[str] = None) -> str:
        """
        Get yesterday's date.

        :param _format: Date format.
        :type _format: str
        :return: Yesterday's date.
        :rtype: str
        """
        if not _format:
            _format = DateTimeEnum.DATE.value

        return (datetime.now() - relativedelta(days=1)).strftime(_format)

    @classmethod
    def tomorrow(cls, _format: Optional[str] = None) -> str:
        """
        Get tomorrow's date.

        :param _format: Date format.
        :type _format: str
        :return: Tomorrow's date.
        :rtype: str
        """
        if not _format:
            _format = DateTimeEnum.DATE.value

        return (datetime.now() + relativedelta(days=1)).strftime(_format)

    @classmethod
    def daysdelta(cls, dt1: Union[str, int, float], dt2: Union[str, int, float], timestamp: bool = False, ms: bool = False, _format: Optional[str] = None) -> int:
        """
        Calculate the number of days between two dates.

        :param dt1: Datetime_str or timestamp of the first date.
        :type dt1: str or int or float
        :param dt2: Datetime_str or timestamp of the second date.
        :type dt2: str or int or float
        :param timestamp: Is timestamp or datetime_str.
        :type timestamp: bool
        :param ms: Is ms or not.
        :type ms: bool
        :param _format: Datetime_str format.
        :type _format: str
        :return: Days delta.
        :rtype: int
        """
        if not _format:
            _format = DateTimeEnum.DATE.value

        if timestamp:
            if ms:
                date1 = datetime.fromtimestamp(dt1 / 1000)
                date2 = datetime.fromtimestamp(dt2 / 1000)
            else:
                date1 = datetime.fromtimestamp(dt1)
                date2 = datetime.fromtimestamp(dt2)
        else:
            date1 = datetime.strptime(dt1, _format)
            date2 = datetime.strptime(dt2, _format)

        return abs((date2 - date1).days)

    @classmethod
    def unzone_utc(cls) -> datetime:
        """
        Remove the timezone from the current datetime.

        :return: Unzoned datetime.
        :rtype: datetime
        """
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @classmethod
    def unzone_cst(cls) -> datetime:
        """
        Remove the timezone from the current datetime in China.

        :return: Unzoned datetime in China.
        :rtype: datetime
        """
        return datetime.now(tz=timezone(timedelta(hours=8), name=cls.TIMEZONE)).replace(tzinfo=None)


