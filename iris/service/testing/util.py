import sys
import types
import json
import pprint
import functools

from pyramid.testing import DummyRequest

from webtest.response import TestResponse


def print_json(js):
    if isinstance(js, TestResponse):
        js = js.body
    if isinstance(js, types.StringType):
        try:
            d = json.loads(js)
        except ValueError:
            print >> sys.stderr, js
            raise
    else:
        d = js
    print_dict(d)


def print_dict(d):
    print(json.dumps(d,
                     indent=2,
                     sort_keys=True,
                     ensure_ascii=False,
                     separators=(',', ': ')
                     ))


def GET(browser, url):
    print(browser.get(url, expect_errors=True))


def GET_JSON(browser, url):
    response = browser.get(url, expect_errors=True)
    print json.dumps(
        response.json,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def POST(browser, url):
    print(browser.post(url, expect_errors=True))


def get_test_request():
    request = DummyRequest()
    request.remote_addr = '127.0.0.1'
    request._LOCALE_ = 'en'
    return request


def setupGlobs(globs, browser):
    globs['print_json'] = print_json
    globs['print_dict'] = print_dict
    globs['pp'] = print_dict
    globs['pprint'] = pprint.pprint
    globs['get_test_request'] = get_test_request
    # for api documentation HTTP calls
    globs['HTTP_GET'] = functools.partial(GET, browser)
    globs['HTTP_GET_JSON'] = functools.partial(GET_JSON, browser)
    globs['HTTP_POST'] = functools.partial(POST, browser)
