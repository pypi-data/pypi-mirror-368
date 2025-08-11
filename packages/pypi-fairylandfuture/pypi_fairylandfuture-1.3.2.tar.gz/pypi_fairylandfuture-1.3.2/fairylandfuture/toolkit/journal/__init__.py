# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-08-18 01:06:36 UTC+08:00
"""

import os
import sys
import threading
from importlib.resources import read_text
from typing import Optional

from loguru import logger

from fairylandfuture.enums.encode import EncodingEnum
from fairylandfuture.enums.journal import LogLevelEnum


class Journal(object):
    """
    A logging utility implemented as a singleton to ensure that only one instance
    handles logging across the application.

    :param dirname: Path to directory where log files are stored.
    :type dirname: str
    :param filename: Name of the log file.
    :type filename: str
    :param debug: Flag to set logging level to debug.
    :type debug: bool
    :param rotation: Log rotation size or time.
    :type rotation: str
    :param retention: Time period to retain old log files.
    :type retention: str
    :param formatting: Log message format.
    :type formatting: str or None
    :param compression: Compression format for rotated logs.
    :type compression: str
    :param encoding: Encoding for the log files.
    :type encoding: EncodingEnum
    :param level: Logging level for the file handler.
    :type level: LogLevelEnum
    :param serialize: Serialize log messages to JSON format.
    :type serialize: bool
    :param console: Flag to enable logging to console.
    :type console: bool
    :param console_level: Logging level for the console handler.
    :type console_level: LogLevelEnum
    :param console_format: Log message format for console.
    :type console_format: str or None
    :param clear_existing: Flag to clear existing log files.
    :type clear_existing: bool

    Usage::
        >>> # Create a journal instance
        >>> journal = Journal()
        >>>
        >>> # Log messages
        >>> journal.info("This is an info message")
        >>> journal.error("This is an error message")

    Note: This class uses `loguru` library for logging.
    The metaclass `SingletonMeta` ensures a single instance is used.
    """

    DEFAULT_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | P:{process} T:{thread} | {message}"

    def __init__(
        self,
        dirname: str = "logs",
        filename: str = "service.log",
        debug: bool = False,
        rotation: str = "5 MB",
        retention: str = "180 days",
        formatting: Optional[str] = None,
        compression: str = "gz",
        encoding: EncodingEnum = EncodingEnum.UTF8,
        level: LogLevelEnum = LogLevelEnum.INFO,
        serialize: bool = False,
        console: bool = False,
        console_level: LogLevelEnum = LogLevelEnum.TRACE,
        console_format: Optional[str] = None,
        clear_existing: bool = True,
    ):
        """
        Constructs all the necessary attributes for the Journal object.
        Initializes file and console loggers with specified configurations.
        """

        self._dirname = dirname
        self._filename = filename
        self._debug = debug
        self._rotation = rotation
        self._retention = retention
        self._formatting = formatting
        self._compression = compression
        self._encoding = encoding
        self._level = level
        self._serialize = serialize
        self._console = console
        self._console_level = console_level
        self._console_format = console_format
        self._clear_existing = clear_existing

        self._logo = self.load_logo()

        self.logger = logger

        self._configure(
            self._dirname,
            self._filename,
            self._debug,
            self._rotation,
            self._retention,
            self._formatting,
            self._compression,
            self._encoding,
            self._level,
            self._serialize,
            self._console,
            self._console_level,
            self._console_format,
            self._clear_existing,
        )

    def _configure(
        self,
        dirname: str,
        filename: str,
        debug: bool,
        rotation: str,
        retention: str,
        formatting: Optional[str],
        compression: str,
        encoding: EncodingEnum,
        level: LogLevelEnum,
        serialize: bool,
        console: bool,
        console_level: LogLevelEnum,
        console_format: Optional[str],
        clear_existing: bool,
    ):

        if clear_existing:
            self.logger.remove()

        name, ext = os.path.splitext(filename)

        if debug:
            if not ext:
                filename = f"{name}.debug.log"
            else:
                filename = f"{name}.debug{ext}"
            level = LogLevelEnum.DEBUG

        formatting = formatting if formatting else self.DEFAULT_LOG_FORMAT

        self._write_logo(os.path.join(dirname, filename))

        logger.add(
            sink=os.path.join(dirname, filename),
            rotation=rotation,
            retention=retention,
            format=formatting,
            compression=compression,
            encoding=encoding.value,
            level=level.value,
            enqueue=True,
            colorize=False,
            backtrace=True,
            diagnose=True,
        )

        if serialize:
            serialize_name = f"{name}.serialize{ext if ext else '.log'}"
            logger.add(
                sink=os.path.join(dirname, serialize_name),
                rotation=rotation,
                retention=retention,
                format=formatting,
                compression=compression,
                encoding=encoding.value,
                level=level.value,
                enqueue=True,
                colorize=False,
                backtrace=True,
                diagnose=True,
                serialize=serialize,
            )

        if console:
            if not console_format:
                console_format = (
                    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}:{function}:{line}</cyan> | "
                    "P:{process} T:{thread} | "
                    "<level>{message}</level>"
                )

            logger.add(
                sink=sys.stdout,
                format=console_format,
                level=console_level.value,
                colorize=True,
                enqueue=False,
            )

    @staticmethod
    def load_logo():
        logo_text = read_text("fairylandfuture.conf.release", "logo")

        return logo_text

    def _write_logo(self, sink: str):
        """
        Writes the logo to the specified file.
        :param sink: Sink file path.
        :type sink: str
        :return: ...
        :rtype: ...
        """
        if not os.path.exists(sink):
            os.makedirs(os.path.dirname(sink), exist_ok=True)

            with open(sink, "a+") as f:
                f.write(self._logo)

    def trace(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).trace(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).info(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).success(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        return self.logger.opt(depth=1).exception(msg, *args, **kwargs)


class SingletonJournal(Journal):

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if SingletonJournal._initialized:
            return

        super().__init__(*args, **kwargs)

        SingletonJournal._initialized = True
