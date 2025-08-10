# -*- coding: utf-8 -*-
from typing import Any, Optional, Union

from aiogram.filters.callback_data import CallbackData


class PayPlanCallback(CallbackData, prefix="payplan"):
    """⭐"""
    action: str
    value: Union[int, str]


class YesNoCallback(CallbackData, prefix="yesno"):
    """⭐"""
    value: bool


class AdminCallback(CallbackData, prefix="admin"):
    """⭐"""
    action: str


class SupportCallback(CallbackData, prefix="support"):
    """⭐"""
    action: str


class UserCallback(CallbackData, prefix="user"):
    """⭐"""
    action: str
    value: Optional[Any] = None


class NotifyCallback(CallbackData, prefix="notify"):
    """⭐"""
    value: str
