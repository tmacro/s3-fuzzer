import random
from .util.conf import config
import math
import hashlib
from .util import operation, conv
from functools import partial
from .util.log import Log
from .ds import DeleteMarker
import itertools

_log = Log('generate')

class Payload:
    def __init__(self, seed):
        self._seed = seed

    def _init_prng(self):
        self._prng = conv.prng(self._seed)

    def __repr__(self):
        return '<Payload bucket:%s, prefix:%s, objects:%i>'%(self._bucket_name, self._prefix, self._num_objects)

    def _gen_uuid(self, length):
        a = hashlib.sha256(("%32x" % self._prng.getrandbits(128)).encode('utf-8')).hexdigest()
        return a[:length]

    def _gen_str(self, length):
        s = self._gen_uuid(length)
        if len(s) < length:
            return s + self._gen_str(length - len(s))
        return s[:length]

    def _gen_object_count(self):
        return self._prng.randint(config.objects.count.min, config.objects.count.max)

    def _gen_num_prefixes(self):
        return self._prng.randint(config.objects.prefix.min, config.objects.prefix.max)

    def _gen_prefix(self, count):
        if count == 0:
            return ''
        max_len = math.floor((915 - count)/count) - 1
        return '/'.join([self._gen_str(self._prng.randint(1, max_len)) for x in range(count)])

    def _gen_params(self):
        self._num_objects = self._gen_object_count()
        self._num_prefixes = self._gen_num_prefixes()
        self._prefix = self._gen_prefix(self._num_prefixes)
        _log.info('Using prefix len %i'%len(self._prefix))

    def _gen_object_names(self, count, prefix_len):
        for x in range(count):
            yield self._gen_str(self._prng.randint(1, 915-prefix_len-1))

    def _gen_object_versions(self):
        return self._prng.randint(config.objects.versions.min, config.objects.versions.max)

    def _gen_objs(self):
        for name in self._gen_object_names(self._num_objects, len(self._prefix)):
            yield name, self._gen_object_versions()

    def __call__(self, bucket):
        self._init_prng()
        self._gen_params()
        _log.info('Environment num_object: %i prefix: %s'%(self._num_objects, self._prefix))
        fmt = '%s/%s' if self._prefix else '%s%s'
        for name, versions in self._gen_objs():
            yield partial(operation.create_object,  # Create Master
                            bucket,
                            fmt%(self._prefix, name),
                            b'')
            if config.versioned:
                for v in range(versions):
                    yield partial(operation.create_object,  # Create our versions
                                    bucket,
                                    fmt%(self._prefix, name),
                                    b'')

def generate_payloads(seed, count = -1, step = 0):
    prng = conv.prng(seed)
    for x in range(step):
        conv.get_rint(prng)
    for i in itertools.count(step):
        sd = conv.get_rint(prng)
        pl = Payload(sd)
        yield pl
        if count != -1 and i >= count - 1:
            break


class Transformation:
    def __init__(self, seed, ds):
        self._datastore = ds
        self._seed = seed

    @property
    def _ops(self):
        if config.versioned:
            return (
                operation.delete_master,
                operation.delete_version
            )
        else:
            return (operation.delete_master,)

    def _init_prng(self):
        self._prng = conv.prng(self._seed)

    def _rand_op(self):
        return self._prng.choice(self._ops)

    def _rand_key(self, bucket):
        try:
            return self._prng.choice(list(self._datastore.get(bucket).keys(deleted=False)))
        except IndexError:
            return None

    def _rand_version(self, bucket, key):
        available = self._datastore.get(bucket, key).versions
        if not available:
            return None
        return self._prng.choice(available)

    def rand_op(self, bucket):
        op = self._rand_op()
        key = self._rand_key(bucket)
        if key is None:
            return None
        if op is operation.delete_version:
            version = self._rand_version(bucket, key)
            if not version:
                return self.rand_op(bucket)
            self._datastore.delete_version(bucket, key, version)
            return partial(op, bucket, key, version)
        elif op is operation.delete_master:
            self._datastore.delete_master(bucket, key)
            return partial(op, bucket, key)

    def __call__(self, bucket):
        self._init_prng()
        num_ops = self._prng.randint(config.transform.min, config.transform.max)
        for op in range(num_ops):
            rop = self.rand_op(bucket)
            if rop is not None:
                yield rop



def generate_transormation(seed, ds):
    prng = conv.prng(seed)
    return Transformation(conv.get_rint(prng), ds)


class Test:
    _ops = (
        operation.list_objects,
        operation.list_versions
    ) if config.versioned else (operation.list_objects,)

    def __init__(self, seed, ds):
        self._ds = ds
        self._seed = seed

    def _init_prng(self):
        self._prng = conv.prng(self._seed)

    def _rand_key(self, bucket):
        return self._prng.choice(list(self._ds.get(bucket).keys()))

    def _rand_prefix(self, key):
        lvls = key.count('/')
        lvl = self._prng.randint(0, lvls)
        prefix = '/'.join(key.split('/')[:lvl])
        if prefix: # Every lvl aside from 0 needs a trailing '/' appended
            return prefix + '/'
        return prefix

    def _rand_mode(self):
        return self._prng.choice(self._ops)


    def __call__(self, bucket):
        self._init_prng()
        key = self._rand_key(bucket)
        prefix = self._rand_prefix(key)
        mode = self._rand_mode()
        if mode is operation.list_objects:
            return conv.compare_listing, partial(mode, bucket, prefix)
        elif mode is operation.list_versions:
            return conv.compare_version_listing, partial(mode, bucket, prefix)

def generate_test(seed, ds):
    prng = conv.prng(seed)
    return Test(conv.get_rint(prng), ds)
