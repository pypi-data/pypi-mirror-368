# -*- coding: utf-8 -*-
from asyncio import create_task, gather
from asyncio import sleep as asleep
from collections import Counter
from datetime import datetime, timedelta
from functools import reduce
from logging import getLogger
from uuid import UUID

from aiohttp import ClientSession
from sqlalchemy import text

from vpnflow.db import repositories as repo
from vpnflow.db.base import engine_mrzbn, engine_r, engine_w, run_session
from vpnflow.db.tools import (get_marzban_users, get_soon_expired_users,
                              get_telegram_expired_users, load_external_table)
from vpnflow.misc import slice_generator
from vpnflow.services._marzban import Marzban
from vpnflow.services._telegram import broadcast, parse_ref_param_start
from vpnflow.services.cache import DEFAULT_TTL, CacheRepository
from vpnflow.settings import settings
from vpnflow.web import schemas

logger = getLogger(__name__)


async def is_telegram_user_exists(telegram_id: int, engine=engine_r) -> bool:
    """⭐"""
    cache_result = await CacheRepository.get(f"tg_exists:{telegram_id}")
    if cache_result:
        return cache_result
    async with run_session(engine) as session:
        user = await repo.UsersTelegramRepository.find_one_or_none(session, id=telegram_id)
        if user:
            await CacheRepository.set(f"tg_exists:{telegram_id}", True, DEFAULT_TTL)
            return True
    return False


async def create_user_from_telegram(user_data, command_args, engine=engine_r):
    """⭐"""
    tg_user = schemas.UserTelegram(
        id=user_data.id, name=user_data.username, name_full=user_data.full_name,
        is_bot=user_data.is_bot, language_code=user_data.language_code,
        is_premium=user_data.is_premium
        )
    referral = parse_ref_param_start(command_args) if command_args else None
    if referral and referral.telegram_id == tg_user.id:
        referral = None
    async with run_session(engine, commit=True) as session:
        tg_user_created = await repo.UsersTelegramRepository.add(session, tg_user)
        if referral:
            referral_created = await repo.ReferralRepository.add(session, referral)
            user = repo.UsersRepository.schema(
                telegram_id=tg_user_created.id, referral_id=referral_created.id
                )
        else:
            user = repo.UsersRepository.schema(telegram_id=tg_user_created.id)
        user_created = await repo.UsersRepository.add(session, user)
        return user_created


async def create_user_marzban(days, traffic_limit, proxies, inbounds, retries=10):
    """⭐"""
    async with ClientSession() as session:
        headers = await Marzban.auth(session)
        for _ in range(retries):
            username = Marzban.usernames_generator()
            result = await Marzban.request(
                session, "GET", f"/users?limit=10&search={username}", **headers
                )
            # params: offset limit username search status sort
            if result.get("total", 0) == 0:
                result = await Marzban.request(
                    session, "POST", "/user",
                    json=schemas.MarzbanUserCreate(
                        username=username,
                        data_limit=2 ** 30 * traffic_limit,
                        proxies=proxies,
                        inbounds=inbounds,
                        expire=int((datetime.utcnow() + timedelta(days=days)).timestamp())
                        ).dict(), **headers
                    )
                return schemas.MarzbanResponse(**result)


async def update_user(user, engine=engine_w, **values):
    """⭐"""
    await clean_cache(f"user:{user.telegram_id}")
    async with run_session(engine) as session:
        user_updated = await repo.UsersRepository.update(
            session, {"id": user.id}, **values
            )
    return user_updated


async def get_user(telegram_id, engine=engine_r):
    """⭐"""
    cache_result = await CacheRepository.get(f"user:{telegram_id}")
    if cache_result:
        return cache_result
    async with run_session(engine) as session:
        user = await repo.UsersRepository.find_one_or_none(session, telegram_id=telegram_id)
        if user:
            await CacheRepository.set(f"user:{telegram_id}", user, DEFAULT_TTL)
        return user


async def get_user_balances(user, engine=engine_r):
    """⭐"""
    balances = []
    async with run_session(engine) as session:
        for balance in user.balances:
            user_balance = schemas.UserBalanceView.model_validate(balance)
            currency = await repo.PayPlanPriceCurrenciesRepository.find_one_or_none(session, code=balance.currency)
            if not currency:
                logger.warning(f"Can't find currency: {balance.currency}")
                continue
            user_balance.symbol = currency.symbol
            balances.append(user_balance.text)
    return " ".join(balances) if balances else "0"


