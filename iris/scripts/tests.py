import unittest

from iris.service.testing.suite import (
    create_crate_suite,
    create_suite,
)


def test_suite():
    s = unittest.TestSuite((
        create_suite('../scripts/file_relations.rst'),
        create_crate_suite('../scripts/cleanup_s3.rst'),
        ))
    return s
