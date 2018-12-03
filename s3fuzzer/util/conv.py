import itertools
import queue
import random
import urllib.parse as urlparse
from functools import partial
from itertools import starmap

from ..workload import build_workloads
from .log import Log
from .operation import delete_version


def prng(seed):
    r = random.Random()
    r.seed(seed)
    return r

def get_rint(prng, bits = 128):
    return prng.getrandbits(bits)


def iter_prng(seed, count = -1, step = 0):
    _prng = prng(seed)
    for _ in range(step):
        get_rint(_prng)
    for i in itertools.count(step):
        yield get_rint(_prng)
        if count != -1 and i >= count -1:
            break

def enumfilter(f, itr):
    def wrapper(el):
        return f(el[1])
    return filter(wrapper, enumerate(itr))


def empty_queue(q):
    while True:
        try:
            q.get_nowait()
        except queue.Empty:
            break


def enumazip(a, b):
    i = 0
    for x, y in zip(a,b):
        yield i, x, y
        i += 1


_log = Log('conv.compare')

def log_assert(a, b):
    try:
        assert(a == b)
    except AssertionError as e:
        _log.error('Assertion FAILED! %s != %s'%(a, b))
        raise

def check_dict(a, b, keys):
    for k in keys:
        log_assert(a.get(k), b.get(k))
    return True


TO_CHECK_OBJ_LVL = ['Key', 'Size', 'StorageClass']
def condense_obj(obj):
    return {k: obj[k] for k in TO_CHECK_OBJ_LVL}

def condense_contents(cnts):
    condensed = [condense_obj(o) for o in cnts]
    return sorted(condensed, key=lambda k: k['Key'])

def compare_contents(req_a, req_b):
    for obj_a, obj_b in zip(condense_contents(req_a), condense_contents(req_b)):
        for k in TO_CHECK_OBJ_LVL:
            try:
                assert(obj_a[k] == obj_b[k])
            except AssertionError as e:
                _log.error('Listing compare failed! %s != %s'%(obj_a.get(k), obj_b.get(k)))
                _log.error('zenko: %s'%obj_a)
                _log.error('aws: %s'%obj_b)
                raise e
    return True



# TO_CHECK_TOP_LVL = ['IsTruncated', 'Marker', 'Prefix', 'Delimiter', 'MaxKeys', 'CommonPrefixes']
TO_CHECK_TOP_LVL = ['IsTruncated', 'Marker', 'Delimiter', 'MaxKeys', 'CommonPrefixes']
def compare_listing(req_a, req_b):
    assert(urlparse.unquote(req_a['Prefix']) == req_b['Prefix'])
    for key in TO_CHECK_TOP_LVL:
        try:
            assert(req_a.get(key) == req_b.get(key))
        except AssertionError as e:
            _log.error('Listing compare failed! %s != %s'%(req_a.get(key), req_b.get(key)))
            raise e
    try:
        return compare_contents(req_a['Contents'], req_b['Contents'])
    except KeyError:
        if 'Contents' not in req_a and 'Contents' not in req_b:
            return True
        return False



TO_CHECK_DM_LVL = ['Key', 'IsLatest']
def compare_delete_markers(req_a, req_b):
    for dm_a, dm_b in zip(req_a, req_b):
        assert(check_dict(dm_a, dm_b, TO_CHECK_DM_LVL))
    return True

TO_CHECK_VER_LVL = ['Size', 'StorageClass', 'Key', 'IsLatest']
def compare_versions(req_a, req_b):
    for ver_a, ver_b in zip(req_a, req_b):
        assert(check_dict(ver_a, ver_b, TO_CHECK_VER_LVL))
    return True



TO_CHECK_TOP_LVL_VER = ['IsTruncated', 'Name', 'Prefix', 'MaxKeys', 'CommonPrefixes', 'Delimiter']
def compare_version_listing(req_a, req_b):
    assert(check_dict(req_a, req_b, TO_CHECK_TOP_LVL_VER))
    assert(compare_delete_markers(req_a['DeleteMarkers'], req_b['DeleteMarkers']))
    assert(compare_versions(req_a['Versions'], req_b['Versions']))
    return True

def cleanup_bucket(bucket, client_factory):
    bkt = client_factory(True).Bucket(bucket)
    bkt.object_versions.all().delete()
