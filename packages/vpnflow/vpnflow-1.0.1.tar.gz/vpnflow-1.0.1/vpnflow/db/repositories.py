# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from logging import getLogger
from typing import Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from vpnflow.db import models as orm
from vpnflow.db.base import Base
from vpnflow.settings import settings
from vpnflow.web import schemas

logger = getLogger(__name__)

ModelORM = TypeVar("ModelORM", Base, Base)
ModelSchema = TypeVar("ModelSchema")


class Repository(Generic[ModelORM, ModelSchema]):
    """⭐"""

    model: Type[ModelORM]
    schema: Type[ModelSchema]

    @classmethod
    async def add(cls, session: AsyncSession, instance: ModelSchema) -> ModelORM:
        """⭐"""
        values = instance.model_dump(exclude_unset=True)
        model_obj = cls.model(**values)
        session.add(model_obj)
        await session.flush()
        # await session.commit()
        await session.refresh(model_obj)
        return model_obj

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: List[ModelSchema]):
        """⭐"""
        model_objs = (
            cls.model(
                **instance.model_dump(exclude_unset=True)
                ) for instance in instances
            )
        session.add_all(model_objs)
        await session.flush()
        # await session.commit()
        return model_objs

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by) -> Optional[ModelORM]:
        """⭐"""
        query = select(cls.model).filter_by(**filter_by)
        logger.debug(query)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by) -> Sequence[ModelORM]:
        """⭐"""
        query = select(cls.model).filter_by(**filter_by)
        logger.debug(query)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, filter_by, **values):
        """⭐"""
        query = (
            update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
            .values(**values)
            .execution_options(synchronize_session="fetch")
            # .returning(cls.model)
        )
        logger.debug(query)
        result = await session.execute(query)
        # await session.commit()
        logger.debug(f"Updated {result.rowcount} rows")
        return result

    @classmethod
    async def delete(cls, session: AsyncSession, **filter_by):
        """⭐"""
        query = delete(cls.model).filter_by(**filter_by)
        logger.debug(query)
        result = await session.execute(query)
        # await session.commit()
        logger.debug(f"Deleted {result.rowcount} rows")
        return result

    @classmethod
    async def delete_all(cls, session: AsyncSession):
        """⭐"""
        result = await session.execute(delete(cls.model))
        return result

    @classmethod
    async def count(cls, session: AsyncSession):
        """⭐"""
        result = await session.execute(
            select(func.count()).select_from(cls.model)
            )
        return result.scalar_one_or_none()

    @staticmethod
    async def commit(session: AsyncSession) -> None:
        """⭐"""
        await session.commit()


class UsersTelegramRepository(Repository):
    """⭐"""

    model, schema = orm.UserTelegram, schemas.UserTelegram


class ReferralRepository(Repository):
    """⭐"""

    model, schema = orm.Referral, schemas.Referral

    @classmethod
    async def get_stats_user(cls, session: AsyncSession, telegram_id: int):
        """⭐"""
        query = (
            select(func.count("*").label("c"))
            .where(cls.model.telegram_id == telegram_id)
            )
        result = await session.execute(query)
        return result.scalar_one_or_none()


class UsersRepository(Repository):
    """⭐"""

    model, schema = orm.User, schemas.User

    @classmethod
    async def get_stats(cls, session: AsyncSession):
        """⭐"""
        query = (
            select(func.count("*").label("c"))
            .where(cls.model.marzban_username == None)
            )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_marzban_names(cls, session: AsyncSession):
        """⭐"""
        result = await session.execute(
            select(cls.model.marzban_username)
            .where(cls.model.marzban_username != None)
            )
        return result.scalars().all()

    @classmethod
    async def get_telegram_ids_by_marzban_names(cls, session, marzban_names):
        """⭐"""
        result = await session.execute(
            select(cls.model.telegram_id)
            .where(cls.model.marzban_username.in_(marzban_names))
            )
        return result.scalars().all()

    @classmethod
    async def get_telegram_ids_by_marzban_names_exp(cls, session, marzban_names):
        """⭐"""
        result = await session.execute(
            select(cls.model)
            .where(cls.model.marzban_username.in_(marzban_names))
            )
        for user in result.scalars().all():
            if len(user.payments) > 0:
                yield user.telegram_id

    @classmethod
    async def get_telegram_ids_by_marzban_names_exp_no_pay(cls, session, marzban_names):
        """⭐"""
        result = await session.execute(
            select(cls.model)
            .where(cls.model.marzban_username.in_(marzban_names))
            )
        for user in result.scalars().all():
            if len(user.payments) == 0:
                yield user.telegram_id


