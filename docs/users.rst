============
User Service
============

.. contents::

Users are managed in a very minimalistic way, ...


Data
====

.. sourcecode:: json

    {
        "id": "short",
        "status": "published",
        "email": "<id>",
        "firstname": "",
        "lastname": "",
        "sso" [
            {
                "provider": "azmedien",
                "trusted": false
            }
        ]
    }


Get Current User
================

.. http:get:: /v1/auth/whoami

    Provide information about the currently logged in user.

    A user is identified using an authorization cookie.
    If the authorization cookie is not present or not valid the cookie is
    deleted.

    **Example Request**:

    .. sourcecode:: python

        >>> HTTP_GET_JSON('/v1/auth/whoami')
        {
          "data": {
             ...
             trusted: True
          }
        }

    :resheader Content-Type: application/json

    :statuscode 200:
    :statuscode 401:
        - no authorization cookie is provided
        - Body contains an error response structure with the error code

    :>json object data:
        - the result user object

    **Possible Error Codes**:

    .. doctest:: python

        >>> ERROR_CODES('auth_whoami')
        unauthenticated               : This request needs authentication

Content Management API
======================

The management endpoints are only available with a valid authentication.

.. http:get:: /v1/manage/users

    List/Filter users.


.. http:get:: /v1/manage/users/(string:id)

    Provides data for a specific city.

    **Example request**

    >>> HTTP_GET_JSON('/v1/manage/users/1234')

    :responseheader Content-Type: application/json

    :param string id:
        - the id of the city

.. http:post:: /v1/manage/users/(string:id)

.. http:delete:: /v1/manage/users/(string:id)

