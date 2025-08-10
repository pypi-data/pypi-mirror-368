# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field


class BaseSchemaModel(BaseModel):
    """⭐"""

    model_config = ConfigDict(from_attributes=True, validate_assignment=True, populate_by_name=True)


class User(BaseSchemaModel):
    """⭐"""
    id: Optional[int] = None
    ts_created: Optional[datetime] = None
    ts_updated: Optional[datetime] = None
    telegram_id: int
    marzban_username: Optional[str] = None
    payplan_id: Optional[int] = None
    referral_id: Optional[int] = None


class UserTelegram(BaseSchemaModel):
    """⭐"""
    id: Optional[int] = None
    name: Optional[str] = None
    name_full: Optional[str] = None
    language_code: Optional[str] = None
    is_bot: Optional[bool] = None
    is_premium: Optional[bool] = None


class Referral(BaseSchemaModel):
    """⭐"""
    id: Optional[int] = None
    telegram_start: str
    telegram_id: Optional[int] = None


class PayPlan(BaseSchemaModel):
    """⭐"""
    id: Optional[int] = None
    name: str
    days_duration: int
    data_limit_gb: int
    data_limit_reset_strategy: str
    is_active: Optional[bool] = None


class PayPlanPrice(BaseSchemaModel):
    """⭐"""
    payplan_id: int
    payment_method: str
    price: Decimal
    currency_code: str


class PayPlanPriceCurrency(BaseSchemaModel):
    """⭐"""
    code: str
    symbol: str


class PayPlanPriceView(PayPlanPrice):
    """⭐"""
    currency: PayPlanPriceCurrency

    @computed_field
    def price_short(self) -> int:
        """⭐"""
        return int(self.price)


class PayPlanView(PayPlan):
    """⭐"""
    prices: Optional[List[PayPlanPriceView]] = []

    @computed_field
    def button_text(self) -> str:
        """⭐"""
        prices = ' | '.join(
            (f"{int(price.price)} {price.currency.symbol or price.currency_code}" for price in self.prices)
            )
        months = self.days_duration // 30
        if months > 1:
            prices_per_month = '/'.join(
                (f"{int(price.price / months)}{price.currency.symbol or price.currency_code}" for price in self.prices)
                )
            return f"{self.name} - {prices}\n({prices_per_month}/мес.)"
        return f"{self.name} - {prices}"

    @computed_field
    def data_limit(self) -> int:
        """⭐"""
        return 2 ** 30 * self.data_limit_gb


class Coupon(BaseSchemaModel):
    """⭐"""
    id: str
    days_duration: int
    is_active: Optional[bool] = None
    usage_limit: Optional[int] = None


class UsageCoupon(BaseSchemaModel):
    """⭐"""
    user_id: int
    coupon_id: str


class Payment(BaseSchemaModel):
    """⭐"""
    id: Optional[UUID] = None
    ts_created: Optional[datetime] = None
    ts_updated: Optional[datetime] = None
    payplan_id: int
    payment_method: str
    price: int
    currency: str
    paid: Optional[bool] = None
    title: str
    telegram_payment_charge_id: Optional[str] = None
    provider_payment_charge_id: Optional[str] = None


class UserPayment(BaseSchemaModel):
    """⭐"""
    user_id: int
    payment_id: UUID


class UserBalance(BaseSchemaModel):
    """⭐"""
    id: Optional[int] = None
    user_id: int
    currency: str
    amount: Optional[Decimal] = None


class UserBalanceView(UserBalance):
    """⭐"""
    symbol: Optional[str] = None

    @computed_field
    def text(self) -> str:
        """⭐"""
        return f"{int(self.amount)} {self.symbol or self.currency}"


class ReferralPayment(BaseSchemaModel):
    """⭐"""
    ts_created: Optional[datetime] = None
    user_id: int
    referral_id: int
    amount: Decimal
    currency: str


class MarzbanUserCreate(BaseSchemaModel):
    """⭐"""
    username: str
    note: Optional[str] = ""
    proxies: Dict
    data_limit: int
    expire: int
    data_limit_reset_strategy: str = "no_reset"
    inbounds: Dict


class MarzbanResponse(BaseSchemaModel):
    """⭐"""

    model_config = ConfigDict(extra="allow")


class MarzbanUserCreated(MarzbanResponse):
    """⭐"""
    username: str
    links: List[str]
    subscription_url: str


class YookassaProviderDataReceiptItem(BaseSchemaModel):
    """⭐"""
    description: str
    quantity: int = 1
    amount: Dict
    vat_code: int = 1
    payment_mode: str = "full_payment"
    payment_subject: str = "commodity"


class YookassaProviderDataReceipt(BaseSchemaModel):
    """⭐"""
    items: List[YookassaProviderDataReceiptItem]
    tax_system_code: int = 1


class YookassaProviderData(BaseSchemaModel):
    """⭐"""
    receipt: YookassaProviderDataReceipt
