# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-14 10:48:20 UTC+08:00
"""

import json

from ._encoder import JsonEncoder


class JsonSerializerHelper:

    @classmethod
    def serialize(cls, value):
        return json.dumps(value, cls=JsonEncoder, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def deserialize(cls, value):
        return json.loads(value)