class PayPlanPricesRepository(Repository):
    """⭐"""

    model, schema, view = orm.PayPlanPrice, schemas.PayPlanPrice, schemas.PayPlanPriceView


class PayPlanPriceCurrenciesRepository(Repository):
    """⭐"""

    model, schema = orm.PayPlanPriceCurrency, schemas.PayPlanPriceCurrency


class PayPlansRepository(Repository):
    """⭐"""

    model, schema, view = orm.PayPlan, schemas.PayPlan, schemas.PayPlanView


class CouponsRepository(Repository):
    """⭐"""

    model, schema = orm.Coupon, schemas.Coupon


class UsageCouponsRepository(Repository):
    """⭐"""

    model, schema = orm.UsageCoupon, schemas.UsageCoupon

    @classmethod
    async def get_stats(cls, session: AsyncSession, coupon_id):
        """⭐"""
        query = (
            select(func.count("*").label("c"))
            .where(cls.model.coupon_id == coupon_id)
            )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_stats_grouped(cls, session: AsyncSession):
        """⭐"""
        query = (
            select(cls.model.coupon_id, func.count("*"))
            .group_by(cls.model.coupon_id)
            )
        result = await session.execute(query)
        return result.all()


class PaymentsRepository(Repository):
    """⭐"""

    model, schema = orm.Payment, schemas.Payment

    @classmethod
    async def get_stats(
        cls,
        session: AsyncSession,
        currency: str = settings.business.primary_currency
        ):
        """⭐"""
        dt_now = datetime.utcnow()
        dt_today = datetime.combine(dt_now, datetime.min.time())
        query_30d = (
            select(func.sum(cls.model.price).label("s"))
            .where(
                cls.model.ts_created >= dt_now - timedelta(days=30),
                cls.model.paid, cls.model.currency == currency
                )
            )
        query_1d = (
            select(func.sum(cls.model.price).label("s"))
            .where(
                cls.model.ts_created >= dt_today,
                cls.model.paid, cls.model.currency == currency
                )
            )
        query_total = (
            select(func.sum(cls.model.price).label("s"))
            .where(
                cls.model.paid, cls.model.currency == currency
                )
            )
        stats = {}
        for key, query in (
            ("payments_30d", query_30d),
            ("payments_1d", query_1d),
            ("payments_total", query_total)
        ):
            result = await session.execute(query)
            stats[key] = result.scalar_one_or_none() or 0
        return stats


class UserPaymentsRepository(Repository):
    """⭐"""

    model, schema = orm.UserPayment, schemas.UserPayment


class UserBalancesRepository(Repository):
    """⭐"""

    model, schema = orm.UserBalance, schemas.UserBalance


class ReferralPaymentsRepository(Repository):
    """⭐"""

    model, schema = orm.ReferralPayment, schemas.ReferralPayment

    @classmethod
    async def get_user_balance(
        cls,
        session: AsyncSession,
        user_id: int,
        currency: str = settings.business.primary_currency
        ):
        """⭐"""
        query = (
            select(func.sum(cls.model.amount).label("s"))
            .where(
                cls.model.user_id == user_id,
                cls.model.currency == currency
                )
            )
        result = await session.execute(query)
        return result.scalar_one_or_none()
