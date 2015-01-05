from __future__ import absolute_import
from celery.app import shared_task as shared_task_celery
from logger.models import Log
import inspect, sys, traceback
import time
from pprint import pformat
from celery.utils.log import get_task_logger
from celery.exceptions import TimeoutError

logger = get_task_logger(__name__)

@shared_task_celery
def error_handler(uuid, con, subsystem, startTime, args, kwargs):
    elapsedTime = time.time() - startTime
    logger.info(uuid)
    result = con.AsyncResult(uuid)
    exc = None
    message = 'Task failed. Arguments:\n{}\n{}'.format(pformat(args), pformat(kwargs))
    try:
        exc = result.get(propagate=False, timeout=1)
        message = 'Task {} raised exception: {}\n{}. \n'.format(uuid, exc, result.traceback)+message
    except TimeoutError:
        pass
    Log.error(subsystem, message, elapsed_time=elapsedTime)

@shared_task_celery
def callback(res, subsystem, startTime, args, kwargs):
    elapsedTime = time.time() - startTime
    Log.info(subsystem, 'Completed with arguments:\n{}\n{}'.format(pformat(args), pformat(kwargs)), elapsed_time=elapsedTime)

def shared_task(constructor):
    con = shared_task_celery(constructor)
    try:
        frm = inspect.stack()[1]
        name = inspect.getmodule(frm[0]).__name__
    except:
        name = __name__
    subsystem = 'atmospherics.{}.{}'.format(name, con.__name__)

    def alias(*args, **kwargs):
        elapsedTime = None
        try:
            startTime = time.time()
            res = con(*args, **kwargs)
            elapsedTime = time.time() - startTime
        except Exception:
            err = ''.join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
            Log.error(subsystem, 'Error Detected in {}:\n{}. Arguments:\n{}\n{}'.format(subsystem, err, pformat(args), pformat(kwargs)))

        Log.info(subsystem, 'Completed with arguments:\n{}\n{}'.format(pformat(args), pformat(kwargs)), elapsed_time=elapsedTime)
        return res

    def alias_delay(*args, **kwargs):
        startTime = time.time()
        res = None
        try:
            res = con.apply_async(link=callback.s(subsystem, startTime, args, kwargs), link_error=error_handler.s(con, subsystem, startTime, args, kwargs), args=args, kwargs=kwargs)
        except Exception as e:
            err = ''.join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
            Log.error(subsystem, 'Error Detected in {}:\n{}. Arguments:\n{}\n{}'.format(subsystem, err, pformat(args), pformat(kwargs)))
        return res

    con.on_failure = lambda self,*args,**kwargs:None

    alias.delay = alias_delay
    return alias




#Copyright 2014-present lossofgenerality.com