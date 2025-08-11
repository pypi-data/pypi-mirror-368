# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-07-17 10:42:19 UTC+08:00
"""

import warnings
from typing import Dict, Union, Tuple, Sequence, Any, Literal

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk

from fairylandfuture.exceptions.elasticsearch import ElasticSearchExecutionException
from fairylandfuture.exceptions.messages.elasticsearch import ElasticSearchExceptMessage
from fairylandfuture.structures.builder.elasticsearch import ElasticsearchBulkParamFrozenStructure

warnings.filterwarnings("ignore")


class ElasticSearchOperator:

    def __init__(self, client: Elasticsearch):
        self.__client = client

    @property
    def client(self):
        return self.__client

    @property
    def info(self) -> Dict[str, Any]:
        return self.client.info().raw

    @property
    def indices(self) -> Tuple[str, ...]:
        return tuple(self.client.indices.get(index="*").raw.keys())

    def _validate_index(self, index: str) -> str:
        if self.client.indices.exists_alias(name=index):
            raise ElasticSearchExecutionException(ElasticSearchExceptMessage.ALIAS_NOT_ALLOWED)
        if not self.client.indices.exists(index=index):
            raise ElasticSearchExecutionException(ElasticSearchExceptMessage.INDEX_NOT_EXISTS)

        return index

    def _validate_alias(self, alias: str) -> str:
        if self.client.indices.exists(index=alias):
            raise ElasticSearchExecutionException(ElasticSearchExceptMessage.INDEX_NOT_ALLOWED)
        if not self.client.indices.exists_alias(name=alias):
            raise ElasticSearchExecutionException(ElasticSearchExceptMessage.ALIAS_NOT_EXISTS)

        return alias

    def _validate_doc(self, index: str, doc_id: str):
        self._validate_index(index)

        if not self.client.exists(index=index, id=doc_id):
            raise ElasticSearchExecutionException(ElasticSearchExceptMessage.DOC_NOT_EXISTS)

    def get_name_type(self, name: str) -> Literal["index", "alias", "both", "none"]:
        index = self.client.indices.exists(index=name)
        alias = self.client.indices.exists_alias(name=name)

        if index and alias:
            return "both"
        elif index:
            return "index"
        elif alias:
            return "alias"
        else:
            return "none"

    def get_index_info(self, index: str):
        self._validate_index(index)

        return self.client.indices.get(index=index).raw.get(index)

    def get_doc_info(self, index: str, doc_id: str) -> Dict[str, Any]:
        self._validate_index(index)
        self._validate_doc(index, doc_id)

        return self.client.get(index=index, id=doc_id).raw

    def get_index_stats(self, index: str):
        self._validate_index(index)

        return self.client.indices.stats(index=index).raw

    def get_index_stats_light(self, index: str) -> Dict[str, Dict[str, str]]:
        self._validate_index(index)

        data = self.client.cat.indices(index=index, format="json").raw

        result = {row.get("index"): row for row in data}

        return result

    def get_indices_for_alias(self, name: str) -> Union[str, Tuple[str, ...]]:
        try:
            result = tuple(self.client.indices.get_alias(name=name).raw.keys())

            return result if len(result) > 1 else result[0]
        except NotFoundError as err:
            raise RuntimeWarning from err

    def search(self, index: str, body: Dict[str, Any]):
        if not self.client.indices.exists(index=index):
            raise ElasticSearchExecutionException(ElasticSearchExceptMessage.INDEX_NOT_EXISTS)

        results = self.client.search(index=index, body=body).raw

        if results.get("timed_out"):
            raise ElasticSearchExecutionException(ElasticSearchExceptMessage.TIMEOUT)

        return results

    def update_partial(self, index: str, doc_id: str, content: Dict[str, Any]):
        self._validate_index(index)
        self._validate_doc(index, doc_id)

        return self.client.update(index=index, id=doc_id, body={"doc": content}, refresh=True).raw

    def update_replace(self, index: str, doc_id: str, document: Dict[str, Any]):
        self._validate_index(index)
        self._validate_doc(index, doc_id)

        return self.client.index(index=index, id=doc_id, body=document, refresh=True)

    def bulk_update(self, params: Sequence[ElasticsearchBulkParamFrozenStructure]):
        actions = [{"_op_type": "update", "_index": param.index, "_id": param.id, "doc": param.content} for param in params]

        succeed, failed = bulk(self.client, actions, stats_only=True, refresh=True)

        return succeed, failed

    @classmethod
    def parser_search_results(cls, data: Union[str, Dict[str, Any]]) -> Tuple[int, Tuple[Dict[str, ...], ...]]:
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        hits = data.get("hits", {}).get("hits", [])
        return total, tuple(hits)
