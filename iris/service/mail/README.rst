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
    {'message': {'global_merge_vars': [{'content': 'http://www.petitio.ch',
                                        'name': 'confirm_url'}],
                 'merge_vars': [{'rcpt': 'voter@iris.com',
                                 'vars': [{'content': 'voter@iris.com',
                                           'name': 'user_email'},
                                          {'content': u'Top',
                                           'name': 'user_firstname'},
                                          {'content': u'Voter',
                                           'name': 'user_lastname'}]}],
                 'to': [{'email': 'voter@iris.com',
                         'name': u'Top Voter',
                         'type': 'to'}]},
     'template_content': [],
     'template_name': 'iris-mailconfirmation'}


Flatten Dict
============

This is used to flatten nested dict structures to build the variable names for
mandrill::

    >>> from iris.service.mail import flatten_dict

    >>> flatten_dict({})
    {}
    >>> print_json(flatten_dict({
    ...     'a': 1,
    ...     'b': 2,
    ...     'c': {
    ...         '1': 'c1',
    ...         '2': 'c2',
    ...         '3': {
    ...             '1': 'c31',
    ...         }
    ...     }
    ... }))
    {
      "a": 1,
      "b": 2,
      "c_1": "c1",
      "c_2": "c2",
      "c_3_1": "c31"
    }
