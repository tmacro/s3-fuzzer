from itertools import zip_longest

from .layer import FillLayer, ModifyLayer
from .util.conf import config
from .util.log import Log
from .util.prand import PRNG, iter_prng
from .util.s3 import AClient, ZClient

_log = Log('fuzz')

zenko_client = ZClient()
aws_client = AClient()


def _log_failure(key, otype, a, b):
	_log.error('{type} failed comparison! a[{key}] != b[{key}]'.format(
		type=otype,
		key=key
	))
	_log.error('{a} != {b}'.format(
		a=a[key],
		b=b[key]
	))

TO_CHECK_OBJ = ['Key', 'Size', 'StorageClass']
def _compare_obj(a, b):
	for key in TO_CHECK_OBJ:
		if a[key] != b[key]:
			_log_failure(key, 'Object', a, b)
			return False
	return True

TO_CHECK_DM = ['Key', 'IsLatest']
def _compare_dm(a, b):
	if a['Key'] != b['Key']:
		_log_failure('Key', 'DeleteMarker', a, b)
	elif a.get('IsLatest') != b.get('IsLatest'):
		_log_failure('IsLatest', 'DeleteMarker', a, b)
	else:
		return True
	return False

def compare_obj(a, b):
	if not config.runtime.versioned or 'ETag' in a: # If the obj has Etag its a regular object
		return _compare_obj(a,b)
	else: # If it doesn't it's a DeleteMarker
		return _compare_dm(a,b)


def cleanup(f):
	def inner(*args, **kwargs):
		res = f(*args, **kwargs)
		if config.runtime.cleanup:
			aws_client.cleanup()
			zenko_client.cleanup()
		return res
	return inner

@cleanup
def fuzz(seed, dry_run=False):
	# Fill our bucket with random objects
	zoutput, aoutput = FillLayer(seed).apply(zenko_client, aws_client, dry_run=dry_run)
	# Modify our bucket to create deletemarkers etc
	ModifyLayer(seed).apply(zenko_client, aws_client, zoutput.copy(), aoutput.copy(), dry_run=dry_run)

	prng = PRNG(seed)
	# Grab a random object to construct our prefix from
	obj = prng.choice(list(zoutput.keys()))
	# Now split our objects path and pick a subset to use
	path_segments = obj.split('/')
	to_use = prng.rint(between=(0, len(path_segments) - 1))
	prefix = '/'.join(path_segments[:to_use])
	prefix = ''
	# List versions only when in versioned mode and our prng tells us to
	_log.info('Listing using prefix %s'%prefix)
	list_versions = config.runtime.versioned and False #prng.flip()
	# Now create our lists to compare
	# Since these are generators, no actual API calls have been made yet
	zlist = zenko_client.list(prefix, list_versions, dry_run=dry_run)
	alist = aws_client.list(prefix, list_versions, dry_run=dry_run)
	_log.info('Comparing object listings')
	for i, (zobj, aobj) in enumerate(zip_longest(zlist, alist)):
		if zobj is None:
			_log.error('Zenko listing ended early!')
			_log.error('Next AWS listing entry "%s"'%aobj['Key'])
			return False
		if aobj is None:
			_log.error('Zenko has extra entries!')
			_log.error('Next Zenko listing entry "%s"'%zobj['Key'])
			return False
		_log.info('Comparing %s'%zobj['Key'])
		if not compare_obj(zobj, aobj):
			return False
	return True


def main(seed = None, count = -1, step = 0):
	for subseed in iter_prng(seed, count, step):
		if not fuzz(subseed, config.runtime.dry_run):
			_log.info('Failed listing comparison!, Exiting...')
			return 1
		_log.info('Listing comparison succeeded!')
	_log.info("All fuzzing rounds completed!")
	return 0
