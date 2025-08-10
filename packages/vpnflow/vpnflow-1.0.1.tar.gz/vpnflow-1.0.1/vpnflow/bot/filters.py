# -*- coding: utf-8 -*-
from aiogram.filters import BaseFilter
from aiogram.types import Message

from vpnflow.settings import settings


class AdminFilter(BaseFilter):
    """⭐"""

    ADMINS = settings.telegram.admins_id

    async def __call__(self, event: Message) -> bool:
        user = event.from_user
        if user:
            return user.id in self.ADMINS
        return False


class BlacklistFilter(BaseFilter):
    """⭐"""

    BLACKLIST = set(settings.telegram.blacklist)

    async def __call__(self, event: Message) -> bool:
        user = event.from_user
        if user:
            return False if user.id in self.BLACKLIST else True
