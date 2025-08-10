import sys
import time
from logging import getLogger

import schedule

from vpnflow.flows.base import notify_users
from vpnflow.settings import settings

logger = getLogger(__name__)


def scheduled_notify_users():
    """⭐"""
    try:
        notify_users()
    except Exception as exc:
        logger.error(exc)


def _get_time_from_cron(s: str):
    """⭐"""
    m, h, *_ = s.split()
    return f"{h}:{m}"


def run_scheduled_tasks(wait_time: int = 60):
    """⭐"""
    notify_users_time = _get_time_from_cron(settings.flows.notify_users_cron)
    schedule.every().day.at(notify_users_time).do(scheduled_notify_users).tag("daily", "notify")
    try:
        while True:
            logger.info(schedule.get_jobs())
            schedule.run_pending()
            time.sleep(wait_time)
    except (KeyboardInterrupt, SystemExit):
        schedule.clear()
    finally:
        sys.exit()
