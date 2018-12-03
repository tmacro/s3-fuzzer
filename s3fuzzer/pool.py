from .util.log import Log
from .util.conf import config
from .worker import worker_func
import uuid
from threading import Thread
import time
from datetime import datetime
from .util.error import WorkloadTimeoutError
from queue import Queue

_log = Log('pool')



def sync_execute_operations(ops):
    return list(map(worker_func, ops))


BACKGROUND_RESULTS = Queue()
def background_execute_operations(ops):
    res = list(map(worker_func, ops))
    BACKGROUND_RESULTS.put(res)

execute_operations = sync_execute_operations

def timed_execute_operations(ops, timeout=5):
    start_time = datetime.utcnow()
    wrkr = Thread(target=background_execute_operations, args=(ops,))
    wrkr.start()
    wrkr.join(timeout=timeout)
    stop_time = datetime.utcnow()
    _log.info('--Operation took: %s'%(stop_time - start_time))
    if wrkr.is_alive():
        raise WorkloadTimeoutError()
    res = BACKGROUND_RESULTS.get()
    return res
