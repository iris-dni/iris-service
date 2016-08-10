import unittest

from .testing.suite import (
    create_suite,
    create_crate_suite,
    create_crate_doc_suite,
    create_doc_suite,
)


def test_suite():
    s = unittest.TestSuite((
        create_suite('db/dc.rst'),
        create_suite('rest/service.rst'),
        create_suite('rest/mapper.rst'),
        create_suite('rest/document.rst'),
        create_suite('rest/swagger.rst'),

        create_crate_suite('petition/document.rst'),
        create_crate_suite('petition/service.rst'),
        create_crate_suite('petition/events.rst'),
        create_suite('petition/sm.rst'),
        create_crate_doc_suite('petitions.rst'),

        create_crate_suite('user/document.rst'),
        create_crate_suite('user/service.rst'),

        create_crate_suite('city/document.rst'),
        create_crate_suite('city/service.rst'),
        create_crate_suite('city/import.rst'),

        create_crate_suite('security/security.rst'),

        create_crate_suite('auth/service.rst'),
        create_crate_suite('auth/ssotoken.rst'),
        create_crate_suite('auth/sso.rst'),
        create_crate_suite('auth/views.rst'),
        create_suite('auth/secret.rst'),
        create_doc_suite('sso.rst'),

        create_suite('sm/sm.rst'),
        create_suite('static.rst'),

        create_crate_suite('testing/buildsamples.rst',
                           level=99
                          ),
        ))
    return s
