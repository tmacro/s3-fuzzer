from functools import partial

import boto3
import botocore
from botocore.config import Config

from .conf import config
from .log import Log

_log = Log('util.s3')

default_s3_config = Config(retries=dict(max_attempts=5))

listing_s3_config = Config(
	read_timeout = 30,
	retries = dict(max_attempts=0)
)

# ZENKO_HOST = getattr(config.zenko, 'host', None)
# ZENKO_ACCESS_KEY = getattr(config.zenko, 'access_key', None)
# ZENKO_SECRET_KEY = getattr(config.zenko, 'secret_key', None)

# assert(ZENKO_HOST is not None and ZENKO_ACCESS_KEY is not None and ZENKO_SECRET_KEY is not None)

def build_zenko_client(resource=False, s3_config=default_s3_config):
	factory = boto3.client
	if resource:
		factory = boto3.resource
	return factory('s3', config = s3_config, endpoint_url = config.zenko.host,
			aws_access_key_id = config.zenko.access_key, aws_secret_access_key=config.zenko.secret_key,
			verify=config.runtime.verify_certs)

def build_aws_client(resource=False, s3_config=default_s3_config):
	factory = boto3.client
	if resource:
		factory = boto3.resource
	return factory('s3', config = s3_config,
			aws_access_key_id = config.aws.access_key, aws_secret_access_key=config.aws.secret_key)


class BaseClient:
	_client_factory = None
	_client_bucket = None
	_logger_name = 'base'

	def __init__(self):
		self._client = getattr(self, '_client_factory')()
		self._log = _log.getChild('client').getChild(self._logger_name)

	def delete(self, key, ver, master=True, dry_run=False):
		self._log.debug('Deleting %s'%'master' if master else 'version %s'%ver)
		kwargs = dict(Bucket=self._client_bucket, Key=key)
		if not master:
			kwargs['VersionId'] = ver
		if not dry_run:
			return self._client.delete_object(**kwargs)
	def upload(self, key, dry_run=False):
		self._log.debug('Uploading %s'%key)
		kwargs = dict(Bucket=self._client_bucket, Key=key)
		if not dry_run:
			resp = self._client.put_object(**kwargs, Body=b'')
		if not dry_run and config.runtime.versioned:
			return resp['VersionId']
		else:
			return '6e48b2898190e2f3f376215fd7d473da'

	def _list_versions(self, prefix):
		truncated = True
		next_marker = None
		while truncated:
			kwargs = dict(Bucket=self._client_bucket, Prefix=prefix)
			if next_marker is not None:
				kwargs['Marker'] = next_marker
			resp = self._client.list_objects(**kwargs)
			for obj in resp.get('Contents', []):
				yield obj
			for dm in resp.get('DeleteMarkers', []):
				yield dm
			truncated = resp.get('IsTruncated', False)
			next_marker = resp.get("NextMarker")
			next_version = resp.get('NextVersionIdMarker')
			if truncated and next_marker is None:
				break

	def _list_objects(self, prefix):
		truncated = True
		next_marker = None
		next_ver_marker = None
		while truncated:
			kwargs = dict(Bucket=self._client_bucket, Prefix=prefix)
			if next_marker is not None:
				kwargs['Marker'] = next_marker
			if next_ver_marker is not None:
				kwargs['VersionIdMarker'] = next_ver_marker
			resp = self._client.list_objects(**kwargs)
			for obj in resp.get('Contents', []):
				yield obj
			truncated = resp.get('IsTruncated', False)
			next_marker = resp.get("NextMarker")
			if truncated and next_marker is None:
				break

	def _list_stub(self):
		for x in range(0):
			yield None

	def _list(self, prefix, versions=False, dry_run=False):
		if dry_run:
			return self._list_stub()
		if versions:
			self._log.debug('Listing versions with prefix %s'%prefix)
			return self._list_versions(prefix)
		self._log.debug('Listing objects with prefix %s'%prefix)
		return self._list_objects(prefix)

	def list(self, *args, **kwargs):
		# Since listing bigs can produce API calls that never return
		# We need to use a custom config and client
		old_client = self._client
		self._client = self._client_factory(s3_config=listing_s3_config)
		for obj in self._list(*args, **kwargs):
			yield obj
		self._client = old_client

	def cleanup(self):
		bkt = self._client_factory(resource=True).Bucket(self._client_bucket)
		bkt.object_versions.all().delete()

class ZClient(BaseClient):
	_client_factory = partial(build_zenko_client)
	_client_bucket = config.zenko.bucket
	_logger_name = 'zenko'

class AClient(BaseClient):
	_client_factory = partial(build_aws_client)
	_client_bucket = config.aws.bucket
	_logger_name = 'aws'
