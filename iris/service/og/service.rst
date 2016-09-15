=================================
REST API for the /ogcheck service
=================================

The ogcheck service allows to analyse an URL and extract the page's Open Graph
tags. The service returns an object containing the found valid Open Graph tags.


Check a URL and get the Open Graph tags
=======================================

Lets simulate a call of the ogcheck endpoint to get all `og:tags`
provided by the given url::

    >>> test_url = 'http://iristest.com/cool-article'
    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/cool-article-special"/>
    ... <meta property="og:title" content="Rönaldo is back"/>
    ... <meta property="og:site_name" content="Fresh Football News"/>
    ... <meta property="og:description" content="Believe it or not, Rönaldo is back in town"/>
    ... <meta property="og:image" content="http://cdn.test.me/ronaldo-is-back.jpg"/>
    ... </head>
    ... <body>You love Football, so do we</body>
    ... </html>
    ... '''

    >>> import os
    >>> here = os.path.dirname(__file__)
    >>> img_file = open(os.path.join(here, "../testing/blobs/iptc.jpeg"))
    >>> img_content = img_file.read()

    >>> from httmock import all_requests, response, HTTMock, urlmatch
    >>> @urlmatch(path=r'.*ronaldo-is-back.*')
    ... def img_res(url, request):
    ...     headers = {'content-type': 'image/jpeg'}
    ...     return response(200, img_content, headers, None, 5, request)
    >>> @urlmatch(path='/favicon.ico')
    ... def favicon(url, request):
    ...     headers = {'content-type': 'image/x-icon'}
    ...     return response(404, 'ico', headers, None, 5, request)
    >>> @urlmatch(path='/cool-article')
    ... def test_res(url, request):
    ...     return response(200, test_body, None, None, 5, request)

    >>> with HTTMock(img_res, favicon, test_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
      "data": {
        "description": "Believe it or not, Rönaldo is back in town",
        "image": "http://cdn.test.me/ronaldo-is-back.jpg",
        "image_data": {
          "height": 1,
          "width": 1
        },
        "site_name": "Fresh Football News",
        "title": "Rönaldo is back",
        "url": "http://test.me/cool-article-special"
      },
      "status": "ok"
    }

It is also possible to check urls without `http` scheme::

    >>> test_url = 'www.iristest.com/cool-article'

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
      "data": {
        "description": "Believe it or not, Rönaldo is back in town",
        "image": "http://cdn.test.me/ronaldo-is-back.jpg",
        "image_data": {
          "height": 1,
          "width": 1
        },
        "site_name": "Fresh Football News",
        "title": "Rönaldo is back",
        "url": "http://test.me/cool-article-special"
      },
      "status": "ok"
    }

If the URL provides a damaged page with broken html, the code does not fail::

    >>> test_body = '''
    ... <head>
    ... <meta property="og:url" content="http://test.me/cool-article-special"/>
    ... <meta property="og:title" content="Rönaldo is back"/>
    ... <meta property="og:site_name" content="Fresh Football News"/>
    ... <meta property="og:description" content="Believe it or not, Rönaldo is back in town"/>
    ... <meta property="og:image" content="http://cdn.test.me/ronaldo-is-back.jpg"/>
    ... <body You love Football, so do we</body>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
      "data": {
        "description": "Believe it or not, Rönaldo is back in town",
        "image": "http://cdn.test.me/ronaldo-is-back.jpg",
        "image_data": {
          "height": 1,
          "width": 1
        },
        "site_name": "Fresh Football News",
        "title": "Rönaldo is back",
        "url": "http://test.me/cool-article-special"
      },
      "status": "ok"
    }

If tags do not exist, they are omitted in the output::

    >>> test_url = 'http://iristest.com/cool-article'
    >>> test_body = '''
    ... <head>
    ... <meta property="og:url" content="http://test.me/cool-article-special"/>
    ... <meta property="og:image" content="http://cdn.test.me/ronaldo-is-back.jpg"/>
    ... <body You love Football, so do we</body>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
        "data": {
            "image": "http://cdn.test.me/ronaldo-is-back.jpg",
            "image_data": {
                "height": 1,
                "width": 1
            },
            "url": "http://test.me/cool-article-special"
        },
        "status": "ok"
    }

All og-tags different than the defined set of tags will be ignored::

    >>> from iris.service.og.og import OG_TAGS
    >>> OG_TAGS
    ['url', 'title', 'site_name', 'description', 'image']

    >>> test_body = '''
    ... <head>
    ... <meta property="og:url" content="http://test.me/cool-article-special"/>
    ... <meta property="og:image" content="http://cdn.test.me/ronaldo-is-back.jpg"/>
    ... <meta property="og:news" content="ignore me"/>
    ... <meta property="og:public" content="ignore me"/>
    ... <body You love Football, so do we</body>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> set(OG_TAGS + ['image_data']).issuperset(set(res.json['data'].keys()))
    True

