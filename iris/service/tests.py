import unittest

from .testing.suite import (
    create_suite,
    create_crate_suite,
    create_crate_doc_suite,
)


def test_suite():
    s = unittest.TestSuite((
        create_suite('db/dc.rst'),
        create_suite('rest/service.rst'),
        create_suite('rest/mapper.rst'),
        create_suite('rest/document.rst'),

        create_crate_suite('petition/document.rst'),
        create_crate_suite('petition/service.rst'),
        create_crate_doc_suite('petitions.rst'),

        create_crate_suite('user/document.rst'),
        create_crate_suite('user/service.rst'),

        create_suite('sm/sm.rst'),
        create_suite('static.rst'),

        create_crate_suite('testing/buildsamples.rst',
                           level=99
                          ),
        ))
    return s
