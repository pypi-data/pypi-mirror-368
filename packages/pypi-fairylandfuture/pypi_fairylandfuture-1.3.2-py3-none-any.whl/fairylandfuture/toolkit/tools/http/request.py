# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-20 12:26:19 UTC+08:00
"""

from typing import Optional, Dict, Any

import requests
import urllib3

from fairylandfuture.exceptions.generic import BaseProgramException
from fairylandfuture.structures.http.request import HTTPSimpleRequestResultStructure

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPSimpleRequest:

    def __init__(self, headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None, verify: bool = False, timeout: Optional[int] = None):
        self.headers = self._make_headers(headers)
        self.cookies = cookies if cookies else {}
        self.verify = verify
        self.timeout = timeout if timeout else 30

    def _make_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        if not headers:
            return {"Content-Type": "application/json"}

        if headers and isinstance(headers, dict) and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        return headers

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> HTTPSimpleRequestResultStructure:
        try:
            response = requests.get(url, params=params, headers=self.headers, cookies=self.cookies, verify=self.verify, timeout=self.timeout)
            response.raise_for_status()

            try:
                result = response.json()

                return HTTPSimpleRequestResultStructure(True, result, "json", response)
            except requests.exceptions.JSONDecodeError:
                result = response.text

                return HTTPSimpleRequestResultStructure(True, result, "text", response)

        except requests.exceptions.HTTPError as err:
            raise BaseProgramException from err

        except Exception as err:
            raise RuntimeError from err

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> HTTPSimpleRequestResultStructure:
        try:
            response = requests.post(url, json=data, headers=self.headers, cookies=self.cookies, verify=self.verify, timeout=self.timeout)
            response.raise_for_status()

            try:
                result = response.json()

                return HTTPSimpleRequestResultStructure(True, result, "json", response)
            except requests.exceptions.JSONDecodeError:
                result = response.text

                return HTTPSimpleRequestResultStructure(True, result, "text", response)

        except requests.exceptions.HTTPError as err:
            raise BaseProgramException from err

        except Exception as err:
            raise RuntimeError from err