async def update_user_marzban(marzban_username, days, **kw):
    """⭐"""
    await clean_cache(f"marzban:{marzban_username}")
    async with ClientSession() as session:
        headers = await Marzban.auth(session)

        result = await Marzban.request(session, "GET", f"/user/{marzban_username}", **headers)
        marzban_user = schemas.MarzbanResponse(**result)

        ts_expire = marzban_user.expire
        ts_current = datetime.utcnow().timestamp()
        ts = int(ts_current) if ts_expire < ts_current else ts_expire
        ts += days * 86400 # 24 * 60 * 60
        data = {"status": "active", "expire": ts, **kw}

        result = await Marzban.request(session, "PUT", f"/user/{marzban_username}", json=data, **headers)
        return schemas.MarzbanResponse(**result)


async def get_user_marzban(username):
    """⭐"""
    cache_result = await CacheRepository.get(f"marzban:{username}")
    if cache_result:
        return cache_result
    async with ClientSession() as session:
        headers = await Marzban.auth(session)
        result = await Marzban.request(session, "GET", f"/user/{username}", **headers)
        result = schemas.MarzbanResponse(**result)
        await CacheRepository.set(f"marzban:{username}", result, DEFAULT_TTL)
        return result


async def get_pay_plans(engine=engine_r):
    """⭐"""
    async with run_session(engine) as session:
        for pay_plan in await repo.PayPlansRepository.find_all(session, is_active=True):
            # for pay_plan_price in await pay_plan.awaitable_attrs.prices:
            yield repo.PayPlansRepository.view.model_validate(pay_plan)


async def get_pay_plan(_id: int, engine=engine_r):
    """⭐"""
    _id = int(_id) # callback data str type
    cache_result = await CacheRepository.get(f"payplan:{_id}")
    if cache_result:
        return cache_result
    async with run_session(engine) as session:
        pay_plan = await repo.PayPlansRepository.find_one_or_none(session, **{"id": _id, "is_active": True})
        if not pay_plan:
            logger.warning(f"Can't find pay_plan with id: {_id}")
            return
        pay_plan = repo.PayPlansRepository.view.model_validate(pay_plan)
        await CacheRepository.set(f"payplan:{_id}", pay_plan, DEFAULT_TTL)
        return pay_plan


async def create_payment(telegram_id, engine=engine_r, **state_data):
    """⭐"""
    payplan_id = int(state_data["payplan_id"]) # callback data str type
    async with run_session(engine, commit=True) as session:
        user = await repo.UsersRepository.find_one_or_none(session, telegram_id=telegram_id)
        if not user:
            return
        pay_plan = await repo.PayPlansRepository.find_one_or_none(session, **{"id": payplan_id})
        pay_plan = repo.PayPlansRepository.view.model_validate(pay_plan)
        payment_method = state_data["payment_method"]
        for pay_plan_price in pay_plan.prices:
            if pay_plan_price.payment_method == payment_method:
                payment = await repo.PaymentsRepository.add(
                    session, schemas.Payment(
                        payplan_id=pay_plan.id,
                        payment_method=pay_plan_price.payment_method,
                        price=pay_plan_price.price_short,
                        currency=pay_plan_price.currency_code,
                        title=pay_plan.name
                        )
                    )
                user.payments.append(payment)
                return payment


async def _update_payment_info(payment_info, engine=engine_w):
    """⭐"""
    payment_id = UUID(payment_info.invoice_payload)
    async with run_session(engine) as session:
        _ = await repo.PaymentsRepository.update(
            session, {"id": payment_id},
            telegram_payment_charge_id=payment_info.telegram_payment_charge_id,
            provider_payment_charge_id=payment_info.provider_payment_charge_id,
            paid=True
            )
    return payment_id


