# -*- coding: utf-8 -*-
from enum import Enum

BotCommands = Enum("BotCommands", ("start", "pay", "help"))
BotCommandsAdmin = Enum("BotCommandsAdmin", ("panel", ))
