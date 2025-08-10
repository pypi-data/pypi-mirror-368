# -*- coding: utf-8 -*-
from asyncio import get_event_loop
from logging import getLogger

import uvicorn
from aiogram.exceptions import TelegramRetryAfter

from vpnflow.bot.base import create_dispatcher
from vpnflow.cli import create_parser, show_art
from vpnflow.db.tools import init_db
from vpnflow.flows._schedule import run_scheduled_tasks
from vpnflow.misc import load_log_conf
from vpnflow.settings import settings

logger = getLogger(__name__)


def main():
    """⭐"""
    show_art()
    parser, loop = create_parser(), get_event_loop()

    args = parser.parse_args()

    if args.log_conf_file:
        load_log_conf(args.log_conf_file)

    logger.debug(f"Run with args: {args}, settings: {settings}")

    if args.run_scheduled_tasks:
        run_scheduled_tasks()

    if args.command == "db":
        loop.run_until_complete(init_db(args))

    if settings.telegram.webhook_use:
        uvicorn.run(
            "vpnflow.web.app:app",
            host=settings.webserver.host, port=settings.webserver.port,
            workers=settings.webserver.workers, reload=settings.webserver.reload
            )
    else:
        bot_dispatcher = create_dispatcher()
        try:
            loop.run_until_complete(
                bot_dispatcher.start_polling(
                    bot_dispatcher.bot,
                    allowed_updates=bot_dispatcher.resolve_used_update_types(),
                    polling_timeout=60, skip_updates=True
                    )
                )
        except KeyboardInterrupt:
            loop.run_until_complete(bot_dispatcher.stop_polling())
        except TelegramRetryAfter as exc:
            logger.error(exc)
        except Exception as exc:
            logger.exception(exc)


if __name__ == "__main__":
    main()
