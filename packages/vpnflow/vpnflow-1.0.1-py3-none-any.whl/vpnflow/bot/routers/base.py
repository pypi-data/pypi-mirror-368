# -*- coding: utf-8 -*-
from asyncio import create_task
from datetime import datetime
from logging import getLogger
from typing import Final

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types.pre_checkout_query import PreCheckoutQuery

from vpnflow.bot import callbacks as cb
from vpnflow.bot import keyboards as kbs
from vpnflow.bot import states as st
from vpnflow.bot.filters import BlacklistFilter
from vpnflow.bot.middleware import CheckAcceptMiddleware
from vpnflow.db.models import User
from vpnflow.enums import BotCommands
from vpnflow.misc import days_verbose
from vpnflow.services import _telegram, business
from vpnflow.settings import settings
from vpnflow.web import schemas

router: Final[Router] = Router(name=__name__)
router.message.middleware(CheckAcceptMiddleware())
router.callback_query.middleware(CheckAcceptMiddleware())
router.message.filter(BlacklistFilter(), F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(BlacklistFilter(), F.message.chat.type == ChatType.PRIVATE)
logger = getLogger(__name__)
messages = settings.telegram.messages
business_settings = settings.business


@router.message(CommandStart(deep_link=True))
@router.message(Command(BotCommands.start.name))
async def cmd_start(message: Message, command: CommandObject) -> None:
    """⭐"""
    user_data = message.from_user
    is_exists = await business.is_telegram_user_exists(user_data.id)
    if not is_exists:
        user_created = await business.create_user_from_telegram(user_data, command.args)
        if user_created:
            await message.answer(messages["start-welcome"], reply_markup=kbs.inline.user_welcome)
        return
    user = await business.get_user(telegram_id=user_data.id)
    if user is None:
        logger.warning(f"User is None, {user_data.id}")
        return
    if user and user.marzban_username is None:
        await message.answer(messages["start-welcome"], reply_markup=kbs.inline.user_welcome)
        return
    user_balances = await business.get_user_balances(user)
    marzban_user = await business.get_user_marzban(user.marzban_username)
    msg_id = "start-success" if marzban_user.status == "active" else "start-expired"
    await message.answer(
        messages[msg_id].format(
            marzban_username=user.marzban_username, user_balance=user_balances,
            sub_date=datetime.fromtimestamp(marzban_user.expire).strftime("%d.%m.%Y"),
            subscription_url=marzban_user.subscription_url
            ),
        reply_markup=kbs.inline.user,
        disable_web_page_preview=True
        )
    return


@router.callback_query(cb.UserCallback.filter(F.action == "sign_up"))
async def cb_sign_up(
    callback_query: CallbackQuery, callback_data: cb.UserCallback
    ) -> None:
    """⭐"""
    user = await business.get_user(telegram_id=callback_query.from_user.id)
    if not user:
        return
    test_days = business_settings.test_days
    test_traffic_gb_limit = business_settings.test_traffic_gb_limit
    test_proxies = business_settings.test_proxies
    test_inbounds = business_settings.test_inbounds
    marzban_user = await business.create_user_marzban(
        days=test_days, traffic_limit=test_traffic_gb_limit,
        proxies=test_proxies, inbounds=test_inbounds
        )
    _ = await business.update_user(user, marzban_username=marzban_user.username)
    user = await business.get_user(telegram_id=callback_query.from_user.id)
    await _telegram.edit_callback(
        callback_query,
        messages["start-new"].format(days=test_days),
        reply_markup=kbs.inline.user_start_new
        )


@router.callback_query(cb.UserCallback.filter(F.action == "start"))
async def cb_start(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    state: FSMContext, user: User
    ) -> None:
    """⭐"""
    await _telegram.clean_state(state)
    user_balances = await business.get_user_balances(user)
    marzban_user = await business.get_user_marzban(user.marzban_username)
    msg_id = "start-success" if marzban_user.status == "active" else "start-expired"
    await _telegram.edit_callback(
        callback_query,
        messages[msg_id].format(
            marzban_username=user.marzban_username, user_balance=user_balances,
            sub_date=datetime.fromtimestamp(marzban_user.expire).strftime("%d.%m.%Y"),
            subscription_url=marzban_user.subscription_url
            ),
        reply_markup=kbs.inline.user
        )


@router.message(Command(BotCommands.pay.name))
async def cmd_pay(message: Message, state: FSMContext, user: User) -> None:
    """⭐"""
    await message.answer(
        messages[BotCommands.pay.name],
        reply_markup=await kbs.inline.build_pay_plans(business.get_pay_plans())
        )
    await state.set_state(st.PayPlanForm.payplan_choice)


@router.callback_query(cb.UserCallback.filter(F.action == "pay"))
async def cb_pay(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    state: FSMContext, user: User
    ) -> None:
    """⭐"""
    await _telegram.edit_callback(
        callback_query, messages[BotCommands.pay.name],
        reply_markup=await kbs.inline.build_pay_plans(business.get_pay_plans())
        )
    await state.set_state(st.PayPlanForm.payplan_choice)

@router.callback_query(
    cb.PayPlanCallback.filter(F.action == "choice-pay-plan"),
    st.PayPlanForm.payplan_choice
    )
async def cb_choice_pay_plan(
    callback_query: CallbackQuery,
    callback_data: cb.PayPlanCallback,
    state: FSMContext
    ) -> None:
    """⭐"""
    payplan_id = callback_data.value
    await state.update_data(payplan_id=payplan_id)
    pay_plan = await business.get_pay_plan(payplan_id)

    await state.update_data(view_days_duration=pay_plan.days_duration)

    if len(pay_plan.prices) == 1:
        pay_plan_price = pay_plan.prices[0]
        await state.update_data(payment_method=pay_plan_price.payment_method)

        user_has_balance = await business.check_user_balance(
            callback_query.from_user.id, pay_plan_price.currency_code, pay_plan_price.price
            )
        if user_has_balance:
            user = await business.get_user(telegram_id=callback_query.from_user.id)
            user_balances = await business.get_user_balances(user)
            await _telegram.edit_callback(
                callback_query,
                messages["pay-plan-balance"].format(
                    pay_plan_name=pay_plan.name,
                    pay_plan_price=pay_plan_price.price_short,
                    pay_plan_currency_symbol=pay_plan_price.currency.symbol,
                    user_balance=user_balances
                    ), reply_markup=kbs.inline.yes_no_menu
                )
            await state.update_data(
                pay_plan_name=pay_plan.name,
                pay_plan_price=pay_plan_price.price_short,
                pay_plan_currency_symbol=pay_plan_price.currency.symbol
                )
            await state.set_state(st.PayPlanForm.write_off_balance)
        else:
            await _telegram.edit_callback(
                callback_query,
                messages["pay-plan"].format(
                    pay_plan_name=pay_plan.name,
                    pay_plan_price=pay_plan_price.price_short,
                    pay_plan_currency_symbol=pay_plan_price.currency.symbol
                    ), reply_markup=kbs.inline.yes_no_menu
                )
            await state.set_state(st.PayPlanForm.accept_choice)
        return

    await _telegram.edit_callback(
        callback_query, messages["pay-method"],
        reply_markup=kbs.inline.build_pay_plan_prices(pay_plan)
        )
    await state.set_state(st.PayPlanForm.pay_method_choice)


@router.callback_query(
    cb.PayPlanCallback.filter(F.action == "choice-pay-method"),
    st.PayPlanForm.pay_method_choice
    )
async def cb_choice_pay_method(
    callback_query: CallbackQuery,
    callback_data: cb.PayPlanCallback,
    state: FSMContext
    ) -> None:
    """⭐"""
    pay_method = callback_data.value
    await state.update_data(payment_method=pay_method)
    data = await state.get_data()
    pay_plan = await business.get_pay_plan(data.get("payplan_id"))
    for pay_plan_price in pay_plan.prices:
        if pay_plan_price.payment_method == pay_method:
            user_has_balance = await business.check_user_balance(
                callback_query.from_user.id, pay_plan_price.currency_code,
                pay_plan_price.price
                )
            if user_has_balance:
                await _telegram.edit_callback(
                    callback_query,
                    messages["pay-plan-balance"].format(
                        pay_plan_name=pay_plan.name,
                        pay_plan_price=pay_plan_price.price_short,
                        pay_plan_currency_symbol=pay_plan_price.currency.symbol
                    )
                    , reply_markup=kbs.inline.yes_no_menu)
                await state.update_data(
                    pay_plan_name=pay_plan.name,
                    pay_plan_price=pay_plan_price.price_short,
                    pay_plan_currency_symbol=pay_plan_price.currency.symbol
                    )
                await state.set_state(st.PayPlanForm.write_off_balance)
            else:
                await _telegram.edit_callback(
                    callback_query,
                    messages["pay-plan"].format(
                        pay_plan_name=pay_plan.name,
                        pay_plan_price=pay_plan_price.price_short,
                        pay_plan_currency_symbol=pay_plan_price.currency.symbol
                    )
                    , reply_markup=kbs.inline.yes_no_menu)
                await state.set_state(st.PayPlanForm.accept_choice)
            return


@router.callback_query(
    cb.YesNoCallback.filter(),
    st.PayPlanForm.write_off_balance
    )
async def cb_write_off_balance(
    callback_query: CallbackQuery,
    callback_data: cb.YesNoCallback,
    state: FSMContext
    ) -> None:
    """⭐"""
    state_data = await state.get_data()
    if callback_data.value:
        services_access = await business.check_services_access()
        if not services_access:
            logger.error("Some services are not available")
            return
        payment = await business.create_payment(callback_query.from_user.id, **state_data)
        _ = await business.update_user_after_pay_no_provider(callback_query.from_user.id, payment.id)
        await callback_query.message.answer(
            messages["pay-success"].format(days_duration=state_data["view_days_duration"]),
            reply_markup=kbs.inline.user_start
            )
        await _telegram.clean_state(state)
    else:
        await _telegram.edit_callback(
            callback_query,
            messages["pay-plan"].format(**state_data),
            reply_markup=kbs.inline.yes_no_menu
            )
        await state.set_state(st.PayPlanForm.accept_choice)


@router.callback_query(
    cb.YesNoCallback.filter(),
    st.PayPlanForm.accept_choice
    )
async def cb_accept_choice(
    callback_query: CallbackQuery,
    callback_data: cb.YesNoCallback,
    state: FSMContext
    ) -> None:
    """⭐"""
    state_data = await state.get_data()
    await _telegram.clean_state(state)
    if callback_data.value:
        payment = await business.create_payment(callback_query.from_user.id, **state_data)
        await _telegram.send_invoice(callback_query, payment)
        await state.update_data(view_days_duration=state_data["view_days_duration"])
    else:
        await callback_query.answer(text=messages["pay-no"]) # show_alert=True
        await _telegram.edit_callback(
            callback_query, messages[BotCommands.pay.name],
            reply_markup=await kbs.inline.build_pay_plans(business.get_pay_plans())
            )
        await state.set_state(st.PayPlanForm.payplan_choice)


@router.pre_checkout_query()
async def payment_pre_checkout_query(pre_checkout_query: PreCheckoutQuery) -> None:
    """⭐"""
    try:
        services_access = await business.check_services_access()
        if not services_access:
            raise Exception("Some services are not available")
        await pre_checkout_query.answer(ok=True)
    except Exception as exc:
        logger.error(exc)
        await pre_checkout_query.answer(
            ok=False,
            error_message=messages["pay-failed"].format(pay_id=pre_checkout_query.id)
            )


@router.message(F.successful_payment)
async def payment_successful(message: Message, state: FSMContext, bot: Bot) -> None:
    """⭐"""
    state_data = await state.get_data()
    await _telegram.clean_state(state)
    user_id, payment_info = message.from_user.id, message.successful_payment
    user_payment = await business.update_user_after_pay(
        user_id=user_id, payment_info=payment_info, bot=bot
        )
    if not user_payment:
        logger.error(f"Invoice paid, but profile not updated user id: {user_id}, payment_info: {payment_info}")
        await message.answer(messages["error"], reply_markup=kbs.inline.user_start)
        return
    await message.answer(
        messages["pay-success"].format(days_duration=state_data["view_days_duration"]),
        reply_markup=kbs.inline.user_start
        )
    create_task(
        _telegram.broadcast(
            bot,
            messages["admin-alert-pay"].format(
                marzban_username=user_payment.user.marzban_username,
                price=user_payment.payment.price,
                currency=user_payment.payment.currency
                ),
            *settings.telegram.admins_id
            )
        )


@router.callback_query(cb.UserCallback.filter(F.action == "setup"))
async def cb_setup(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    state: FSMContext, user: User
    ) -> None:
    """⭐"""
    await _telegram.edit_callback(
        callback_query, messages["setup-platform"], reply_markup=kbs.inline.user_setup_platform
        )


@router.callback_query(cb.UserCallback.filter(F.action == "setup-platform"))
async def cb_setup_platform(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    state: FSMContext, user: User
    ) -> None:
    """⭐"""
    marzban_user = await business.get_user_marzban(user.marzban_username)
    if marzban_user is None:
        return
    download_url = business_settings.supported_platforms[callback_data.value]
    add_url = business.define_app_by_url(download_url)
    if add_url is None:
        return
    add_url = business_settings.url_redirect + add_url.format(subscription_url=marzban_user.subscription_url)
    await _telegram.edit_callback(
        callback_query, messages["setup-steps"],
        reply_markup=kbs.inline.build_setup_steps(download_url, add_url)
        )


@router.callback_query(cb.UserCallback.filter(F.action == "setup-help"))
async def cb_setup_help(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    state: FSMContext, user: User
    ) -> None:
    """⭐"""
    marzban_user = await business.get_user_marzban(user.marzban_username)
    if marzban_user is None:
        return
    await _telegram.edit_callback(
        callback_query, messages["setup-help"].format(subscription_url=marzban_user.subscription_url),
        reply_markup=kbs.inline.support_back
        )


@router.callback_query(cb.UserCallback.filter(F.action == "promo"))
async def cb_promo(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    state: FSMContext, user: User
    ) -> None:
    """⭐"""
    _ = await business.get_user_marzban(user.marzban_username)
    await _telegram.edit_callback(callback_query, messages["promo-success"])
    await state.set_state(st.CouponForm.coupon)


@router.message(st.CouponForm.coupon)
async def promo_coupon(message: Message, state: FSMContext) -> None:
    """⭐"""
    await _telegram.clean_state(state)
    user = await business.get_user(telegram_id=message.from_user.id)
    filters = schemas.UsageCoupon(
        user_id=user.id, coupon_id=message.text.strip().upper()
        ).dict()
    coupon, coupon_usage, coupon_breaked_limit = await business.get_coupon_and_coupon_usage(**filters)
    if coupon is None:
        await message.answer(messages["promo-coupon-not-exists"], reply_markup=kbs.inline.user_promo)
        return
    if coupon_usage is not None:
        await message.answer(messages["promo-coupon-is-used"], reply_markup=kbs.inline.user_promo)
        return
    if coupon_breaked_limit:
        await message.answer(messages["promo-coupon-is-limit"], reply_markup=kbs.inline.user_promo)
        return
    coupon_usage_created = await business.create_coupon_usage(**filters)
    updated_user_marzban = await business.update_user_marzban(
        user.marzban_username, coupon.days_duration
        )
    if coupon_usage_created and updated_user_marzban:
        await message.answer(
            messages["promo-coupon"].format(
                days_duration=coupon.days_duration, days_say=days_verbose(coupon.days_duration)
                )
            )
        user_balances = await business.get_user_balances(user)
        marzban_user = await business.get_user_marzban(user.marzban_username)
        msg_id = "start-success" if marzban_user.status == "active" else "start-expired"
        await message.answer(
            messages[msg_id].format(
                marzban_username=user.marzban_username, user_balance=user_balances,
                sub_date=datetime.fromtimestamp(marzban_user.expire).strftime("%d.%m.%Y"),
                subscription_url=marzban_user.subscription_url
                ),
            reply_markup=kbs.inline.user,
            disable_web_page_preview=True
            )
        return


@router.callback_query(cb.UserCallback.filter(F.action == "invite"))
async def cb_invite(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    user: User
    ) -> None:
    """⭐"""
    user_balances = await business.get_user_balances(user)
    invite_url = _telegram.create_ref_link(telegram_id=callback_query.from_user.id)
    invited_users = await business.get_invited_users(callback_query.from_user.id)
    referral_balance = await business.get_referral_balance(user.id)
    await _telegram.edit_callback(
        callback_query,
        messages["invite"].format(
            user_balance=user_balances, referral_balance=referral_balance,
            invite_url=invite_url, invited_users=invited_users,
            referral_percent=business_settings.referral_percent_text
            ),
        reply_markup=kbs.inline.build_referral(invite_url)
        )


@router.message(Command(BotCommands.help.name))
async def cmd_help(message: Message, user: User) -> None:
    """⭐"""
    await message.answer(messages["help"], reply_markup=kbs.inline.support)


@router.callback_query(cb.UserCallback.filter(F.action == "help"))
async def cb_help(
    callback_query: CallbackQuery, callback_data: cb.UserCallback,
    user: User
    ) -> None:
    """⭐"""
    await _telegram.edit_callback(callback_query, messages["help"], reply_markup=kbs.inline.support)
