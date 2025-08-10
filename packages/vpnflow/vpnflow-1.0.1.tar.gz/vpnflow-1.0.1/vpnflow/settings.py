# -*- coding: utf-8 -*-
from datetime import timezone
from decimal import Decimal
from typing import Dict, List, Optional, final

from pydantic import SecretStr, ValidationInfo, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from vpnflow import __author__, __email__, __version__
from vpnflow.misc import load_yaml


class SecretMixin:
    """⭐"""

    class Config:
        """⭐"""

        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}
        extra = "ignore"


class _BaseSettings(BaseSettings, SecretMixin):
    """⭐"""


class DatabaseSettings(_BaseSettings):
    """⭐"""
    sqlalchemy_url: SecretStr
    sqlalchemy_engine_params: Dict = {}


class CacheSettings(_BaseSettings):
    """⭐"""
    redis_url: Optional[SecretStr] = ""
    default_ttl: int = 10


class WebServerSettings(_BaseSettings):
    """⭐"""
    host: str = "127.0.0.1"
    port: int = 80
    workers: int = 1
    reload: bool = False
    debug: bool = False
    docs_url: str = ""
    redoc_url: str = ""
    openapi_url: str = "/openapi.json"
    version: str = __version__
    title: str = "vpnflow"
    description: str = ""
    summary: str = ""
    contact: dict = {"name": __author__, "email": __email__}
    static_url: str = ""
    static_dir: str = ""
    templates_dir: str = ""
    swagger_routes: bool = False


class TelegramSettings(_BaseSettings):
    """⭐"""
    bot_name: str
    bot_token: SecretStr
    admins_id: List[int] = []
    log_chat: Optional[int] = None
    provider_token_yookassa: SecretStr
    provider_need_email: bool = True
    provider_send_email_to_provider: bool = True
    rate_limit: float = 0.5
    webhook_use: Optional[bool] = False
    webhook_url_base: str = ""
    webhook_path: str = ""
    webhook_port: int = -1
    webhook_url: str = ""
    webhook_max_connections: int = 50
    webhook_secret_token: Optional[SecretStr] = ""
    messages_path: str = ""
    messages: Dict = {}
    redis_url: Optional[SecretStr] = ""
    blacklist: List = []

    @field_validator("bot_token", mode="before")
    def validate_bot_token(cls, raw: str) -> str:
        """⭐"""
        assert len(raw) == 46
        s1, s2 = raw.split(":")
        assert len(s1) == 10 and len(s2) == 35
        return raw

    @field_validator("webhook_url", mode="before")
    def build_webhook_url(cls, value, info: ValidationInfo) -> str:
        """⭐"""
        values = info.data
        if values.get("webhook_use"):
            url_base = values['webhook_url_base']
            url_path = values['webhook_path']
            port = values['webhook_port']
            if "localhost" in url_base:
                return f"{url_base}:{port}{url_path}"
            return f"{url_base}{url_path}"
        return ""

    @field_validator("messages", mode="before")
    def load_messages(cls, value, info: ValidationInfo) -> dict:
        """⭐"""
        values = info.data
        if values.get("messages_path"):
            return load_yaml(values.get("messages_path"))
        return {}


class MarzbanSettings(_BaseSettings):
    """⭐"""
    host_api: str
    username: str
    password: SecretStr
    token_expire: int
    verify_ssl: bool
    sqlalchemy_url: Optional[SecretStr] = ""


class BusinessSettings(_BaseSettings):
    """⭐"""
    referral_percent: Decimal = Decimal(0)
    test_days: int
    test_traffic_gb_limit: int
    test_proxies: Dict = {}
    test_inbounds: Dict
    url_user_agreement: str
    url_privacy_policy: str
    url_faq: str
    url_support: str
    url_redirect: str
    primary_currency: str = "RUB"
    supported_platforms: Dict
    supported_apps: Dict
    default_desc: Optional[str] = ""
    username_len: Optional[int] = 10

    @computed_field
    def referral_percent_text(self) -> str:
        """⭐"""
        return str(int(self.referral_percent * 100))


class FlowsSettings(_BaseSettings):
    """⭐"""
    notify_users_cron: str = ""
    notify_users_days: List[int] = []
    notify_users_retry_max: int = 1
    notify_users_retry_delay: int = 1


@final
class Settings(BaseSettings, SecretMixin):
    """⭐"""
    tz: timezone = timezone.utc
    database: DatabaseSettings
    cache: CacheSettings
    webserver: WebServerSettings = {}
    telegram: TelegramSettings
    marzban: MarzbanSettings = {}
    business: BusinessSettings
    flows: FlowsSettings = {}

    model_config = SettingsConfigDict(
        extra="allow", env_file=".env",
        env_nested_delimiter="__", env_file_encoding="utf-8",
    ) # env_prefix="APP_"


settings = Settings()
