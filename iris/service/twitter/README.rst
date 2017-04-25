===========
Twitter Api
===========


Render Templates
----------------

Template for the twitter message are rendered as jinja templates. The
templates must be provided in the pyramid configuration::

    >>> owner = creators.user(
    ...     firstname="Hoschi",
    ...     lastname="Galoschi",
    ...     email="petition-owner@iris.com",
    ...     email_trusted=True,
    ...     mobile="555 424242",
    ...     mobile_trusted=True,
    ... )
    >>> city = creators.city(
    ...     id="100042",
    ...     provider="test",
    ...     location={"url": "https://www.aargauerzeitung.ch"},
    ...     name="Hornussen",
    ...     treshold=42,
    ... )
    >>> petition = creators.petition(
    ...     owner={
    ...         "id": owner.id,
    ...         "firstname": owner.firstname,
    ...         "lastname": owner.lastname,
    ...     },
    ...     city=city,
    ... )
    >>> request = get_test_request()

We must use the `prepare_petition` method from the mail package to prepare the
jinja data::

    >>> from iris.service.content.petition.mail import prepare_petition
    >>> data = prepare_petition(request, petition)

Now we can render the configured templates::

    >>> from iris.service import twitter
    >>> for message in sorted(twitter.TEMPLATES):
    ...     text = twitter.renderMessage(message, data)
    ...     print message + ':', text
    ...     if len(text) > 140:
    ...         print "text too long"
    active: Unterstützer gesucht! Es gibt eine neue Petition in Hornussen. http://test.iris.ch/petitons/1Zbfk
    closed: Hornussen hat die Petition von Hoschi Galoschi beantwortet. http://test.iris.ch/petitons/1Zbfk
    winner: Hoschi Galoschi hat mit seiner Petition die für Hornussen nötige Anzahl von 42 Stimmen erreicht! http://test.iris.ch/petitons/1Zbfk


Send To Twitter
===============

For the test we have a mock which collects the created messages.

Send a message::

    >>> response = twitter.send('active', data)
    >>> pprint(twitter.API.lastPost())
    {'args': (),
     'kwargs': {'status': u'Unterst\xfctzer gesucht! Es gibt eine neue Petition in Hornussen. http://test.iris.ch/petitons/...'}}
