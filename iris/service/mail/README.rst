======================
Send Mail Via Mandrill
======================


Send Mail
=========

Prepare data::

    >>> to = [
    ...     {
    ...         'email': 'voter@iris.com',
    ...         'firstname': u'Top',
    ...         'lastname': u'Voter',
    ...     }
    ... ]
    >>> data = {
    ...     'confirm': {
    ...         'url': 'http://www.petitio.ch'
    ...     }
    ... }

Now send the mail (note: the test uses a mock sender)::

    >>> from iris.service.mail import send

    >>> result = send('iris-mailconfirmation', to, data)
    {'message': {'global_merge_vars': [{'content': {'url': 'http://www.petitio.ch'},
                                        'name': 'confirm'}],
                 'merge_vars': [{'rcpt': 'voter@iris.com',
                                 'vars': [{'content': {'email': 'voter@iris.com',
                                                       'firstname': u'Top',
                                                       'lastname': u'Voter'},
                                           'name': 'user'}]}],
                 'to': [{'email': 'voter@iris.com',
                         'name': u'Top Voter',
                         'type': 'to'}]},
     'template_content': [],
     'template_name': 'iris-mailconfirmation'}
