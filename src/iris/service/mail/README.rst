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

    >>> from iris.service import mail
    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "url": "http://www.petitio.ch"
            },
            "name": "confirm"
          },
          {
            "content": {
              "url": "http://test.iris.ch"
            },
            "name": "portal"
          }
        ],
        "merge_vars": [
          {
            "rcpt": "voter@iris.com",
            "vars": [
              {
                "content": {
                  "email": "voter@iris.com",
                  "firstname": "Top",
                  "lastname": "Voter"
                },
                "name": "user"
              }
            ]
          }
        ],
        "to": [
          {
            "email": "voter@iris.com",
            "name": "Top Voter",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-mailconfirmation"
    }
