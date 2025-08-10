# -*- coding: utf-8 -*-
import json
import logging
from asyncio import gather
from asyncio import sleep as asleep
from base64 import urlsafe_b64encode
from urllib.parse import urlparse

from aiogram import Bot
from aiogram.types.labeled_price import LabeledPrice
from aiogram.utils.deep_linking import decode_payload

from vpnflow.misc import slice_generator
from vpnflow.settings import settings
from vpnflow.web.schemas import (Referral, YookassaProviderData,
                                 YookassaProviderDataReceipt,
                                 YookassaProviderDataReceiptItem)

logger = logging.getLogger(__name__)
settings_telegram = settings.telegram


def create_ref_link(bot_name=settings_telegram.bot_name, **kw):
    """⭐"""
    param_start = urlsafe_b64encode(
        json.dumps(kw).encode("UTF-8")
        ).decode("UTF-8").replace("=", "")
    return f"https://t.me/{bot_name}?start={param_start}"


def parse_ref_param_start(param_start):
    """⭐"""
    referral = Referral(telegram_start=param_start)
    try:
        payload = json.loads(decode_payload(param_start))
        referral.telegram_id = payload.get("telegram_id")
    except Exception as exc:
        logger.warning(exc)
    return referral


def parse_ref_link(link):
    """⭐"""
    link_data = dict([f.split("=") for f in urlparse(link).query.split("&")])
    return parse_ref_param_start(link_data.get("start"))


async def send_invoice(callback_query, payment):
    """⭐"""
    price, currency, title, payload = (
        payment.price, payment.currency, payment.title, str(payment.id)
    )
    description = settings_telegram.messages["pay-invoice"]
    is_telegram_pay = currency == "XTR"
    if is_telegram_pay:
        label = currency
    else:
        label = "Оплата"
        price *= 100
    prices = [LabeledPrice(label=label, amount=price)]
    if is_telegram_pay:
        await callback_query.message.answer_invoice(
            title=title, description=description, payload=payload,
            currency=currency, prices=prices # reply_markup=reply_markup
        )
    else:
        provider_token = settings_telegram.provider_token_yookassa.get_secret_value()
        need_email = settings_telegram.provider_need_email
        send_email_to_provider = settings_telegram.provider_send_email_to_provider
        provider_data = YookassaProviderData(
            receipt=YookassaProviderDataReceipt(
                items=[
                    YookassaProviderDataReceiptItem(
                        description=settings.business.default_desc,
                        amount={"value": payment.price, "currency": currency}
                        )
                    ],
                )
            )
        provider_data = json.dumps(provider_data.dict())
        await callback_query.bot.send_invoice(
            chat_id=callback_query.from_user.id, title=title, description=description,
            payload=payload, provider_token=provider_token, currency=currency, prices=prices,
            provider_data=provider_data, need_email=need_email,
            send_email_to_provider=send_email_to_provider # reply_markup=reply_markup
        )


async def clean_state(state) -> None:
    """⭐"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()


async def broadcast(bot: Bot, message: str, *recipients, photo=None):
    """⭐"""
    for sliced_recipients in slice_generator(recipients, 30):
        if photo:
            results = await gather(
                *(
                    bot.send_photo(
                        chat_id=recipient, caption=message, photo=photo
                        ) for recipient in sliced_recipients
                    ),
                return_exceptions=True
            )
        else:
            results = await gather(
                *(
                    bot.send_message(recipient, message) for recipient in sliced_recipients
                    ),
                return_exceptions=True
            )
        for recipient, result in zip(sliced_recipients, results):
            logger.info(f"Broadcast recipient: {recipient}")
            if isinstance(result, Exception):
                logger.warning(str(result))
        await asleep(1)


async def edit_callback(
    callback_query, message, reply_markup=None, disable_web_page_preview=True
    ):
    """⭐"""
    try:
        await callback_query.message.edit_text(
            message, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview
            )
    except Exception as exc:
        logger.warning(exc)
        callback_query.answer()
