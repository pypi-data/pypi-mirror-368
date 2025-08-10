# -*- coding: utf-8 -*-
from logging import getLogger
from logging.config import dictConfig

import yaml

logger = getLogger(__name__)


def load_yaml(file_path: str) -> dict:
    """⭐"""
    with open(file_path, 'r', encoding="UTF-8") as f:
        return yaml.safe_load(f.read())


def load_log_conf(file_path: str) -> None:
    """⭐"""
    dictConfig(load_yaml(file_path))


def days_verbose(days: int) -> str:
    """⭐"""
    if days > 20:
        days %= 10
    if days == 1:
        return "день"
    elif 2 <= days <= 4:
        return "дня"
    return "дней"


def slice_generator(s, l):
    """⭐"""
    for i in range(0, len(s), l):
        yield s[i:i + l]
