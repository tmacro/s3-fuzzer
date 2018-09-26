import boto3
import botocore
from botocore.config import Config


from .conf import config
from .file import FakeFile

s3_config = Config(retries = dict(
    max_attempts = 5
))

ZENKO_HOST = getattr(config.zenko, 'host', None)
ZENKO_ACCESS_KEY = getattr(config.zenko, 'access_key', None)
ZENKO_SECRET_KEY = getattr(config.zenko, 'secret_key', None)

assert(ZENKO_HOST is not None and ZENKO_ACCESS_KEY is not None and ZENKO_SECRET_KEY is not None)

def build_zenko_client():
    return boto3.client('s3', endpoint_url = ZENKO_HOST, config = s3_config,
            aws_access_key_id = ZENKO_ACCESS_KEY, aws_secret_access_key=ZENKO_SECRET_KEY)

def build_aws_client():
    return boto3.client('s3', config = s3_config,
            aws_access_key_id = config.aws.access_key, aws_secret_access_key=config.aws.secret_key)
