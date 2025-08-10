# -*- coding: utf-8 -*-
from datetime import datetime
from logging import getLogger

from aiogram.types import Update
from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic_core._pydantic_core import ValidationError

from vpnflow.settings import settings

logger = getLogger(__name__)

base, swagger, telegram = APIRouter(), APIRouter(), APIRouter(prefix="/api/webhook")
ROUTERS = [base, telegram]
if settings.webserver.swagger_routes:
    ROUTERS.append(swagger)


@base.get("/", description="Index page")
def index(request: Request):
    """⭐"""
    return {"ts": datetime.utcnow()}


@swagger.get("/docs", include_in_schema=False)
async def docs(request: Request) -> HTMLResponse:
    """⭐"""
    return get_swagger_ui_html(
        openapi_url=request.app.openapi_url, title=request.app.title,
        swagger_js_url=f"{settings.webserver.static_url}/js/swagger-ui-bundle.js",
        swagger_css_url=f"{settings.webserver.static_url}/css/swagger-ui.css",
        swagger_favicon_url=f"{settings.webserver.static_url}/icons/favicon.ico",
        )


@swagger.get("/redoc", include_in_schema=False)
async def redoc(request: Request) -> HTMLResponse:
    """⭐"""
    return get_redoc_html(
        openapi_url=request.app.openapi_url, title=request.app.title, with_google_fonts=False,
        redoc_js_url=f"{settings.webserver.static_url}/js/swagger-redoc.standalone.js",
        redoc_favicon_url=f"{settings.webserver.static_url}/icons/favicon.ico"
        )


@telegram.post("/")
async def bot_webhook(request: Request):
    """⭐"""
    resp_client_400 = JSONResponse({"message": "Bad request"}, status_code=400)
    logger.debug("Webhook processing start")
    rq_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if rq_token != settings.telegram.webhook_secret_token.get_secret_value():
        logger.error(f"Bad request from {request.client.host}")
        return resp_client_400
    update = await request.json()
    try:
        update = Update.model_validate(update, context={"bot": request.app.bot})
    except ValidationError as exc:
        logger.exception(exc)
        logger.error(f"Bad request from {request.client.host}")
        return resp_client_400
    else:
        await request.app.bot_dispatcher.feed_update(request.app.bot, update)
        logger.debug("Webhook processing end")
        return JSONResponse({"message": "ok"}, status_code=200)
