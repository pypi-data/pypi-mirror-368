
# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-14 10:48:20 UTC+08:00
"""

import json
import datetime
import decimal

from fairylandfuture.enums.chron import DateTimeEnum
from fairylandfuture.core.superclass.structure import BaseFrozenStructure, BaseStructure

class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime(DateTimeEnum.DATETIME.value)
        elif isinstance(o, datetime.date):
            return o.strftime(DateTimeEnum.DATE.value)
        elif isinstance(o, datetime.time):
            return o.strftime(DateTimeEnum.TIME.value)
        elif isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, (BaseStructure, BaseFrozenStructure)):
            return o.to_json()

        return super().default(o)


# class JsonEncoder(JSONEncoder):
#
#     def __init__(self, *args, **kwargs):
#         superclass().__init__(*args, **kwargs)
#         self.visited_objects = set()
#
#     def default(self, obj):
#         obj_id = id(obj)
#         if obj_id in self.visited_objects:
#             return "[循环引用]"
#
#         self.visited_objects.add(obj_id)
#
#         try:
#             if isinstance(obj, datetime.datetime):
#                 return obj.strftime(DateTimeEnum.datetime.value)
#             elif isinstance(obj, datetime.date):
#                 return obj.strftime("%Y-%m-%d")
#             elif isinstance(obj, datetime.time):
#                 return obj.strftime("%H:%M:%S")
#             elif isinstance(obj, decimal.Decimal):
#                 return float(obj)
#             else:
#                 return superclass().default(obj)
#         finally:
#             self.visited_objects.remove(obj_id)