# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-08-14 17:02:11 UTC+08:00
"""

from dataclasses import dataclass, field
from typing import MutableSequence, Sequence, MutableMapping, Mapping, Union, Self, Dict, Any

from fairylandfuture.core.superclass.structure import BaseStructure, BaseFrozenStructure
from fairylandfuture.const.http.response import RESPONSE_CODE_MAPPING


@dataclass(frozen=False)
class ResponseStructure(BaseStructure):
    code: int = field(default=None)
    message: str = field(default=None)
    data: Union[MutableSequence, Sequence, MutableMapping, Mapping] = field(default=None)

    def __embody(self):
        if self.code and not self.message:
            self.message = RESPONSE_CODE_MAPPING.get(self.code, "Internal Server Error")

    def __post_init__(self):
        self.__embody()

    def __str__(self):
        self.__embody()
        return self.string

    @property
    def asdict(self: Self) -> Dict[str, Any]:
        self.__embody()
        return super().asdict


@dataclass(frozen=True)
class ResponseFrozenStructure(BaseFrozenStructure):
    code: int = field(default=None)
    message: str = field(default=None)
    data: Union[MutableSequence, Sequence, MutableMapping, Mapping] = field(default=None)

    def __post_init__(self):
        if self.code and not self.message:
            object.__setattr__(self, "message", RESPONSE_CODE_MAPPING.get(self.code, "Internal Server Error"))

    def __str__(self):
        return self.string
