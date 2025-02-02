import contextlib
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)

def db_backup():
    logger.info('Running database backup...')
    try:
        call_command('dbbackup')
        logger.info('Database backup completed successfully.')
    except Exception as e:
        logger.error(f'Error during database backup: {e}')

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    job_id = 'weekly_backup'

    try:
        scheduler.get_job(job_id)
        logger.info(f'Job {job_id} already exists, skipping creation.')
    except ConflictingIdError:
        logger.error(f'Conflicting job ID {job_id}, skipping job addition.')
    except Exception as e:
        # Job doesn't exist, add it
        scheduler.add_job(db_backup, 'interval', seconds=1, jobstore='default', id=job_id, replace_existing=False)

    register_events(scheduler)
    scheduler.start()
    logger.info('Scheduler started successfully')

