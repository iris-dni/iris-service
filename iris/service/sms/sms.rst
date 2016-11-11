===
SMS
===

    >>> from iris.service import sms

sms is set into testing mode and just prints out::

    >>> sms.sendSMS('555 123', 'from test run')
    sendSMS('555 123', 'from test run')
    {}

    >>> sms.sendSMS('+436649636988', 'from test run')