async def _update_user_payment(payment_id, engine=engine_r):
    """⭐"""
    async with run_session(engine, commit=True) as session:
        user_payment = await repo.UserPaymentsRepository.find_one_or_none(session, payment_id=payment_id)
        user_balance_filters = {"user_id": user_payment.user.id, "currency": user_payment.payment.currency}
        user_balance = await repo.UserBalancesRepository.find_one_or_none(session, **user_balance_filters)
        if user_balance is None:
            user_balance = await repo.UserBalancesRepository.add(
                session, schemas.UserBalance(**user_balance_filters)
                )
        user_balance.amount += user_payment.payment.price
        await repo.UsersRepository.update(
            session, {"id": user_payment.user.id}, payplan_id=user_payment.payment.payplan_id
            )
    return user_payment, user_balance_filters


async def _update_user_connection(user_payment, engine=engine_r, **user_balance_filters):
    """⭐"""
    async with run_session(engine, commit=True) as session:
        pay_plan = await repo.PayPlansRepository.find_one_or_none(session, id=user_payment.payment.payplan_id)
        user_balance = await repo.UserBalancesRepository.find_one_or_none(session, **user_balance_filters)
        pay_plan_view = repo.PayPlansRepository.view.model_validate(pay_plan)
        _ = await update_user_marzban(
            user_payment.user.marzban_username, pay_plan.days_duration,
            data_limit=pay_plan_view.data_limit,
            data_limit_reset_strategy=pay_plan_view.data_limit_reset_strategy
            )
        user_balance.amount -= user_payment.payment.price
    return True


async def _update_user_referral(user_payment, bot, engine=engine_r, **user_balance_filters):
    """⭐"""
    referral = user_payment.user.referral
    if not(referral and referral.telegram_id): # and len(user_payment.user.payments) == 1
        return True
    async with run_session(engine, commit=True) as session:
        user = await get_user(referral.telegram_id)
        user_balance_filters["user_id"] = user.id
        user_balance = await repo.UserBalancesRepository.find_one_or_none(
            session, **user_balance_filters
            )
        if user_balance is None:
            user_balance = await repo.UserBalancesRepository.add(
                session, schemas.UserBalance(**user_balance_filters)
                )
        payed_amount = user_payment.payment.price * settings.business.referral_percent
        user_balance.amount += payed_amount

        await repo.ReferralPaymentsRepository.add(
            session, schemas.ReferralPayment(
                user_id=user.id, referral_id=referral.id,
                amount=payed_amount, currency=user_payment.payment.currency
                )
            )

    create_task(
        broadcast(
            bot,
            settings.telegram.messages["user-alert-referral"].format(payed_amount=payed_amount),
            referral.telegram_id
            )
        )

    return True


async def update_user_after_pay(user_id, payment_info, bot):
    """⭐"""
    await clean_cache(f"user:{user_id}")
    logger.info(f"Update payment info: {payment_info}")
    payment_id = await _update_payment_info(payment_info)
    logger.info(f"Update user balance for payment id: {payment_id}")
    user_payment, user_balance_filters = await _update_user_payment(payment_id)
    logger.info(f"Update user connection with id: {user_payment.user.id}")
    is_connection_updated = await _update_user_connection(user_payment, **user_balance_filters)
    if not is_connection_updated:
        logger.warning(f"Connection for user: {user_payment.user.id} not updated")
    try:
        is_referral_updated = await _update_user_referral(user_payment, bot, **user_balance_filters)
        if not is_referral_updated:
            logger.warning(f"Referral for user: {user_payment.user.id} not updated")
    except Exception as exc:
        logger.error(f"Can't update referral: {exc}")

    return user_payment


async def update_user_after_pay_no_provider(user_id, payment_id, engine=engine_r):
    """⭐"""
    await clean_cache(f"user:{user_id}")
    async with run_session(engine, commit=True) as session:
        _ = await repo.PaymentsRepository.update(session, {"id": payment_id}, paid=True)

        user_payment = await repo.UserPaymentsRepository.find_one_or_none(session, payment_id=payment_id)
        if user_payment is None:
            logger.warning(f"Can't find payment with id: {payment_id}")
            return

        payment_data = {"user_id": user_payment.user.id, "currency": user_payment.payment.currency}
        user_balance = await repo.UserBalancesRepository.find_one_or_none(session, **payment_data)
        _ = await repo.UsersRepository.update(
            session, {"id": user_payment.user.id}, payplan_id=user_payment.payment.payplan_id
            )

        await session.commit()

        pay_plan = await repo.PayPlansRepository.find_one_or_none(session, id=user_payment.payment.payplan_id)
        pay_plan_view = repo.PayPlansRepository.view.model_validate(pay_plan)
        _ = await update_user_marzban(
            user_payment.user.marzban_username, pay_plan.days_duration,
            data_limit=pay_plan_view.data_limit,
            data_limit_reset_strategy=pay_plan_view.data_limit_reset_strategy
            )
        user_balance.amount -= user_payment.payment.price

        await session.commit()

    return user_payment


