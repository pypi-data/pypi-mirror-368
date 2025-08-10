# -*- coding: utf-8 -*-
from redis.asyncio import ConnectionPool, Redis


def create_client(url: str) -> Redis:
    """⭐"""
    return Redis(connection_pool=ConnectionPool.from_url(url=url))
