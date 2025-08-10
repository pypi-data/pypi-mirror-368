# -*- coding: utf-8 -*-
import datetime
from logging import getLogger

from sqlalchemy import MetaData, Table, and_, select

from vpnflow.db import repositories as repo
from vpnflow.db.base import Base, engine_w, run_session
from vpnflow.db.models import User, indexes
from vpnflow.misc import load_yaml

logger = getLogger(__name__)


async def load_external_table(engine, table_name):
    """⭐"""
    async with engine.begin() as conn:
        table = await conn.run_sync(
            lambda conn: Table(table_name, MetaData(), autoload_with=conn)
            )
        logger.debug(f"Table params: {table.params}\nTable keys: {table.c.keys()}")
    return table


async def init_db(args, engine=engine_w):
    """⭐"""
    async with engine.begin() as conn:
        if args.drop:
            await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
        if args.create:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            for index in indexes:
                await conn.run_sync(index.create, checkfirst=True)
    if args.insert:
        async with run_session(engine) as session:
            insert_data = load_yaml(args.insert)

            _ = await repo.PayPlanPriceCurrenciesRepository.add_many(
                session,
                [
                    repo.PayPlanPriceCurrenciesRepository.schema(
                        **row
                        ) for row in insert_data.get("price_currencies", [])
                    ]
                )
            for row in insert_data.get("pay_plans_and_prices", []):
                pay_plan = await repo.PayPlansRepository.add(session, repo.PayPlansRepository.schema(**row))
                _ = await repo.PayPlanPricesRepository.add_many(
                    session,
                    [
                        repo.PayPlanPricesRepository.schema(
                            **{**row_p, **{"payplan_id": pay_plan.id}}
                            ) for row_p in row.get("prices", [])
                        ]
                    )
            _ = await repo.CouponsRepository.add_many(
                session,
                [
                    repo.CouponsRepository.schema(
                        **coupon
                        ) for coupon in insert_data.get("coupons", [])
                    ]
                )


async def get_soon_expired_users(session, users_table, *args):
    """⭐"""
    dt = datetime.datetime.utcnow()
    dt_up = (
        datetime
        .datetime(dt.year, dt.month, dt.day, 23, 59)
        .replace(tzinfo=datetime.timezone.utc)
    )
    for days_future in args:
        _dt_up = (dt_up + datetime.timedelta(days=days_future)).timestamp()
        users = await session.execute(
            select(
                # users_table.c.id,
                users_table.c.username
            )
            .where(
                and_(
                    users_table.c.status == "active",
                    users_table.c.expire >= _dt_up - 86400,
                    users_table.c.expire <= _dt_up
                    )
                )
            )
        yield days_future, (row.username for row in users.fetchall())


async def get_telegram_expired_users(session, soon_expired_users):
    """⭐"""
    async for days_exp, usernames in soon_expired_users:
        query = select(User.telegram_id).where(User.marzban_username.in_(usernames))
        users_id = (await session.execute(query)).scalars().all()
        yield days_exp, users_id


async def get_marzban_users(session, users_table, status):
    """⭐"""
    users = await session.execute(
        select(users_table.c.username).where(users_table.c.status == status)
        )
    return (row.username for row in users.fetchall())
