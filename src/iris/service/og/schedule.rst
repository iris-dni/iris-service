===========================
Open Graph Scheduled Worker
===========================

The open graph worker updates WebLocation's without og data::

    >>> from iris.service.og.schedule import Worker

    >>> worker = Worker()
    >>> worker.do_og_update()
    0

Build some mock data for the external requests::

    >>> test_url = 'http://iris__test.com/about'
    >>> test_body = u'''<html>
    ... <head>
    ... <meta property="og:url" content="http://test.me/about"/>
    ... <meta property="og:title" content="All about IRIS"/>
    ... <meta property="og:site_name" content="IRIS grouching page"/>
    ... <meta property="og:description" content="This is the place to grouch"/>
    ... <meta property="og:image" content="http://cdn.test.me/about_iris.jpg"/>
    ... </head>
    ... <body></body>
    ... </html>
    ... '''

    >>> import os
    >>> here = os.path.dirname(__file__)
    >>> img_file = open(os.path.join(here, "../testing/blobs/iptc.jpeg"))
    >>> img_content = img_file.read()

    >>> from httmock import response, HTTMock, urlmatch
    >>> @urlmatch(path=r'/about_iris.jpg')
    ... def img_res(url, request):
    ...     headers = {'content-type': 'image/jpeg'}
    ...     return response(200, img_content, headers, None, 5, request)
    >>> @urlmatch(path='/favicon.ico')
    ... def favicon(url, request):
    ...     headers = {'content-type': 'image/x-icon'}
    ...     return response(404, 'ico', headers, None, 5, request)
    >>> @urlmatch(path='/about')
    ... def test_res(url, request):
    ...     return response(200, test_body, None, None, 5, request)

Create a new WebLocation::

    >>> weblocation = creators.weblocation(url=test_url)
    >>> weblocation.og is None
    True

    >>> with HTTMock(img_res, favicon, test_res):
    ...     worker.do_og_update()
    1

    >>> from iris.service.content.weblocation import WebLocation
    >>> weblocation = WebLocation.mget_urls([weblocation.url])[0]
    >>> print_json(weblocation.og)
    {
      "description": "This is the place to grouch",
      "image": {
        "height": 1,
        "url": "https://proxy/https_proxy?url=http%3A%2F%2Fcdn.test.me%2Fabout_iris.jpg",
        "width": 1
      },
      "site_name": "IRIS grouching page",
      "title": "All about IRIS",
      "ts": ...,
      "url": "http://test.me/about"
    }

Now no update is done::

    >>> worker.do_og_update()
    0

Resetting the og property triggers a new refresh::

    >>> weblocation.og = None
    >>> _ = weblocation.store(refresh=True)
    >>> with HTTMock(img_res, favicon, test_res):
    ...     worker.do_og_update()
    1

Unknown urls::

    >>> weblocation = creators.weblocation(url='http://localhost:42042')
    >>> worker.do_og_update()
    1
    >>> weblocation = WebLocation.mget_urls([weblocation.url])[0]
    >>> print_json(weblocation.og)
    {
      "ts": ...
    }