If the returned og-tags do not contain the url, the given url will be used
for the response instead::

    >>> test_body = '''
    ... <head>
    ... <meta property="og:image" content="http://cdn.test.me/ronaldo-is-back.jpg"/>
    ... <body You love Football, so do we</body>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
        "data": {
            "image": "http://cdn.test.me/ronaldo-is-back.jpg",
            "image_data": {
                "height": 1,
                "width": 1
            },
            "url": "http://iristest.com/cool-article"
        },
        "status": "ok"
    }

The returned url always contains a valid scheme::

    >>> test_body = '''
    ... <head>
    ... <meta property="og:url" content="test.me/cool-article-special"/>
    ... <body You love Football, so do we</body>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
        "data": {
            "url": "http://test.me/cool-article-special"
        },
        "status": "ok"
    }

    >>> test_body = '''
    ... <head>
    ... <meta property="og:image" content="http://cdn.test.me/ronaldo-is-back.jpg"/>
    ... <body You love Football, so do we</body>
    ... </html>
    ... '''
    >>> test_url = 'iristest.com/cool-article'
    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
        "data": {
            "image": "http://cdn.test.me/ronaldo-is-back.jpg",
            "image_data": {
                "height": 1,
                "width": 1
            },
            "url": "http://iristest.com/cool-article"
        },
        "status": "ok"
    }

If no og-tags are returned by the page the response will also not contain a
url::

    >>> test_body = '''
    ... <head>
    ... <body You love Football, so do we</body>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print_json(res.body)
    {
        "data": {},
        "status": "ok"
    }


Failures
--------

If the og check fails, status `og_check_failed` is returned::

    >>> resp = browser.post_json('/v1/og/check',
    ...                          {"url": "http://lovelybrokenurl-invalid.com"},
    ...                          expect_errors=True
    ...                         )
    >>> print_json(resp.body)
    {
      "error": {
        "code": 400,
        "description": "Bad request: og_check_failed"
      }
    }

If a request takes too long status `og_check_failed` is returned as well::

    >>> import time
    >>> def wait_one_sec(request, uri, headers):
    ...     time.sleep(1)
    ...     return (200, headers, "The {} response from {}".format(request.method, uri))
    >>> @urlmatch(path='/long_request')
    ... def test_res_long(url, request):
    ...     time.sleep(1)
    ...     return response(200, "The {} response from {}".format(request.method, url.path), None, None, 5, request)

    >>> from iris.service.og import og
    >>> og.OG_PAGE_CHECK_TIMEOUT = 0.5
    >>> long_request_url = 'http://www.iristest.com/long_request'

    >>> with HTTMock(test_res_long):
    ...     res = browser.post_json('/v1/og/check',
    ...                             {"url": long_request_url},
    ...                             expect_errors=True,
    ...                            )
    >>> print_json(resp.body)
    {
      "error": {
        "code": 400,
        "description": "Bad request: og_check_failed"
      }
    }

If an empty or invalid url is posted, an error is returned::

    >>> print browser.post_json('/v1/og/check', {"url": ""},
    ...                         expect_errors=True)
    Response: 400 Bad Request
    ...
    {"error": {"code": 400, "description": "Bad request: og_check_failed"}}

    >>> print browser.post_json('/v1/og/check', {"url": "http://invalid"},
    ...                         expect_errors=True)
    Response: 400 Bad Request
    ...
    {"error": {"code": 400, "description": "Bad request: og_check_failed"}}

    >>> print browser.post_json('/v1/og/check', {"url": "ftp://google.com"},
    ...                         expect_errors=True)
    Response: 400 Bad Request
    ...
    {"error": {"code": 400, "description": "Bad request: og_check_failed"}}


Image URLS
----------

If the image url is relative, an absolute url with the url tag is built::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me"/>
    ... <meta property="og:image" content="/ronaldo-is-back.jpg"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['image']
    http://test.me/ronaldo-is-back.jpg

The relative URL is on root::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... <meta property="og:image" content="/ronaldo-is-back.jpg"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['image']
    http://test.me/ronaldo-is-back.jpg

The image url is a relative url with a path::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... <meta property="og:image" content="ronaldo-is-back.jpg"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['image']
    http://test.me/test/ronaldo-is-back.jpg

Must also work if the url is not finished by slash::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test"/>
    ... <meta property="og:image" content="ronaldo-is-back.jpg"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['image']
    http://test.me/test/ronaldo-is-back.jpg

If the returned image url results in a status_code different than 200 no
og-tag `image` will be returned::

    >>> @urlmatch(path=r'.*ronaldo-is-back.*')
    ... def img_res_404(url, request):
    ...     headers = {'content-type': 'image/jpeg'}
    ...     return response(404, 'img', headers, None, 5, request)

    >>> with HTTMock(test_res, favicon, img_res_404):
    ...     resp= browser.post_json('/v1/og/check', {"url": test_url})
    >>> "image" in resp.json['data']
    False

If the image url does not point to a location providing content of the type
image/* no og-tag `image` will be returned::

    >>> @urlmatch(path=r'.*ronaldo-is-back.*')
    ... def img_res_wront_content(url, request):
    ...     headers = {'content-type': 'text/html'}
    ...     return response(200, 'img', headers, None, 5, request)

    >>> with HTTMock(test_res, favicon, img_res_404):
    ...     resp= browser.post_json('/v1/og/check', {"url": test_url})
    >>> "image" in resp.json['data']
    False

If the request to fetch the image takes to long the og-tag `image` is also not
included in the response::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test"/>
    ... <meta property="og:image" content="http://www.lovelywarwtest.com/long_request"/>
    ... </head>
    ... </html>
    ... '''

    >>> og.OG_IMAGE_CHECK_TIMEOUT = 0.5

    >>> with HTTMock(test_res, favicon, test_res_long):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> "image" in resp.json['data']
    False


