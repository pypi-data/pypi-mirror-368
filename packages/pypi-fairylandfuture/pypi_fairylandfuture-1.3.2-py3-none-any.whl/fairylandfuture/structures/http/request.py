# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-21 10:51:39 UTC+08:00
"""

from dataclasses import dataclass
from typing import Union, Dict, Any, Literal, Optional, Self

from requests import Response

from fairylandfuture.core.superclass.structure import BaseFrozenStructure
from fairylandfuture.helpers.json.serializer import JsonSerializerHelper


@dataclass(frozen=True)
class HTTPSimpleRequestResultStructure(BaseFrozenStructure):
    flag: bool
    content: Optional[Union[str, Dict[str, Any]]]
    format: Optional[Literal["json", "text"]]
    response: Optional[Response]

    def __repr__(self):
        if self.format == "json":
            content = JsonSerializerHelper.serialize(self.content)
        else:
            content = self.content

        return f"<HTTPSimpleRequestResultStructure(flag={self.flag}, content={content}, format={self.format}, response={self.response})"

    def to_json(self: Self, /, *, ignorenone: bool = False) -> Dict[str, Any]:
        result = super().to_dict(ignorenone=ignorenone)

        if self.response:
            result["response"] = {
                "status_code": self.response.status_code,
                "headers": dict(self.response.headers),
                "url": self.response.url,
                "cookies": dict(self.response.cookies),
                "elapsed": self.response.elapsed.total_seconds() if self.response.elapsed else None,
            }

        return result
