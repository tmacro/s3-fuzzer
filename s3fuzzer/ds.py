from collections import defaultdict, OrderedDict
from copy import deepcopy
from .util.log import Log

_log = Log('datastore')

def default_dict_list():
    return defaultdict(list)

class DeleteMarker:
    pass


class Object:
    def __init__(self):
        self._versions = []
        self._current = None
        self._deleted = False

    def __repr__(self):
        return '<Object current:%s, deleted: %s, versions:%s'%(self._current, self._deleted, ', '.join(self._versions))

    def rm_version(self, version):
        if not version in self._versions:
            raise Exception("Can't delete a nonexistent object version!")
        pos = self._versions.index(version)
        self._versions[pos] = DeleteMarker
        # self._versions.remove(version)
        if self._current == version:
            for new_version in filter(lambda x: x is not DeleteMarker, self._versions):
                self._current = version
                break

    def add_version(self, version):
        self._versions.insert(0, version)
        self._current = version

    @property
    def versions(self):
        return list(filter(lambda x: x is not DeleteMarker, self._versions))

    @property
    def deleted(self):
        return self._deleted

    def delete_master(self):
        self._deleted = True

class Bucket(OrderedDict):
    def keys(self, deleted = True):
        if deleted:
            return super().keys()
        return filter(lambda x: not self.get(x).deleted, super().keys())

class Datastore:
    def __init__(self):
        self._buckets = defaultdict(Bucket)

    def __repr__(self):
        return '<Datastore %s'%self._buckets

    def get(self, bucket, key = None, version = None):
        if key is None:
            return self._buckets.get(bucket)
        return self._buckets.get(bucket).get(key)


    def put(self, bucket, key, version = None):
        obj = self._buckets.get(bucket, {}).get(key, None)
        if obj is None:
            obj = Object()
            _log.debug('Creating object at %s/%s'%(bucket, key))
        if version:
            obj.add_version(version)
            _log.debug('Adding version %s to %s/%s'%(version, bucket, key))
        self._buckets[bucket][key] = obj

    def delete_version(self, bucket, key, version):
        _log.debug('Deleting %s/%s %s'%(bucket, key, version))
        obj = self.get(bucket, key)
        if obj is None:
            raise Exception("Can't delete a nonexistent object version!")
        obj.rm_version(version)

    def delete_master(self, bucket, key):
        obj = self.get(bucket, key)
        if obj is None:
            raise Exception("Can't delete a nonexistent object!")
        obj.delete_master()

    def __iter__(self):
        for bname,  bucket in self._buckets.items():
            for kname, version in bucket.items():
                yield bname, kname, version

    def __getstate__(self):
        return deepcopy(self._buckets)

    def __setstate__(self, state):
        self._buckets = state
