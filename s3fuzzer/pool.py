from .util.log import Log
from .util.conf import config
from .worker import worker_func
import uuid

_log = Log('pool')

def sync_execute_operations(ops):
    return list(map(worker_func, ops))


execute_operations = sync_execute_operations
