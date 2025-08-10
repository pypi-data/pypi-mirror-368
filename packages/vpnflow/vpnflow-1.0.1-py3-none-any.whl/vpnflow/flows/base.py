# -*- coding: utf-8 -*-
import asyncio
from logging import getLogger

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramRetryAfter

from vpnflow.bot.base import create_bot
from vpnflow.db.base import engine_mrzbn, engine_r, run_session
from vpnflow.db.tools import (get_soon_expired_users,
                              get_telegram_expired_users, load_external_table)
from vpnflow.misc import days_verbose
from vpnflow.services._telegram import broadcast
from vpnflow.settings import settings

logger = getLogger(__name__)


async def _send_messsages(session, soon_expired_telegram_users):
    """⭐"""
    bot = create_bot(session=session)
    message_template = settings.telegram.messages["flows-notify-users"]
    async for days_exp, telegram_ids in soon_expired_telegram_users:
        message = message_template.format(
            days_exp=days_exp, days_exp_say=days_verbose(days_exp)
            )
        await broadcast(bot, message, *telegram_ids)
    try:
        await bot.session.close()
        # await bot.close()
    except TelegramRetryAfter as exc:
        logger.error(exc)
    except Exception as exc:
        logger.error(f"{type(exc)}. {exc}")


async def _notify_users():
    """⭐"""
    users_table = await load_external_table(engine_mrzbn, "users")
    async with \
        run_session(engine_mrzbn) as session_marzban, \
        run_session(engine_r) as session, \
        AiohttpSession() as http_session \
        :
        soon_expired_marzban_users = get_soon_expired_users(
            session_marzban, users_table, *settings.flows.notify_users_days
            )
        soon_expired_telegram_users = get_telegram_expired_users(session, soon_expired_marzban_users)
        await _send_messsages(http_session, soon_expired_telegram_users)


def notify_users():
    """⭐"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_notify_users())
