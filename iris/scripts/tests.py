import unittest

from iris.service.testing.suite import (
    create_crate_suite,
)


def test_suite():
    s = unittest.TestSuite((
        create_crate_suite('../scripts/cleanup_s3.rst'),
        ))
    return s
