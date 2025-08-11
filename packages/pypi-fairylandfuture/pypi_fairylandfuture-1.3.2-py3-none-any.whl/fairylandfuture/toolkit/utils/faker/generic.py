# coding: UTF-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-10-15 17:00:00 UTC+08:00
"""

import secrets


class FakeGeneralToolkit:

    @classmethod
    def generate_hex_string(cls, number, group=1, sep=""):
        if number % 2 != 0:
            raise ValueError("The number must be an even number.")

        segments = [secrets.token_hex(round(number / 2)).upper() for _ in range(group)]
        return f"{sep}".join(segments)

    @classmethod
    def generate_random_string(cls, length=16, charset="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
        if length <= 0:
            raise ValueError("Length must be a positive integer.")
        return "".join(secrets.choice(charset) for _ in range(length))
