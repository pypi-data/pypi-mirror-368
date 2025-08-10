# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (DECIMAL, TIMESTAMP, VARCHAR, BigInteger, Boolean,
                        ForeignKey, Index, Integer, Text, UniqueConstraint,
                        Uuid, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vpnflow.db.base import Base


class User(Base):
    """⭐"""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("referral_id"),)

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=True)
    ts_created: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    ts_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    telegram_id: Mapped[int] = mapped_column(ForeignKey("users_telegram.id"))
    marzban_username: Mapped[Optional[str]] = mapped_column(VARCHAR(64))
    payplan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    referral_id: Mapped[Optional[int]] = mapped_column(ForeignKey("referrals.id"))

    user_telegram: Mapped["UserTelegram"] = relationship(back_populates="user")
    referral: Mapped["Referral"] = relationship(back_populates="user", lazy="selectin")
    usages_coupons_association: Mapped[List["UsageCoupon"]] = relationship(back_populates="user")
    coupons: Mapped[List["Coupon"]] = relationship(secondary="usage_coupons", back_populates="users")
    user_payments_association: Mapped[List["UserPayment"]] = relationship(back_populates="user")
    payments: Mapped[List["Payment"]] = relationship(secondary="user_payments", back_populates="users", lazy="selectin")
    balances: Mapped[List["UserBalance"]] = relationship(back_populates="user", lazy="selectin")

    referral_payment_association: Mapped[List["ReferralPayment"]] = relationship(back_populates="user")
    referrals: Mapped[List["Referral"]] = relationship(secondary="referral_payments", back_populates="users")


class UserTelegram(Base):
    """⭐"""

    __tablename__ = "users_telegram"

    id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(VARCHAR(64))
    name_full: Mapped[Optional[str]] = mapped_column(VARCHAR(64))
    language_code: Mapped[Optional[str]] = mapped_column(VARCHAR(16))
    is_bot: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_premium: Mapped[Optional[bool]] = mapped_column(Boolean)

    user: Mapped["User"] = relationship(back_populates="user_telegram")


class Referral(Base):
    """⭐"""

    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=True)
    telegram_start: Mapped[str] = mapped_column(Text)
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    user: Mapped["User"] = relationship(back_populates="referral")
    referral_payment_association: Mapped[List["ReferralPayment"]] = relationship(back_populates="referral")
    users: Mapped[List["User"]] = relationship(secondary="referral_payments", back_populates="referrals")


class PayPlan(Base):
    """⭐"""

    __tablename__ = "pay_plans"

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    days_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    data_limit_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    data_limit_reset_strategy: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    prices: Mapped[List["PayPlanPrice"]] = relationship(back_populates="pay_plan", lazy="selectin")


class PayPlanPrice(Base):
    """⭐"""

    __tablename__ = "payplan_prices"

    payplan_id: Mapped[int] = mapped_column(ForeignKey("pay_plans.id"), primary_key=True)
    payment_method: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL)
    currency_code: Mapped[str] = mapped_column(ForeignKey("price_currencies.code"), primary_key=True)

    pay_plan: Mapped["PayPlan"] = relationship(back_populates="prices")
    currency: Mapped["PayPlanPriceCurrency"] = relationship(back_populates="price", lazy="selectin")


class PayPlanPriceCurrency(Base):
    """⭐"""

    __tablename__ = "price_currencies"

    code: Mapped[str] = mapped_column(VARCHAR(16), primary_key=True, unique=True)
    symbol: Mapped[str] = mapped_column(VARCHAR(8))

    price: Mapped["PayPlanPrice"] = relationship(back_populates="currency")


class Coupon(Base):
    """⭐"""

    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(VARCHAR(24), unique=True, primary_key=True)
    days_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    usages_coupons_association: Mapped[List["UsageCoupon"]] = relationship(back_populates="coupon")
    users: Mapped[List["User"]] = relationship(secondary="usage_coupons", back_populates="coupons")


class UsageCoupon(Base):
    """⭐"""

    __tablename__ = "usage_coupons"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    coupon_id: Mapped[str] = mapped_column(ForeignKey("coupons.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="usages_coupons_association")
    coupon: Mapped["Coupon"] = relationship(back_populates="usages_coupons_association")


class Payment(Base):
    """⭐"""

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(Uuid, unique=True, primary_key=True, default=uuid4)
    ts_created: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    ts_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    payplan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_method: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    title: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    telegram_payment_charge_id: Mapped[Optional[str]] = mapped_column(VARCHAR(64), nullable=True)
    provider_payment_charge_id: Mapped[Optional[str]] = mapped_column(VARCHAR(64), nullable=True)

    user_payments_association: Mapped[List["UserPayment"]] = relationship(back_populates="payment")
    users: Mapped[List["User"]] = relationship(secondary="user_payments", back_populates="payments")


class UserPayment(Base):
    """⭐"""

    __tablename__ = "user_payments"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    payment_id: Mapped[UUID] = mapped_column(ForeignKey("payments.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="user_payments_association", lazy="selectin")
    payment: Mapped["Payment"] = relationship(back_populates="user_payments_association", lazy="selectin")


class UserBalance(Base):
    """⭐"""

    __tablename__ = "users_balances"

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    currency: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL, default=Decimal(0))

    user: Mapped["User"] = relationship(back_populates="balances")


class ReferralPayment(Base):
    """⭐"""

    __tablename__ = "referral_payments"

    ts_created: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    referral_id: Mapped[int] = mapped_column(ForeignKey("referrals.id"), primary_key=True)
    amount: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False)
    currency: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)

    user: Mapped["User"] = relationship(back_populates="referral_payment_association")
    referral: Mapped["Referral"] = relationship(back_populates="referral_payment_association")


indexes = (
    Index("idx_users_telegram_id", User.telegram_id),
)
