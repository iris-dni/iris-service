import time
from datetime import datetime
import logging
import gevent

from croniter import croniter


logger = logging.getLogger('cron')


def spawn(job, settings, *args, **kwargs):
    """Span a new cron job

    Arguments:
        job: will be called according to the cron settings string with args and
             kwargs
        settings: a string containing the cron settings. (See
                  https://en.wikipedia.org/wiki/Cron)
    """
    return gevent.spawn(cron_job, job, settings, *args, **kwargs)


def distributed_spawn(job, settings, elector, *args, **kwargs):
    """Spawn a new cron job and run it using an elector
    """
    def exec_distributed(*args, **kwargs):
        if elector.is_elected:
            job(*args, **kwargs)
    return spawn(exec_distributed, settings, *args, **kwargs)


def cron_job(job, settings, *args, **kwargs):
    """Worker loop for one specific cron job.

    This function is spawned whenever one cronjob has been spawned by
    `cron.spawn`. This function will loop forever and process the given job
    whenever its due date is calculated. The given job is only calculated if
    the running instance is elected as worker for the given job.

    Arguments:
        see arguments of function `cron.spawn`
    """
    cron_iter = croniter(settings, datetime.now())
    while True:
        next_exec = cron_iter.get_next()
        sleeptime = _sleep_time(next_exec)
        # sleep for the remain time until the job needs to run
        gevent.sleep(sleeptime)
        # execute the job
        try:
            job(*args, **kwargs)
        except:
            logger.exception('cron job "%r" failed' % job)


def _sleep_time(next_exec):
    """Calculate the time until the next job run

    Note: Tests are using this function to stub the processing times of cron
    jobs.
    """
    return next_exec - time.time()
