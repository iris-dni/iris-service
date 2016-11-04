==============
Tests for cron
==============

The cron module provides functionality to execute jobs chronologically.

Defining a cron job
===================

A cronjob consists of a callable with optional arguments and keyword arguments
spawned by `cron.spawn` in a configured interval defined in valid cron syntax
(see https://en.wikipedia.org/wiki/Cron).

Testing setup
-------------

Implement a callable or testing purpose::

    >>> def callable_job(*args, **kwargs):
    ...     print "### job called", args, kwargs

For testing we will mock the calculation of the due date for each job::

    >>> from iris.service import cron
    >>> cron._sleep_time = lambda x: 0.1

Spawning a cron job
-------------------

The given callable_job is called in the interval defined by the given cron
string with the given optionally arguments::

    >>> green = cron.spawn(callable_job, "* * * * *", "any arg", x=42)

    >>> import time
    >>> time.sleep(0.11)
    ### job called ('any arg',) {'x': 42}

    >>> green.kill()

If the job raises any exception the greenlet does not crash::

    >>> def crashing_job(*args, **kwargs):
    ...     print "### this job will fail"
    ...     raise Exception

    >>> green = cron.spawn(crashing_job, "* * * * *", "any arg", x=42)

    >>> time.sleep(0.21)
    ### this job will fail
    ### this job will fail

    >>> green.kill()
