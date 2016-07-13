import os
import doctest
import unittest

from pyramid import paster
from webtest import TestApp

from iris.service.testing import util
from iris.service.testing import layer


here = os.path.abspath(os.path.dirname(__file__))
testing_dir = os.path.join(here, 'testing')
conf = os.path.join(testing_dir, 'testing.ini')

default_app = None
app = None


def get_app():
    global default_app, app
    if default_app is None:
        default_app = paster.get_app(conf, 'main')
    app = default_app
    return app


def setUp(test):
    app = get_app()
    testapp = TestApp(app, extra_environ={'REMOTE_ADDR': '127.0.0.1'})
    test.globs['browser'] = testapp
    util.setupGlobs(test.globs, testapp)


def setUpCrate(test):
    setUp(test)
    layer.create_crate_indexes()


def tearDown(test):
    pass


def create_suite(testfile,
                 layer=None,
                 level=None,
                 setUp=setUp,
                 tearDown=tearDown,
                 cls=doctest.DocFileSuite,
                 encoding='utf-8'):
    testfile = os.path.join(testfile)
    suite = cls(
        testfile, setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
        encoding=encoding)
    if layer:
        suite.layer = layer
    if level:
        suite.level = level
    return suite


def create_crate_suite(testfile):
    return create_suite(testfile,
                        layer=layer.crateDBLayer,
                        setUp=setUpCrate,
                       )


def test_suite():
    s = unittest.TestSuite((
        create_crate_suite('petition/document.rst'),
        create_suite('db/dc.rst'),
        create_suite('rest/service.rst'),
        create_suite('rest/mapper.rst'),
        create_suite('rest/document.rst'),
        create_suite('sample/service.rst'),
        create_suite('static.rst'),
        ))
    return s
