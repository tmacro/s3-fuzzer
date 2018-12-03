import uuid
from abc import ABC, abstractmethod
from collections import Iterable, namedtuple
from datetime import datetime

from .ds import Datastore
from .util.log import Log
from .util.s3 import build_zenko_client

_log = Log('workload')

Results = namedtuple('Results', ['started', 'finished', 'duration', 'results'])


class Workload:
    def __init__(self, ops, client):
        self._started = None
        self._finished = None
        self._results = None
        self._ops = ops
        self.__client_factory = client
        self._client = None

    def _start(self):
        self._client = self.__client_factory()
        self._started = datetime.utcnow()

    def _finish(self):
        self._client = None
        self._finished = datetime.utcnow()

    def _parse_outer(self, result):
        return self._parse(*result)

    def _parse(self, result, op):
        return result

    def execute(self):
        self._start()
        self._results = list(map(self._parse_outer, self.workload()))
        self._finish()

    @property
    def ops(self):
        if isinstance(self._ops, list):
            return self._ops
        else:
            return [self._ops,]

    def workload(self):
        for op in self.ops:
            yield op(self._client), op

    @property
    def started(self):
        return self._started is not None

    @property
    def finished(self):
        return self._finished is not None

    @property
    def duration(self):
        if self._started is None:
            raise Exception('Workload has not been started!')
        elif self._finished is None:
            raise Exception('Workload has not finished!')
        return self._finished - self._started

    @property
    def results(self):
        return Results(self.started, self.finished, self.duration, self._results)

class EnvironmentWorkload(Workload):
    def _parse(self, result, op):
        return result.get('VersionId'), op.args

class ListWorkload(Workload):
    def _parse(self, result, op):
        return result


def workload_wrapper(cls = Workload, client = None):
    def inner(op):
        return cls(op, client)
    return inner

# Turns an iterable of operations into Workloads
def build_workloads(itr, cls = Workload, client = None):
    return list(map(workload_wrapper(cls, client), itr))
