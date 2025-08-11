# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-22 17:45:03 UTC+08:00
"""

from dataclasses import dataclass
from typing import Union, Mapping, MutableMapping, Any

from fairylandfuture.core.superclass.structure import BaseFrozenStructure


@dataclass(frozen=True)
class ElasticsearchBulkParamFrozenStructure(BaseFrozenStructure):
    index: str
    id: str
    content: Union[Mapping[str, Any], MutableMapping[str, Any]]
