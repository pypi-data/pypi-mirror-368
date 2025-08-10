# -*- coding: utf-8 -*-
from logging import getLogger
from typing import Optional, Tuple

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from vpnflow.bot import commands, middleware, routers
from vpnflow.services import _redis
from vpnflow.services._telegram import broadcast
from vpnflow.services.cache import CacheRepository
from vpnflow.settings import Settings, TelegramSettings, settings

logger = getLogger(__name__)
telegram_settings = settings.telegram


async def on_startup_bot(
    bot: Bot,
    bot_dispatcher: Dispatcher,
    settings_telegram: TelegramSettings = telegram_settings
    ):
    """⭐"""
    logger.info("Startup bot")
    bot_info = await bot.get_me()
    logger.info(f"Name: {bot_info.full_name}. Username: @{bot_info.username}. ID: {bot_info.id}")
    assert bot_info.username == settings.telegram.bot_name
    await broadcast(bot, settings_telegram.messages["bot-on"], *settings_telegram.admins_id)
    await bot.delete_my_commands()
    await bot.set_my_commands(commands.user)
    for admin_id in settings_telegram.admins_id:
        await bot.set_my_commands(commands.admin, scope=BotCommandScopeChat(chat_id=admin_id))
    if settings_telegram.webhook_use:
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info}")
        if webhook_info.url != settings_telegram.webhook_url:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(
                url=settings_telegram.webhook_url, drop_pending_updates=True,
                allowed_updates=bot_dispatcher.resolve_used_update_types(),
                max_connections=settings_telegram.webhook_max_connections,
                secret_token=settings_telegram.webhook_secret_token.get_secret_value()
                )
    is_health = await CacheRepository.check_health()
    assert is_health


async def on_shutdown_bot(
    bot: Bot,
    bot_dispatcher: Dispatcher,
    settings_telegram: TelegramSettings = telegram_settings
    ):
    """⭐"""
    logger.info("Shutdown bot")
    if isinstance(bot_dispatcher.storage, RedisStorage):
        await bot_dispatcher.storage.close()
        await bot_dispatcher.fsm.storage.close()
    await broadcast(bot, settings_telegram.messages["bot-off"], *settings_telegram.admins_id)
    # if settings_telegram.webhook_use:
    #     await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    await bot.close()
    await CacheRepository.close()


async def on_startup_bot_dispatcher(dispatcher) -> None:
    """⭐"""
    logger.info("Startup bot dispatcher")
    await on_startup_bot(dispatcher.bot, dispatcher)


async def on_shutdown_bot_dispatcher(dispatcher) -> None:
    """⭐"""
    logger.info("Shutdown bot dispatcher")
    await on_shutdown_bot(dispatcher.bot, dispatcher)


def create_bot(
    settings_telegram: TelegramSettings = telegram_settings,
    session: Optional[AiohttpSession] = None
    ) -> Bot:
    """⭐"""
    if session is None:
        session: AiohttpSession = AiohttpSession()
    return Bot(
        token=settings_telegram.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
        )


def create_dispatcher(
    bot: Bot = create_bot(),
    middlewares: Tuple = middleware.ALL,
    routers: Tuple = routers.ALL,
    settings: Settings = settings,
    on_startup = on_startup_bot_dispatcher,
    on_shutdown = on_shutdown_bot_dispatcher
    ) -> Dispatcher:
    """⭐"""
    redis_url = settings.telegram.redis_url.get_secret_value()
    if redis_url:
        storage: BaseStorage = RedisStorage(redis=_redis.create_client(redis_url))
    else:
        storage: BaseStorage = MemoryStorage()
    dispatcher = Dispatcher(name="bot_dispatcher", storage=storage)
    dispatcher.bot = bot
    for _middleware in middlewares:
        dispatcher.update.middleware.register(_middleware)
    dispatcher.callback_query.middleware(CallbackAnswerMiddleware())
    dispatcher.include_routers(*routers)
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)
    return dispatcher