async def get_invited_users(telegram_id, engine=engine_r):
    """⭐"""
    cache_result = await CacheRepository.get(f"invited:{telegram_id}")
    if cache_result:
        return cache_result
    async with run_session(engine) as session:
        users_count = await repo.ReferralRepository.get_stats_user(session, telegram_id)
        await CacheRepository.set(f"invited:{telegram_id}", users_count, DEFAULT_TTL)
        return users_count


async def get_coupon_and_coupon_usage(engine=engine_r, **filters):
    """⭐"""
    async with run_session(engine) as session:
        coupon = await repo.CouponsRepository.find_one_or_none(
            session, id=filters["coupon_id"], is_active=True
            )
        coupon_usage = await repo.UsageCouponsRepository.find_one_or_none(session, **filters)
        coupon_breaked_limit = False
        if coupon and coupon.usage_limit is not None:
            used_n = await repo.UsageCouponsRepository.get_stats(session, coupon_id=coupon.id)
            if used_n >= coupon.usage_limit:
                coupon_breaked_limit = True
        return coupon, coupon_usage, coupon_breaked_limit


async def create_coupon_usage(engine=engine_w, **values):
    """⭐"""
    async with run_session(engine) as session:
        coupon_usage_created = await repo.UsageCouponsRepository.add(
            session, repo.UsageCouponsRepository.schema(**values)
            )
        return coupon_usage_created


async def check_services_access(engine=engine_r) -> bool:
    """⭐"""
    async with ClientSession() as session, engine.connect() as connection:
        headers = await Marzban.auth(session)
        marzban_response = await Marzban.request(session, "GET", "/system", **headers)
        db_response = (await connection.execute(text("SELECT 1"))).scalar_one_or_none()
        cache_response = await CacheRepository.check_health()
        if marzban_response is not None and db_response is not None and cache_response:
            return True
    return False


async def get_user_marzban_status(session, username, **headers):
    """⭐"""
    result = await Marzban.request(session, "GET", f"/user/{username}", **headers)
    if result:
        return result["status"]


async def get_stats(engine=engine_r):
    """⭐"""
    cache_result = await CacheRepository.get("admin_stats")
    if cache_result:
        return cache_result
    async with \
        run_session(engine) as session, \
        ClientSession() as http_session, \
        run_session(engine_mrzbn) as session_marzban \
        :
        users_stats = {}
        users_total = await repo.UsersRepository.count(session)
        users_stats["users_total"] = users_total
        users_not_accept = await repo.UsersRepository.get_stats(session)
        users_stats["users_not_accept"] = users_not_accept

        marzban_names = await repo.UsersRepository.get_marzban_names(session)

        headers = await Marzban.auth(http_session)

        status_counters = []
        for sliced_marzban_names in slice_generator(marzban_names, 1000):
            marzban_statuses = await gather(
                *(
                    get_user_marzban_status(
                        http_session, username, **headers
                        ) for username in sliced_marzban_names
                    ), return_exceptions=True
                )
            status_counters.append(Counter(marzban_statuses))
            await asleep(1)
        if status_counters:
            status_counter = reduce(lambda x, y: x + y, status_counters)
        else:
            status_counter = {}
        users_stats["users_online"] = status_counter.get("active", 0)
        users_stats["users_offline"] = sum(
            status_counter.get(status, 0) for status in ("disabled", "expired", "on_hold")
            )

        users_table = await load_external_table(engine_mrzbn, "users")
        soon_expired_marzban_users = get_soon_expired_users(
            session_marzban, users_table, *[1, 2, 3]
            )
        soon_expired_telegram_users = get_telegram_expired_users(session, soon_expired_marzban_users)
        async for days_exp, telegram_ids in soon_expired_telegram_users:
            users_stats[f"users_expired_{days_exp}d"] = len(telegram_ids)

        pay_stats = await repo.PaymentsRepository.get_stats(session)

        coupons_usage_data = await repo.UsageCouponsRepository.get_stats_grouped(session)
        coupons_usage = []
        for c1, c2 in coupons_usage_data:
            coupons_usage.append(f"{c1}: {c2}")
        users_stats["coupons_usage"] = "\n".join(coupons_usage)
        stats = {**users_stats, **pay_stats}
        await CacheRepository.set("admin_stats", stats, DEFAULT_TTL)
        return stats


