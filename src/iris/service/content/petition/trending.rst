==================
Trending Petitions
==================

Create some sampledata::

    >>> samples.users(30)
    >>> samples.cities(30)

    >>> from datetime import datetime, timedelta
    >>> samples.petitions(
    ...     30,
    ...     timerange=(
    ...         datetime.now() - timedelta(days=6 * 30),
    ...         datetime.now()
    ...     )
    ... )


Request Trending Petitions
--------------------------

A sort for "trending" provides trending petitions::

    >>> response = browser.get('/v1/petitions?sort=trending&limit=20')
    >>> response.json['total']
    20

To test different trending settings the 'trending' parameter can be used::

    >>> response = browser.get('/v1/petitions?trending=7,90,7')
    >>> response.json['total']
    10

    >>> response = browser.get('/v1/petitions?trending=7,14,7&limit=20')
    >>> response.json['total']
    14

    >>> response = browser.get('/v1/petitions?trending=1,1,1')
    >>> response.json['total']
    2

    >>> response = browser.get('/v1/petitions?trending=1,1,0')
    >>> response.json['total']
    2
