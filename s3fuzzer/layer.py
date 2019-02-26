import math
from collections import OrderedDict

from .util.conf import config
from .util.log import Log
from .util.prand import PRNG

_log = Log('layer')

class Layer:
	def __init__(self, seed):
		self._prng = PRNG(seed)

	def apply(self, client):
		return {}, {}


class FillLayer(Layer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._log = _log.getChild('fill')

	def _gen_prefix(self, prev=None):
		"""Generate a random prefix of random depth for a object ei fhjgklhgjeoivfj/fjs/euejd
		Optionaly takes a example prefix and uses a random contiguous subset of its segments when constructing the new prefix
		"""
		base=''
		# If a previous path is given, split it then choose segments to reuse
		if prev is not None:
			segs = prev.split('/')
			to_reuse = self._prng.rint(between=(0, len(segs) - 1))
			base = '/'.join(segs[:to_reuse])
		self._log.debug('Using "%s" as base path'%base)
		# How much are we starting with
		base_len = len(base)
		# How many new segments to add
		_log.debug('Choosing between 0 and %s prefixes'%config.objects.prefix.max)
		prefix_count = self._prng.rint(
			between=(
				0,
				config.objects.prefix.max
			)
		)
		if not prefix_count:
			return base
		self._log.debug('Creating %s prefixes'%prefix_count)
		# Our max len for each prefix = (max obj name len - length of reused - num of prefixes) / num of prefixes - 1
		#            915 max prefix length
		#     - base_len what we already used
		# - prefix_count how many `/` we're gonna have
		# / prefix_count how many prefixes we have
		#            - 1 for edges cases I haven't thought of yet
		max_len = math.floor((915 - base_len - prefix_count)/prefix_count) - 1
		self._log.debug('Max prefix length is %s'%max_len)
		# Generate a str of length < max_len for each prefix, then join with '/'
		return '/'.join([base] + [
			self._prng.rstr(
				self._prng.rint(between=(1, max_len))
			) for x in range(prefix_count)])

	def _gen_obj_name(self, prefix):
		"""Generate a random object name from the space left over"""
		prefix_len = len(prefix)
		return self._prng.rstr(self._prng.rint(between=(1, 915 - prefix_len - 1)))

	def _gen_objs(self, count):
		"""Generate randomly named object/prefix combos"""
		# Generate a base prefix to help with generating nested prefixes
		# Think of it as a empty directory tree with only a "trunk" and no branches
		# And we'll pick random levels and insert "branches" ei new files/subdirectories
		base_prefix = self._gen_prefix()
		self._log.debug('Using base prefix %s'%base_prefix)
		for x in range(count):
			prefix = self._gen_prefix(base_prefix)
			name = self._gen_obj_name(prefix)
			yield '/'.join([prefix, name])


	def apply(self, client1, client2, dry_run=False):
		"""Generate a random amount of object names/prefixes and upload each"""
		# Create our output logs for each client
		output_1 = OrderedDict()
		output_2 = OrderedDict()
		# Decide how many objects we need
		num_objects = self._prng.rint(
			between=(
				config.objects.count.min,
				config.objects.count.max
			)
		)
		self._log.info('Generating %s objects'%num_objects)
		# And how he max number of versions. If versioning is disabled just do 1
		max_versions = config.objects.versions.max if config.runtime.versioned else 1
		for path in self._gen_objs(num_objects):
			for version in range(self._prng.rint(between=(1, max_versions))):
				# Our client returns  the version id which we'll need for later
				# So insert it at the head of the version list
				# Do this for each client
				ver_id = client1.upload(path, dry_run)
				if path not in output_1:
					output_1[path] = [ver_id]
				else:
					output_1[path].insert(0, ver_id)
				ver_id = client2.upload(path, dry_run)
				if path not in output_2:
					output_2[path] = [ver_id]
				else:
					output_2[path].insert(0, ver_id)
		return output_1, output_2

class ModifyLayer(Layer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._log = _log.getChild('modify')

	def _rand_key(self, output):
		"""Returns a random object and version"""
		obj = self._prng.choice(list(output.keys()))
		return obj

	def apply(self, zclient, aclient, zup, aup, dry_run=False):
		for _ in range(config.transform.min, config.transform.max):
			# For each tansformation, pick a random object
			obj = self._rand_key(zup)
			delete_master = True
			if config.runtime.versioned: # If this is a versioned bucket, flip to see if we delete the master or not
				delete_master = self._prng.flip()
			zver = None
			aver = None
			ver_index = None
			if not delete_master and zup[obj]: # If we should delete a version and we have some to delete
				ver_index = self._prng.rint(between=(0, len(zup[obj]) - 1)) # Pick one
				zver = zup[obj][ver_index] # And save them
				aver = aup[obj][ver_index]
			# Then delete that version
			zclient.delete(obj, zver, delete_master, dry_run)
			aclient.delete(obj, aver, delete_master, dry_run)
			# And remove the version from our list
			if ver_index:
				zup[obj].pop(ver_index)
				aup[obj].pop(ver_index)
