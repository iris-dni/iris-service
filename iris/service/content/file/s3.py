import boto3
import botocore
import logging
import os


logger = logging.getLogger(__name__)


AWS_CLIENT_CONFIG = {}
BUCKET_NAME = None
TEMP_DIR = None


def upload(iid, file_obj):
    """Upload a file to S3.

    Returns true if successful.
    """
    if AWS_CLIENT_CONFIG and BUCKET_NAME:
        try:
            s3 = boto3.resource('s3', **AWS_CLIENT_CONFIG)
            s3.Bucket(BUCKET_NAME).put_object(Key=iid, Body=file_obj)
            return True
        except botocore.exceptions.ClientError as e:
            logger.error(e)
    elif TEMP_DIR:
        # store locally in temp dir for tests
        store_test_file(iid, file_obj)
        return True
    return False


def fetch(iid):
    if AWS_CLIENT_CONFIG and BUCKET_NAME:
        try:
            s3 = boto3.resource('s3', **AWS_CLIENT_CONFIG)
            obj = s3.Bucket(BUCKET_NAME).Object(iid).get()
            if obj:
                return obj.get('Body')
        except botocore.exceptions.ClientError as e:
            logger.error(e)
    elif TEMP_DIR:
        # get locally from temp dir for tests
        return get_test_file(iid)
    return None


def get_test_upload_path():
    """Get the path for the upload directory and create it if needed.
    """
    path = os.path.join(TEMP_DIR, 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def store_test_file(iid, file_obj):
    """Store the file locally in a temporary location.

    Used for testing environment.
    """
    filename = os.path.join(get_test_upload_path(), iid)
    f = open(filename, 'w')
    f.write(file_obj.read())
    f.close()


def get_test_file(iid):
    """Get a file stored locally in temporary location.

    User for testing environment.
    """
    filename = os.path.join(get_test_upload_path(), iid)
    return open(filename, 'r')


def includeme(config):
    global AWS_CLIENT_CONFIG, BUCKET_NAME, TEMP_DIR
    settings = config.get_settings()
    TEMP_DIR = settings.get('temp.dir', TEMP_DIR)
    for key, value in settings.iteritems():
        if key == 'aws.s3.bucket_name':
            BUCKET_NAME = value
        elif key.startswith('aws.s3.'):
            AWS_CLIENT_CONFIG[key[7:]] = value
