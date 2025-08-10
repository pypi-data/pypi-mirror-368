# -*- coding: utf-8 -*-
import os
from contextlib import asynccontextmanager
from logging import getLogger

from aiogram.exceptions import TelegramRetryAfter
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

from vpnflow.bot.base import create_dispatcher, on_shutdown_bot, on_startup_bot
from vpnflow.settings import settings
from vpnflow.web.views import ROUTERS

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """⭐"""
    pid = os.getpid()
    app.settings = settings
    app.bot_dispatcher = create_dispatcher()
    app.bot = app.bot_dispatcher.bot
    try:
        logger.info(f"Webserver startup: {pid}")
        await on_startup_bot(app.bot, app.bot_dispatcher)
        yield
        logger.info(f"Webserver on_shutdown: {pid}")
        await on_shutdown_bot(app.bot, app.bot_dispatcher)
    except TelegramRetryAfter as exc:
        logger.error(exc)
    except Exception as exc:
        logger.error(f"{type(exc)}. {exc}")
    finally:
        pass


app = FastAPI(**{**settings.webserver.dict(), **{"lifespan": lifespan}})
if settings.webserver.static_url and os.path.exists(settings.webserver.static_dir):
    app.mount(
        settings.webserver.static_url,
        StaticFiles(directory=settings.webserver.static_dir), name="static"
        )
if settings.webserver.templates_dir and os.path.exists(settings.webserver.templates_dir):
    app.templates = Jinja2Templates(directory=settings.webserver.templates_dir)
for router in ROUTERS:
    app.include_router(router)
Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def exception_handling(request: Request, call_next):
    """⭐"""
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(exc)
        return JSONResponse({"message": "error"}, status_code=500)
