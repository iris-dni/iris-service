import sys
from datetime import datetime, timedelta
import logging
import argparse
import boto3
from elasticsearch import helpers
from elasticsearch import Elasticsearch
from elasticsearch.client.utils import _make_path
from elasticsearch.exceptions import NotFoundError

from iris.service.content.file.document import StorageType, File


logger = logging.getLogger('cleanup_s3')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)


class S3Cleaner(object):
    """Cleanup utility for unused files.
    """

    def __init__(self,
                 hosts,
                 min_age,
                 bucket,
                 aws_access_key_id,
                 aws_secret_access_key,
                 region_name,
                 dry_run=False):
        self.min_age = min_age
        self.bucket_name = bucket
        self.dry_run = dry_run

        self.init_boto(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.init_es(hosts)

    def init_boto(self, **kwargs):
        self.s3 = boto3.resource('s3', **kwargs)

    def init_es(self, hosts):
        self.es = Elasticsearch(hosts=hosts)
        File.ES = self.es

    def _in_use(self, file_id):
        """Determine if given file_id is referenced anywhere.

        NOTE: Usage is checked on all indices but only on fields called
              'relations.images.id'. How to determine new relations to Files?
        """
        try:
            exists_query = {
                "query": {"term": {"relations.images.id": file_id}}
            }
            path = _make_path('_all', 'default', '_search', 'exists')
            self.es.transport.perform_request(
                'GET',
                path,
                params=None,
                body=exists_query
            )
            return True
        except NotFoundError:
            return False
        except:
            return True

    def _delete(self, file_id):
        """Delete given file.

        Args:
            file_id: the id (or hash) of the file to delete

        If not dry_run was set delete the file on S3. If successful delete the
        file in elasticsearch. If one file couldn't have been deleted on S3
        an exception will be raised.

        """
        logger.debug("Deleting file %s", file_id)
        if not self.dry_run:
            obj = self.s3.Object(self.bucket_name, file_id)
            obj.delete()
            # this call will raise an exception if the file couldn't have been
            # deleted on S3
            obj.wait_until_not_exists()
            f = File.get(file_id)
            if f:
                f.delete()

    def _s3_files(self):
        """Get all locally known S3 files older than MIN_AGE

        Return a generator over all S3 files
        """
        min_age = datetime.now() - timedelta(days=self.min_age)
        s3_files_query = {
            "fields": [],
            "query": {
                "bool": {
                    "must": [
                        {"term": {"storage_type": StorageType.S3}},
                        {"range": {"dc.created": {"lte": min_age}}}
                    ]
                }
            }
        }
        return helpers.scan(
            self.es,
            query=s3_files_query,
            index=File.INDEX
        )

    def clean(self):
        """Remove all stale files on S3 and in Crate.
        """
        deleted, kept = 0, 0
        for f in self._s3_files():
            f_id = f['_id']
            if not self._in_use(f_id):
                deleted += 1
                self._delete(f_id)
            else:
                kept += 1
                logger.debug("Keep file %s", f_id)
            print "Deleted:\t", deleted, "\tKept:\t", kept, "\r",
            sys.stdout.flush()
        logger.info("Deleted:\t%i\tKept:\t%i", deleted, kept)


def main():
    parser = argparse.ArgumentParser(description='Cleanup unused files.')
    parser.add_argument(
        '--es-hosts',
        required=True,
        dest='hosts',
        help='Comma seperated list of es hosts'
    )
    parser.add_argument(
        '--aws-key',
        dest='aws_access_key_id',
        help='AWS access key'
    )
    parser.add_argument(
        '--aws-secret',
        dest='aws_secret_access_key',
        help='AWS secret key'
    )
    parser.add_argument(
        '--s3-bucket',
        dest='bucket',
        help='The S3 bucket containing files'
    )
    parser.add_argument(
        '--aws-region',
        dest='region_name',
        default='eu-central-1',
        help='AWS region (optional)'
    )
    parser.add_argument(
        '--min-age',
        dest='min_age',
        default=7,
        type=int,
        help='Minimum age of files to delete.'
    )
    parser.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        default=False,
        help='Do a dry run'
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.setLevel(logging.DEBUG)

    args.hosts = args.hosts.split(',')
    cleaner = S3Cleaner(**dict(args._get_kwargs()))
    cleaner.clean()
