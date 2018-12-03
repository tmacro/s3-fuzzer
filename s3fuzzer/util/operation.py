from .log import Log
from itertools import chain

_log = Log('operation')

def create_object(bucket = None, key = None, content = None, client = None):
    _log.debug('Putting object %s/%s'%(bucket, key))
    return client.put_object(Bucket=bucket, Key=key, Body=content)

def delete_master(bucket, key, client):
    _log.debug('Deleting master %s/%s'%(bucket, key))
    return client.delete_object(Bucket=bucket, Key=key)

def delete_version(bucket, key, version, client):
    _log.debug('Deleting version %s/%s'%(bucket, key))
    return client.delete_object(Bucket=bucket, Key=key, VersionId = version)

def put_placeholder(bucket, key, version, client):
    pass


def _list_objects(bucket, prefix, client, next_marker = None):
    kwargs = dict(Bucket=bucket, Prefix=prefix)
    if next_marker is not None:
        kwargs['Marker'] = next_marker
    resp = client.list_objects(**kwargs)
    return resp, resp.get('NextMarker')

def list_objects(bucket, prefix, client, next_marker = None):
    _log.info('Listing %s/%s'%(bucket, prefix))
    response, next_marker = _list_objects(bucket, prefix, client, next_marker=next_marker)
    if next_marker:
        return [response] + list_objects(bucket, prefix, client, next_marker)
    return [response]

def _list_versions(bucket, prefix, client, next_marker = None, next_ver_marker = None):
    kwargs = dict(Bucket=bucket, Prefix=prefix)
    if next_marker is not None:
        kwargs['KeyMarker'] = next_marker
    if next_ver_marker is not None:
        kwargs['VersionIdMarker'] = next_ver_marker
    resp = client.list_object_versions(**kwargs)
    return resp, resp.get('NextKeyMarker'), resp.get('NextVersionIdMarker')


def list_versions(bucket, prefix, client, next_marker = None, next_ver_marker = None):
    _log.info('Listing versions %s/%s'%(bucket, prefix))
    resp, next_marker, next_ver_marker = _list_versions(bucket, prefix, client, next_marker, next_ver_marker)
    if next_marker or next_ver_marker:
        return [resp] + list_versions(bucket, prefix, client, next_marker, next_ver_marker)
    return [resp]
