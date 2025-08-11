# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-28 17:26:58 UTC+08:00
"""

import math


class GenericToolkit:

    @classmethod
    def format_filesize(cls, size: int) -> str:
        if size == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB", "TB"]

        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size / p, 2)
        return f"{s} {size_names[i]}"
