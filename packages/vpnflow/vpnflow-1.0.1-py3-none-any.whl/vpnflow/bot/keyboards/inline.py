# -*- coding: utf-8 -*-
from functools import lru_cache

from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from vpnflow.bot import callbacks as cb
from vpnflow.settings import settings

buttons_text = settings.telegram.messages["buttons"]


def create_inline_keyboard(*buttons_data, rows_num=None, cols_num=None, attach=None, as_markup=True):
    """⭐"""
    kb = InlineKeyboardBuilder()
    for button_text, button_callback in buttons_data:
        kb.button(text=button_text, callback_data=button_callback)
    if attach:
        kb.attach(attach)
    if rows_num:
        if cols_num:
            kb.adjust(rows_num, cols_num)
        else:
            kb.adjust(rows_num)
    if as_markup:
        return kb.as_markup()
    return kb


@lru_cache(maxsize=32)
def build_referral(url: str) -> InlineKeyboardMarkup:
    """⭐"""
    kb = InlineKeyboardBuilder()
    kb.button(text=buttons_text["referral-share"], url=f"https://telegram.me/share/url?url={url}")
    kb.button(text=buttons_text["start"], callback_data=cb.UserCallback(action="start"))
    kb.adjust(1)
    return kb.as_markup()


@lru_cache(maxsize=32)
def build_setup(url: str) -> InlineKeyboardMarkup:
    """⭐"""
    kb = InlineKeyboardBuilder()
    kb.button(text=buttons_text["setup-open"], web_app=WebAppInfo(url=url))
    return kb.as_markup()


async def build_pay_plans(pay_plans_agenerator) -> InlineKeyboardMarkup:
    """⭐"""
    kb_data = []
    async for pay_plan in pay_plans_agenerator:
        kb_data.append(
            (
                pay_plan.button_text,
                cb.PayPlanCallback(action="choice-pay-plan", value=pay_plan.id))
                )
    kb_data.append((buttons_text["back"], cb.UserCallback(action="start")))
    return create_inline_keyboard(*kb_data, rows_num=1)


def build_pay_plan_prices(pay_plan) -> InlineKeyboardMarkup:
    """⭐"""
    kb_data = []
    for pay_plan_price in pay_plan.prices:
        kb_data.append(
            (
                pay_plan_price.currency.symbol,
                cb.PayPlanCallback(action="choice-pay-method", value=pay_plan_price.payment_method))
            )
    return create_inline_keyboard(*kb_data, rows_num=2)


@lru_cache(maxsize=32)
def build_setup_steps(download_url: str, add_url: str) -> InlineKeyboardMarkup:
    """⭐"""
    kb = InlineKeyboardBuilder()
    kb.button(text=buttons_text["setup-download"], url=download_url)
    kb.button(text=buttons_text["setup-add"], url=add_url)
    kb.button(text=buttons_text["start"], callback_data=cb.UserCallback(action="start"))
    kb.adjust(1)
    return kb.as_markup()


support = InlineKeyboardBuilder()
support.button(text=buttons_text["help-faq"], web_app=WebAppInfo(url=settings.business.url_faq))
support.button(text=buttons_text["help-ask"], url=settings.business.url_support)
support.button(text=buttons_text["setup-help"], callback_data=cb.UserCallback(action="setup-help"))
support.button(text=buttons_text["back"], callback_data=cb.UserCallback(action="start"))
support.adjust(1)
support = support.as_markup()

support_back = InlineKeyboardBuilder()
support_back.button(text=buttons_text["back"], callback_data=cb.UserCallback(action="help"))
support_back.adjust(1)
support_back = support_back.as_markup()

yes_no_menu = create_inline_keyboard(
    *(
        (buttons_text["choice-yes"], cb.YesNoCallback(value=True)),
        (buttons_text["choice-no"], cb.YesNoCallback(value=False))
    ), rows_num=2
)

user_promo = create_inline_keyboard(
    *(
        (buttons_text["promo-again"], cb.UserCallback(action="promo")),
        (buttons_text["start"], cb.UserCallback(action="start"))
    ), rows_num=1
)

user_welcome = InlineKeyboardBuilder()
user_welcome.button(text=buttons_text["start-accept"], callback_data=cb.UserCallback(action="sign_up"))
user_welcome.adjust(1)
user_welcome = user_welcome.as_markup()

user_start = InlineKeyboardBuilder()
user_start.button(text=buttons_text["start"], callback_data=cb.UserCallback(action="start"))
user_start = user_start.as_markup()

user_start_new = InlineKeyboardBuilder()
user_start_new.button(text=buttons_text["start-setup"], callback_data=cb.UserCallback(action="setup"))
user_start_new = user_start_new.as_markup()

user_setup_platform = create_inline_keyboard(
    *(
        (
            platform, cb.UserCallback(action="setup-platform", value=platform)
            ) for platform in settings.business.supported_platforms
    ), rows_num=4
)

user = create_inline_keyboard(
    *(
        (
            buttons_text[k], cb.UserCallback(action=k)
            ) for k in ("pay", "setup", "promo", "invite", "help")
    ), rows_num=1
)


admin = create_inline_keyboard(
    *(
        (
            buttons_text[f"admin-{k}"], cb.AdminCallback(action=k)
            ) for k in ("stats", "notify", "coupons", "services")
    ), rows_num=1
)

admin_notify = create_inline_keyboard(
    *(
        (buttons_text["admin-notify-all"], cb.NotifyCallback(value="all")),
        (buttons_text["admin-notify-active"], cb.NotifyCallback(value="active")),
        (buttons_text["admin-notify-expired"], cb.NotifyCallback(value="expired")),
        (buttons_text["admin-notify-pay-expired"], cb.NotifyCallback(value="pay-expired")),
        (buttons_text["admin-notify-pay-no-expired"], cb.NotifyCallback(value="pay-no-expired")),
        (buttons_text["back"], cb.AdminCallback(action="panel"))
    ), rows_num=1
)

admin_start = InlineKeyboardBuilder()
admin_start.button(text=buttons_text["panel"], callback_data=cb.AdminCallback(action="panel"))
admin_start = admin_start.as_markup()
