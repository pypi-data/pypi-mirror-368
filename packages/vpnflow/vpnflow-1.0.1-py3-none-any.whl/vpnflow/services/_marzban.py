# -*- coding: utf-8 -*-
import random
from logging import getLogger
from ssl import create_default_context

import certifi
from aiohttp import FormData

from vpnflow.settings import settings

logger = getLogger(__name__)
ssl_context = create_default_context(cafile=certifi.where())


class MarzbanUsernameGenerator:
    """⭐"""

    def __init__(self, name_len: int = settings.business.username_len):
        self._len = name_len
        self._alphabet = ("aeiou", "bcdfghjklmnpqrstvwxyz") # vowels, consonants

    def __next__(self):
        word = ""
        for _ in range(self._len):
            if _ % 2 == 0:
                word += random.choice(self._alphabet[1])
            else:
                word += random.choice(self._alphabet[0])
        return word.upper()

    def __call__(self):
        return next(self)


class Marzban:
    """⭐"""

    settings = settings.marzban
    usernames_generator = MarzbanUsernameGenerator()

    @classmethod
    async def auth(cls, session):
        """⭐"""
        auth_data = FormData()
        auth_data.add_field('username', cls.settings.username)
        auth_data.add_field('password', cls.settings.password.get_secret_value())
        rs = await cls.request(session, "POST", "/admin/token", json=None, data=auth_data)
        return {"Authorization": "Bearer {access_token}".format(**rs)}

    @classmethod
    async def request(cls, session, method, path, json=None, data=None, **headers):
        """⭐"""
        if json:
            session_request = session.request(
                method, cls.settings.host_api + path,
                json=json, headers=headers, ssl=ssl_context
                )
        elif data:
            session_request = session.request(
                method, cls.settings.host_api + path,
                data=data, headers=headers, ssl=ssl_context
                )
        else:
            session_request = session.request(
                method, cls.settings.host_api + path,
                headers=headers, ssl=ssl_context
                )
        async with session_request as resp:
            if resp.status == 200:
                resp_data = await resp.json()
                return resp_data
            else:
                try:
                    resp_data = await resp.json()
                except Exception:
                    resp_data = await resp.text()
                logger.error(f"Status: {resp.status}. Message: {resp_data}")
                resp.raise_for_status()