async def send_stats(bot, telegram_id):
    """⭐"""
    stats = await get_stats()
    await bot.send_message(
        telegram_id,
        settings.telegram.messages["admin-stats"].format(**stats)
        )


async def notify_users(bot, engine=engine_w, **state_data):
    """⭐"""
    notify_group = state_data["notify_group"]
    if notify_group == "all":
        async with run_session(engine) as session:
            users = await repo.UsersRepository.find_all(session)
            users = [user.telegram_id for user in users if user.marzban_username]
    elif notify_group in ("active", "expired"):
        async with \
            run_session(engine) as session, \
            run_session(engine_mrzbn) as session_marzban \
            :
            users_table = await load_external_table(engine_mrzbn, "users")
            marzban_names = await get_marzban_users(session_marzban, users_table, notify_group)
            users = await repo.UsersRepository.get_telegram_ids_by_marzban_names(
                session, marzban_names
                )
    elif notify_group in ("pay-expired", "pay-no-expired"):
        async with \
            run_session(engine) as session, \
            run_session(engine_mrzbn) as session_marzban \
            :
            users_table = await load_external_table(engine_mrzbn, "users")
            marzban_names = await get_marzban_users(session_marzban, users_table, "expired")
            users = []
            if notify_group == "pay-expired":
                users_generator = repo.UsersRepository.get_telegram_ids_by_marzban_names_exp
            else:
                users_generator = repo.UsersRepository.get_telegram_ids_by_marzban_names_exp_no_pay
            async for telegram_id in users_generator(session, marzban_names):
                users.append(telegram_id)
    else:
        users = []
    await broadcast(
        bot, state_data["notify_message"], *users, photo=state_data.get("notify_image")
        )
    return len(users)


async def create_coupon(engine=engine_w, **state_data):
    """⭐"""
    values = {
        "id": state_data["coupon_id"],
        "days_duration": int(state_data["coupon_days"])
        }
    usage_limit = state_data.get("coupon_usage_limit")
    if usage_limit:
        values["usage_limit"] = int(usage_limit)
    async with run_session(engine) as session:
        coupon_exists = await repo.CouponsRepository.find_one_or_none(
            session, **{"id": values["id"]}
            )
        if coupon_exists:
            return
        coupon_created = await repo.CouponsRepository.add(
            session, repo.CouponsRepository.schema(**values)
            )
        return coupon_created


async def get_referral_balance(user_id, engine=engine_r):
    """⭐"""
    cache_result = await CacheRepository.get(f"balance:{user_id}")
    if cache_result:
        return cache_result
    async with run_session(engine) as session:
        user_balance = await repo.ReferralPaymentsRepository.get_user_balance(session, user_id)
        user_balance = round(user_balance, 1) if user_balance else 0
        await CacheRepository.set(f"balance:{user_id}", user_balance, DEFAULT_TTL)
        return user_balance


async def check_user_balance(telegram_id, pay_plan_currency, pay_plan_price, engine=engine_r):
    """⭐"""
    async with run_session(engine) as session:
        user = await repo.UsersRepository.find_one_or_none(session, telegram_id=telegram_id)
        if not user:
            return False
        for balance in user.balances:
            if balance.currency == pay_plan_currency:
                if balance.amount >= pay_plan_price:
                    return True
    return False


async def clean_cache(key: str):
    """⭐"""
    cache_result = await CacheRepository.get(key)
    if cache_result:
        await CacheRepository.delete(key)


def define_app_by_url(url: str):
    """⭐"""
    for app in settings.business.supported_apps:
        if app in url:
            return settings.business.supported_apps[app]