Favicons
--------

The favicon of a page providing the article which get checked of og-tags might
be provided by the definition of a link tag with rel="icon" or by the existence of
a favicon.ico in the root of the page::

If the favicon url is relative, an absolute url with the url tag is built::

    >>> test_body = u'''<html>
    ... <head>
    ... <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
    ... <meta property="og:url" content="http://test.me"/>
    ... </head>
    ... </html>
    ... '''

    httpretty.register_uri(httpretty.GET, test_url, body=test_body)

    httpretty.register_uri(httpretty.HEAD,
                           "http://test.me/static/favicon.ico",
                           body="img",
                           content_type='image/x-icon')

    >>> @urlmatch(path='.*favicon.ico')
    ... def favicon(url, request):
    ...     headers = {'content-type': 'image/x-icon'}
    ...     return response(200, 'ico', headers, None, 5, request)

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['favicon']
    http://test.me/static/favicon.ico

The relative URL is on root::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['favicon']
    http://test.me/static/favicon.ico

The favicon url is relative to the url with a path::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... <link rel="icon" href="favicon.ico" type="image/x-icon" />
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['favicon']
    http://test.me/test/favicon.ico

Must also work if the url is not finished by slash::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test"/>
    ... <link rel="icon" href="favicon.ico" type="image/x-icon" />
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['favicon']
    http://test.me/test/favicon.ico

The rel attribute of the link might contain additional values::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... <link rel="shortcut icon" href="/static/favicon.ico" type="image/x-icon" />
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['favicon']
    http://test.me/static/favicon.ico

If no link with rel 'icon' was found the ogcheck tries to find a favicon.ico in
the root of the page::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> print res.json['data']['favicon']
    http://test.me/favicon.ico

If no link tag was found and also no favicon.ico was found in the root the
favicon field is not included in the result::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... </head>
    ... </html>
    ... '''

    >>> @urlmatch(path='.*favicon.ico')
    ... def favicon_404(url, request):
    ...     headers = {'content-type': 'image/x-icon'}
    ...     return response(404, 'ico', headers, None, 5, request)

    >>> with HTTMock(test_res, favicon_404, img_res):
    ...     res = browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in res.json['data']
    False

If the found favicon url results in a status_code different than 200 no
favicon field will be returned. It doesn't matter if the favicon url was one
defined by a link tag or the default one::

    >>> test_body = u'''<html>
    ... <head>
    ... <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
    ... <meta property="og:url" content="http://test.me"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon_404, img_res):
    ...     resp= browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in resp.json['data']
    False

It is ignored if the content-type of the link tag and actual content-type of
the favicon does not match::

    >>> test_body = u'''<html>
    ... <head>
    ... <link rel="icon" href="/static/favicon.ico" type="text/html" />
    ... <meta property="og:url" content="http://test.me"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     resp= browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in resp.json['data']
    True

The returned favicon must be of type image/* ::

    >>> test_body = u'''<html>
    ... <head>
    ... <link rel="icon" href="/statix/favicon.ico" />
    ... <meta property="og:url" content="http://test.me"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     resp= browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in resp.json['data']
    True

    >>> @urlmatch(path='.*favicon.ico')
    ... def favicon_wrong_type(url, request):
    ...     headers = {'content-type': 'text/html'}
    ...     return response(404, 'ico', headers, None, 5, request)

    >>> with HTTMock(test_res, favicon_wrong_type, img_res):
    ...     resp= browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in resp.json['data']
    False

The default favicon is always checked against content-type image/* ::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon, img_res):
    ...     resp= browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in resp.json['data']
    True

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test/"/>
    ... </head>
    ... </html>
    ... '''

    >>> with HTTMock(test_res, favicon_wrong_type, img_res):
    ...     resp = browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in resp.json['data']
    False

If the request to fetch the favicon takes to long the favicon is also not
included in the response::

    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/test"/>
    ... <link rel="icon" href="http://www.iristest.com/long_request" type="image/x-icon" />
    ... </head>
    ... </html>
    ... '''
    >>> og.OG_FAVICON_CHECK_TIMEOUT = 0.5

    >>> with HTTMock(test_res, test_res_long, img_res):
    ...     resp = browser.post_json('/v1/og/check', {"url": test_url})
    >>> 'favicon' in resp.json['data']
    False


Security
========

Check access permissions::

    >>> check_roles("POST",
    ...             "/v1/og/check",
    ...             json_body={"url": "http://iristest.com/cool-article"})
    Anonymous                               200 OK
    Authenticated                           200 OK
    admin                                   200 OK
    apikey-user                             200 OK
    session-user                            200 OK
