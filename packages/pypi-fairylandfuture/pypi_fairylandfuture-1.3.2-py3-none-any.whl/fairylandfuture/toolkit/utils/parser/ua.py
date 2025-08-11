# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2025-05-28 17:17:06 UTC+08:00
"""

import typing as t
from user_agents import parse


class UserAgentParserToolkit:

    @classmethod
    def parse_user_agent(cls, user_agent: str) -> t.Optional[t.Dict[str, t.Any]]:
        if not user_agent:
            return None

        parsed = parse(user_agent)

        return {
            "browser": {
                "family": parsed.browser.family,
                "version": parsed.browser.version_string,
            },
            "os": {
                "family": parsed.os.family,
                "version": parsed.os.version_string,
            },
            "device": {
                "family": parsed.device.family,
                "brand": parsed.device.brand,
                "model": parsed.device.model,
            },
            "is_mobile": parsed.is_mobile,
            "is_tablet": parsed.is_tablet,
            "is_pc": parsed.is_pc,
            "is_bot": parsed.is_bot,
        }
