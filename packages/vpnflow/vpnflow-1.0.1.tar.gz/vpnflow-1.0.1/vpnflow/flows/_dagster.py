# -*- coding: utf-8 -*-
from dagster import (DefaultScheduleStatus, Definitions, RetryPolicy,
                     ScheduleDefinition, job, op)

from vpnflow.flows.base import notify_users
from vpnflow.settings import settings


@op(
    retry_policy=RetryPolicy(
        max_retries=settings.flows.notify_users_retry_max,
        delay=settings.flows.notify_users_retry_delay
        )
    )
def op_notify_users():
    """⭐"""
    notify_users()


@job
def job_notify_users():
    """⭐"""
    op_notify_users()


schedule_notify_users = ScheduleDefinition(
    cron_schedule=settings.flows.notify_users_cron, name="notify_users",
    description="Notify in telegram soon expired users",
    job=job_notify_users, execution_timezone="UTC",
    default_status=DefaultScheduleStatus.RUNNING
)


definitions = Definitions(
    schedules=[schedule_notify_users],
    jobs=[job_notify_users]
)
