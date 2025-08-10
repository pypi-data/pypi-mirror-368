# -*- coding: utf-8 -*-
from aiogram.fsm.state import State, StatesGroup


class CouponForm(StatesGroup):
    """⭐"""
    coupon = State()


class PayPlanForm(StatesGroup):
    """⭐"""
    payplan_choice = State()
    pay_method_choice = State()
    accept_choice = State()
    write_off_balance = State()


class SupportForm(StatesGroup):
    """⭐"""
    question = State()


class NotifyForm(StatesGroup):
    """⭐"""
    group_choice = State()
    message = State()
    accept_choice = State()


class CouponAddForm(StatesGroup):
    """⭐"""
    name = State()
    days = State()
    accept_choice = State()
    accept_usage_limit = State()
    usage_limit = State()
