=======================
Tests for /probe_status
=======================

The probe_status endpoint is used to check if the service is available.
Load balancers must use the endpoint to check if the service is available.


Check probe_status
==================

An HTTP-GET provides the status::

    >>> print browser.get('/probe_status')
    Response: 200 OK
    Content-Type: text/plain; charset=UTF-8
    OK


Controlling The probe_status
============================

To be able to decommission an application server it is possible to control the
probe_status response. This can be done by posting on the probe_status
endpoint and providing the get parameter "body". "body" can be any string. If
the string is not "OK" the probe_status endpoint will return http status 503
and the "body" parameter as the body if the response::

    >>> print browser.post('/probe_status?body=OFF', expect_errors=True)
    Response: 200 OK
    Content-Type: text/plain; charset=UTF-8
    OFF

From now on the probe_status endpoint provides the body string from the POST
request::

    >>> print browser.get('/probe_status', expect_errors=True)
    Response: 503 Service Unavailable
    Content-Type: text/plain; charset=UTF-8
    OFF

Setting the body to "OK" changes the response status code to 200::

    >>> print browser.post('/probe_status?body=OK', expect_errors=True)
    Response: 200 OK
    Content-Type: text/plain; charset=UTF-8
    OK

    >>> print browser.get('/probe_status', expect_errors=True)
    Response: 200 OK
    Content-Type: text/plain; charset=UTF-8
    OK

