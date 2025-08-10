# -*- coding: utf-8 -*-
from logging import getLogger

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

logger = getLogger(__name__)


@event.listens_for(Engine, "connect")
def on_connect(conn, conn_record):
    """⭐"""
    logger.debug(f"Open DBAPI connection: {conn}")


@event.listens_for(Engine, "close")
def on_close(conn, conn_record):
    """⭐"""
    logger.debug(f"Close DBAPI connection: {conn}")


@event.listens_for(Engine, "before_execute")
def on_before_execute(
    conn,
    clauseelement,
    multiparams,
    params,
    execution_options
    ):
    """⭐"""
    logger.debug("Before execute")


@event.listens_for(Session, "before_commit")
def on_before_commit(session):
    """⭐"""
    logger.debug("Before commit")


@event.listens_for(Session, "after_commit")
def on_after_commit(session):
    """⭐"""
    logger.debug("Before commit")
