# -*- coding: utf-8 -*-
from logging import getLogger
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from vpnflow.bot import keyboards as kbs
from vpnflow.bot.callbacks import UserCallback
from vpnflow.services import business
from vpnflow.services._telegram import edit_callback
from vpnflow.settings import settings

logger = getLogger(__name__)
messages = settings.telegram.messages


class CheckAcceptMiddleware(BaseMiddleware):
    """⭐"""

    def __init__(
        self,
        callbacks = ("start", "pay", "setup", "promo", "invite", "help", "setup-platform", "setup-help")
        ) -> None:
        self.callbacks = callbacks

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and "/start" not in str(event.text):
            user = await business.get_user(telegram_id=event.from_user.id)
            if user and user.marzban_username is None:
                await event.answer(messages["start-welcome"], reply_markup=kbs.inline.user_welcome)
                return
            else:
                data["user"] = user
                if user is None:
                    logger.warning(f"User is None, {event.from_user.id}")
                    return
        if isinstance(event, CallbackQuery):
            callback_data = data.get("callback_data")
            if (
                callback_data and
                isinstance(callback_data, UserCallback) and
                callback_data.action in self.callbacks
            ):
                user = await business.get_user(telegram_id=event.from_user.id)
                if user and user.marzban_username is None:
                    await edit_callback(event, messages["start-welcome"], reply_markup=kbs.inline.user_welcome)
                    return
                else:
                    data["user"] = user
                    if user is None:
                        logger.warning(f"User is None, {event.from_user.id}")
                        return
        result = await handler(event, data)
        return result


class FilterNoUserMiddleware(BaseMiddleware):
    """⭐"""

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (CallbackQuery, Message)) and event.from_user is None:
            return
        result = await handler(event, data)
        return result


ALL = (FilterNoUserMiddleware(), )
