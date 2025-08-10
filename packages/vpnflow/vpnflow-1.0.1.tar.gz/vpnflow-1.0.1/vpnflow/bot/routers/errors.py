# -*- coding: utf-8 -*-
from logging import getLogger
from typing import Final

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import ErrorEvent

from vpnflow.settings import settings

router: Final[Router] = Router(name=__name__)
logger = getLogger(__name__)
telegram_settings = settings.telegram


@router.errors()
async def error_handler(event: ErrorEvent, bot: Bot) -> None:
    """⭐"""
    logger.critical(event, exc_info=True)

    message = event.update.message

    if not message:
        return

    await message.answer(telegram_settings.messages["error"])

    user_id = message.from_user.id if message.from_user else ""
    text = telegram_settings.messages["error-notify"].format(
        user_id=user_id, error=event.exception
        )

    logger.error(text)

    if telegram_settings.log_chat:
        try:
            await bot.send_message(chat_id=telegram_settings.log_chat, text=text)
        except (TelegramBadRequest, TelegramRetryAfter) as exc:
            logger.error(exc)
