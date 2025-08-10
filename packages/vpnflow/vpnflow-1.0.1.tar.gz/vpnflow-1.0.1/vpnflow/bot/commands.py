# -*- coding: utf-8 -*-
from aiogram.types import BotCommand

from vpnflow.enums import BotCommands, BotCommandsAdmin
from vpnflow.settings import settings


def build_menu_from_enum(enum, commands_text=settings.telegram.messages["commands"]):
    """⭐"""
    for k, _ in enum.__members__.items():
        yield BotCommand(command=f"/{k}", description=commands_text[k])


user = list(build_menu_from_enum(BotCommands))
admin = user + list(build_menu_from_enum(BotCommandsAdmin))
