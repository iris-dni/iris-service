==============
Sample Service
==============

The sample service is just a place holder to have a working endpoint for the
minimal package definition.

Call the sample service::

    >>> res = browser.get('/v1/sample')
    >>> print_json(res)
    {
        "hello": "blub!"
    }
