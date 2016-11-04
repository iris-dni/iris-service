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
        create_suite('cron/README.rst'),

        create_suite('rest/service.rst'),
        create_suite('rest/mapper.rst'),
        create_suite('rest/document.rst'),
        create_suite('rest/swagger.rst'),
        create_crate_suite('rest/transform.rst'),
        create_crate_suite('rest/extender.rst'),
        create_crate_doc_suite('api.rst'),

        create_crate_suite('elector/election.rst'),

        create_crate_suite('og/service.rst'),
        create_crate_suite('og/schedule.rst'),

        create_suite('sms/sms.rst'),

        create_crate_suite('content/weblocation/document.rst'),
        create_crate_suite('content/weblocation/service.rst'),

        create_crate_suite('content/petition/document.rst'),
        create_crate_suite('content/petition/service.rst'),
        create_crate_suite('content/petition/trending.rst'),
        create_crate_suite('content/petition/flow.rst'),
        create_crate_suite('content/petition/events.rst'),
        create_crate_suite('content/petition/support.rst'),
        create_crate_suite('content/petition/sm.rst'),
        create_crate_suite('content/petition/schedule.rst'),
        create_crate_suite('content/petition/trusted.rst'),
        create_crate_suite('content/petition/confirmation.rst'),
        create_crate_doc_suite('petitions.rst'),

        create_crate_suite('content/user/document.rst'),
        create_crate_suite('content/user/service.rst'),

        create_crate_suite('content/city/document.rst'),
        create_crate_suite('content/city/service.rst'),
        create_crate_suite('content/city/import.rst'),

        create_crate_suite('content/confirmation/document.rst'),
        create_crate_suite('content/confirmation/handler.rst'),
        create_crate_suite('content/confirmation/service.rst'),

        create_crate_suite('content/file/document.rst'),
        create_crate_suite('content/file/service.rst'),
        create_crate_doc_suite('files.rst'),

        create_crate_suite('security/security.rst'),

        create_crate_suite('auth/service.rst'),
        create_crate_suite('auth/ssotoken.rst'),
        create_crate_suite('auth/sso.rst'),
        create_crate_suite('auth/views.rst'),
        create_suite('auth/secret.rst'),
        create_doc_suite('sso.rst'),

        create_suite('sm/service.rst'),
        create_suite('static.rst'),

        create_crate_suite('testing/buildsamples.rst',
                           level=99
                          ),
        ))
    return s
