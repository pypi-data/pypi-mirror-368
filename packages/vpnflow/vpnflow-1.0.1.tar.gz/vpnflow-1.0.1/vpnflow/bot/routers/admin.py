# -*- coding: utf-8 -*-
from asyncio import create_task
from logging import getLogger
from typing import Final

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from vpnflow.bot import callbacks as cb
from vpnflow.bot import keyboards as kbs
from vpnflow.bot import states as st
from vpnflow.bot.filters import AdminFilter
from vpnflow.enums import BotCommandsAdmin
from vpnflow.services import _telegram, business
from vpnflow.services._telegram import edit_callback
from vpnflow.settings import settings

logger = getLogger(__name__)
router: Final[Router] = Router(name=__name__)
router.message.filter(AdminFilter(), F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(AdminFilter(), F.message.chat.type == ChatType.PRIVATE)

admins_id = settings.telegram.admins_id
messages = settings.telegram.messages


@router.message(Command(BotCommandsAdmin.panel.name))
async def cmd_panel(message: Message) -> None:
    """⭐"""
    await message.answer(
        messages[BotCommandsAdmin.panel.name], reply_markup=kbs.inline.admin
        )


@router.callback_query(
    cb.AdminCallback.filter(F.action == "panel"), F.from_user.id.in_(admins_id)
    )
async def cb_panel(callback_query: CallbackQuery) -> None:
    """⭐"""
    await edit_callback(
        callback_query, messages[BotCommandsAdmin.panel.name], reply_markup=kbs.inline.admin
        )


@router.callback_query(
    cb.AdminCallback.filter(F.action == "stats"), F.from_user.id.in_(admins_id)
    )
async def cb_stats(callback_query: CallbackQuery, bot: Bot) -> None:
    """⭐"""
    await callback_query.answer(messages["admin-stats-answr"])
    create_task(business.send_stats(bot, callback_query.from_user.id))
    await edit_callback(
        callback_query, messages["admin-stats-preview"],
        reply_markup=kbs.inline.admin_start
        )
    return


@router.callback_query(
    cb.AdminCallback.filter(F.action == "notify"), F.from_user.id.in_(admins_id)
    )
async def cb_notify(callback_query: CallbackQuery, state: FSMContext) -> None:
    """⭐"""
    await edit_callback(
        callback_query, messages["admin-notify"], reply_markup=kbs.inline.admin_notify
        )
    await state.set_state(st.NotifyForm.group_choice)


@router.callback_query(
    cb.NotifyCallback.filter(), F.from_user.id.in_(admins_id),
    st.NotifyForm.group_choice
    )
async def cb_choice_group(
    callback_query: CallbackQuery,
    callback_data: cb.NotifyCallback,
    state: FSMContext
    ) -> None:
    """⭐"""
    notify_group = callback_data.value
    await state.update_data(notify_group=notify_group)
    await edit_callback(
        callback_query, messages["admin-notify-text"]
        )
    await state.set_state(st.NotifyForm.message)


@router.message(st.NotifyForm.message)
async def notify_accept(message: Message, state: FSMContext) -> None:
    """⭐"""
    if message.photo is not None:
        await state.update_data(notify_image=message.photo[-1].file_id)
    await state.update_data(notify_message=message.html_text.strip())
    await message.answer(messages["admin-notify-accept"], reply_markup=kbs.inline.yes_no_menu)
    await state.set_state(st.NotifyForm.accept_choice)


@router.callback_query(
    cb.YesNoCallback.filter(), F.from_user.id.in_(admins_id),
    st.NotifyForm.accept_choice
    )
async def cb_accept_choice(
    callback_query: CallbackQuery,
    callback_data: cb.YesNoCallback,
    state: FSMContext, bot: Bot
    ) -> None:
    """⭐"""
    state_data = await state.get_data()
    await _telegram.clean_state(state)
    if callback_data.value:
        await callback_query.answer(messages["admin-notify-start"])
        notified_users = await business.notify_users(bot, **state_data)
        await edit_callback(
            callback_query,
            messages["admin-notify-end"].format(notified_users=notified_users),
            reply_markup=kbs.inline.admin_start
            )
    else:
        await edit_callback(
             callback_query, messages[BotCommandsAdmin.panel.name], reply_markup=kbs.inline.admin
             )


@router.callback_query(
    cb.AdminCallback.filter(F.action == "coupons"), F.from_user.id.in_(admins_id)
    )
async def cb_coupons(callback_query: CallbackQuery, state: FSMContext) -> None:
    """⭐"""
    await edit_callback(callback_query, messages["admin-coupons"])
    await state.set_state(st.CouponAddForm.name)


@router.message(st.CouponAddForm.name)
async def coupons_name(message: Message, state: FSMContext) -> None:
    """⭐"""
    await state.update_data(coupon_id=message.text.strip().upper())
    await message.answer(messages["admin-coupons-days"])
    await state.set_state(st.CouponAddForm.days)


@router.message(st.CouponAddForm.days)
async def coupons_accept(message: Message, state: FSMContext) -> None:
    """⭐"""
    await state.update_data(coupon_days=message.text.strip())
    await message.answer(messages["admin-coupons-usage-accept"], reply_markup=kbs.inline.yes_no_menu)
    await state.set_state(st.CouponAddForm.accept_usage_limit)


@router.callback_query(
    cb.YesNoCallback.filter(), F.from_user.id.in_(admins_id),
    st.CouponAddForm.accept_usage_limit
    )
async def coupons_accept_usage_limit(
    callback_query: CallbackQuery,
    callback_data: cb.YesNoCallback,
    state: FSMContext
    ) -> None:
    """⭐"""
    if callback_data.value:
        await edit_callback(callback_query, messages["admin-coupons-usage"])
        await state.set_state(st.CouponAddForm.usage_limit)
    else:
        await edit_callback(callback_query, messages["admin-coupons-accept"], reply_markup=kbs.inline.yes_no_menu)
        await state.set_state(st.CouponAddForm.accept_choice)


@router.message(st.CouponAddForm.usage_limit)
async def coupons_usage_limit(message: Message, state: FSMContext) -> None:
    """⭐"""
    await state.update_data(coupon_usage_limit=message.text.strip())
    await message.answer(messages["admin-coupons-accept"], reply_markup=kbs.inline.yes_no_menu)
    await state.set_state(st.CouponAddForm.accept_choice)


@router.callback_query(
    cb.YesNoCallback.filter(), F.from_user.id.in_(admins_id),
    st.CouponAddForm.accept_choice
    )
async def coupons_accept_choice(
    callback_query: CallbackQuery,
    callback_data: cb.YesNoCallback,
    state: FSMContext
    ) -> None:
    """⭐"""
    state_data = await state.get_data()
    await _telegram.clean_state(state)
    if callback_data.value:
        coupon_created = await business.create_coupon(**state_data)
        if coupon_created:
            await edit_callback(
                callback_query,
                messages["admin-coupons-success"],
                reply_markup=kbs.inline.admin_start
                )
        else:
            await edit_callback(
                callback_query,
                messages["admin-coupons-failed"],
                reply_markup=kbs.inline.admin_start
                )
    else:
        await edit_callback(
            callback_query, messages[BotCommandsAdmin.panel.name],
            reply_markup=kbs.inline.admin
            )

@router.callback_query(
    cb.AdminCallback.filter(F.action == "services"), F.from_user.id.in_(admins_id)
    )
async def cb_services(callback_query: CallbackQuery) -> None:
    """⭐"""
    await edit_callback(
        callback_query, messages["admin-services"],
        reply_markup=kbs.inline.admin_start
        )
