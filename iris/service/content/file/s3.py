import boto3
import botocore
import logging

from .document import StorageType
from .tempstorage import store_temp_file, get_temp_file

logger = logging.getLogger(__name__)

AWS_CLIENT_CONFIG = {}
BUCKET_NAME = None


def upload(iid, file_obj):
    """Upload a file to S3.

    Returns the storage type `s3` on success or None on a failure.

    For local/testing environments the file is stored in a temp folder and the
    storage type `tmp` is returned.
    """
    if AWS_CLIENT_CONFIG and BUCKET_NAME:
        try:
            s3 = boto3.resource('s3', **AWS_CLIENT_CONFIG)
            s3.Bucket(BUCKET_NAME).put_object(Key=iid, Body=file_obj)
            return StorageType.S3
        except botocore.exceptions.ClientError as e:
            logger.error(e)
    else:
        # store locally in temp dir (tests, local development)
        store_temp_file(iid, file_obj)
        return StorageType.TMP
    return None


def fetch(iid):
    """Get a file from S3.
    """
    if AWS_CLIENT_CONFIG and BUCKET_NAME:
        try:
            s3 = boto3.resource('s3', **AWS_CLIENT_CONFIG)
            obj = s3.Bucket(BUCKET_NAME).Object(iid).get()
            if obj:
                return obj.get('Body')
        except botocore.exceptions.ClientError as e:
            logger.error(e)
    else:
        # get locally from temp dir (tests, local development)
        return get_temp_file(iid)
    return None


def get_s3_url(iid):
    """Get the S3 url.
    """
    return "https://s3.%s.amazonaws.com/%s/%s" % (
        AWS_CLIENT_CONFIG['region_name'],
        BUCKET_NAME,
        iid
    )


def includeme(config):
    global AWS_CLIENT_CONFIG, BUCKET_NAME
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if key == 'aws.s3.bucket_name':
            BUCKET_NAME = value
        elif key.startswith('aws.s3.'):
            AWS_CLIENT_CONFIG[key[7:]] = value
