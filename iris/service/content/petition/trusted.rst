====================================
Petition service API Data Management
====================================


    >>> import copy
    >>> from iris.service import rest
    >>> request = get_test_request()

Get the petitions mapper::

    >>> mapper = rest.RESTMapper.getMapperImplementation('petitions', request)

Create a User::

    >>> user1 = creators.user(email="user1@iris.com", lastname="user1")


Owner Id Management
===================

We start with a session user::

    >>> from iris.service.content.user import SessionUser
    >>> request.session_user = SessionUser()
    >>> request.user = None

Creating a new petition will add the session user id to the owner property of
the incoming data::

    >>> data = {
    ...     "owner": {
    ...     }
    ... }
    >>> mapper._prepare_data(None, data)
    >>> print_json(data)
    {
      "owner": {
        "id": "iris-session:..."
      }
    }


Trusted Flag Management (Incoming Data)
=======================================


For Logged In Users
-------------------

Create a logged in request::

    >>> request.session_user = user1
    >>> request.user = user1


Create a new Petition
^^^^^^^^^^^^^^^^^^^^^

Create new petition (doc paramter is None)::

    >>> data = {
    ...     "owner": {
    ...     }
    ... }
    >>> mapper._prepare_data(None, data)
    >>> print_json(data)
    {
      "owner": {
        "id": "..."
      }
    }

    >>> data = {
    ...     "owner": {
    ...         "mobile": "555 1234",
    ...         "email": "email@iris.com"
    ...     }
    ... }
    >>> mapper._prepare_data(None, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "email@iris.com",
        "id": "1n3gf",
        "mobile": "555 1234"
      }
    }


Edit an Existing Petition
^^^^^^^^^^^^^^^^^^^^^^^^^

For an existing petition the trusted flag is set to false if the data is
changed against the existing petition.

Edit existing petition::

    >>> petition = creators.petition()
    >>> data = {
    ...     "owner": {
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)

The trusted flag is reset::

    >>> print_json(data)
    {
      "owner": {
        "email_trusted": false,
        "mobile_trusted": false
      }
    }

Set data::

    >>> data = {
    ...     "owner": {
    ...         "email": "email@iris.com",
    ...         "mobile": "555 1234"
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "email@iris.com",
        "email_trusted": false,
        "mobile": "555 1234",
        "mobile_trusted": false
      }
    }

We set trusted data on the existing petition::

    >>> petition.owner = {
    ...     "email": "email@iris.com",
    ...     "email_trusted": True,
    ...     "mobile": "555 4321",
    ...     "mobile_trusted": True
    ... }
    >>> _ = petition.store(refresh=True)

With another data as the existing data the trusted flag is set to False::

    >>> data = {
    ...     "owner": {
    ...         "email": "other@iris.com",
    ...         "mobile": "555 1234"
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "other@iris.com",
        "email_trusted": false,
        "mobile": "555 1234",
        "mobile_trusted": false
      }
    }

With the same data as the existing data the trusted flag is not changed::

    >>> data = {
    ...     "owner": {
    ...         "email": "email@iris.com",
    ...         "mobile": "555 4321"
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "email@iris.com",
        "mobile": "555 4321"
      }
    }


For Session User
----------------

Create a session user request::

    >>> request.session_user = SessionUser()
    >>> request.user = None


Create a new Petition
^^^^^^^^^^^^^^^^^^^^^

The trusted flags are not modified in case we have a session user::

    >>> data = {
    ...     "owner": {
    ...         "email": "email@iris.com",
    ...         "mobile": "555 1234"
    ...     }
    ... }
    >>> mapper._prepare_data(None, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "email@iris.com",
        "id": "iris-session:...",
        "mobile": "555 1234"
      }
    }


Edit an Existing Petition
^^^^^^^^^^^^^^^^^^^^^^^^^

Edit existing petition::

    >>> petition = creators.petition()
    >>> data = {
    ...     "owner": {
    ...         "email": "email@iris.com",
    ...         "mobile": "555 1234"
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "email@iris.com",
        "email_trusted": false,
        "mobile": "555 1234",
        "mobile_trusted": false
      }
    }

The session owner is assigned to the petition document::

    >>> print_json(petition.owner.relation_dict)
    {
      "class": "User",
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "iris-session:...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "",
      "town": "",
      "zip": ""
    }

Change a already assigned data::

    >>> petition.owner = {
    ...     "email": "new@iris.com",
    ...     "mobile": "555 1234",
    ... }
    >>> _ = petition.store(refresh=True)
    >>> data = {
    ...     "owner": {
    ...         "email": "email@iris.com",
    ...         "mobile": "555 2345"
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "email@iris.com",
        "email_trusted": false,
        "mobile": "555 2345",
        "mobile_trusted": false
      }
    }

If the already set data is provided the trusted flag is not affected::

    >>> data = {
    ...     "owner": {
    ...         "email": "new@iris.com",
    ...         "mobile": "555 1234"
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)
    >>> print_json(data)
    {
      "owner": {
        "email": "new@iris.com",
        "mobile": "555 1234"
      }
    }


Trusted Flag Management (Before Store)
======================================

This is the code called after a new petition has been created or an existing
petition was edited. Here the trusted flags are synchronized between the
realtion and the owner.

A helper to prepare a petition before calling _prepare_document::

    >>> def prepare_petition(petiton, data):
    ...     mapper._prepare_data(petition, data)
    ...     for name, value in data.items():
    ...         setattr(petition, name, value)


For Logged in Users
-------------------

Create a new user without trust data::

    >>> user2 = creators.user(email="user2@iris.com", lastname="user2")

Create a logged in request::

    >>> request.session_user = user2
    >>> request.user = user2

Create a petition and prepare it for the user::

    >>> petition = creators.petition()
    >>> data = {
    ...     "owner": {
    ...         "email": "email@iris.com",
    ...         "mobile": "555 1234"
    ...     }
    ... }
    >>> prepare_petition(petition, data)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "email": "email@iris.com",
      "email_trusted": false,
      ...
      "mobile": "555 1234",
      "mobile_trusted": false,
      ...
    }
    
    >>> mapper._prepare_document(petition, data, is_create=False)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "email": "email@iris.com",
      "email_trusted": false,
      ...
      "mobile": "555 1234",
      "mobile_trusted": false,
      ...
    }

Set trusted data on the user::

    >>> user2.email = "new@iris.com"
    >>> user2.email_trusted = True
    >>> user2.mobile = "555 4321"
    >>> user2.mobile_trusted = True
    >>> _ = user2.store(refresh=True)

Provide the same data as the user already has::

    >>> petition = creators.petition()
    >>> data = {
    ...     "owner": {
    ...         "email": "new@iris.com",
    ...         "mobile": "555 4321"
    ...     }
    ... }
    >>> prepare_petition(petition, data)
    >>> mapper._prepare_document(petition, data, is_create=False)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "email": "new@iris.com",
      "email_trusted": true,
      ...
      "mobile": "555 4321",
      "mobile_trusted": true,
      ...
    }

Provide a different data as the user already has::

    >>> petition = creators.petition()
    >>> data = {
    ...     "owner": {
    ...         "email": "email@iris.com",
    ...         "mobile": "555 1234"
    ...     }
    ... }
    >>> prepare_petition(petition, data)
    >>> mapper._prepare_document(petition, data, is_create=False)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "email": "email@iris.com",
      "email_trusted": false,
      ...
      "mobile": "555 1234",
      "mobile_trusted": false,
      ...
    }


For Session User
----------------

Create a session user request::

    >>> request.session_user = SessionUser()
    >>> request.user = None

Create a petition and prepare it for the session user::

    >>> petition = creators.petition()
    >>> data = {
    ...     "owner": {
    ...     }
    ... }
    >>> mapper._prepare_data(petition, data)
    >>> before_data = copy.deepcopy(data)
    >>> before_rel_dict = petition.owner.relation_dict

    >>> mapper._prepare_document(petition, data, is_create=True)
    >>> before_data == data
    True
    >>> before_rel_dict == petition.owner.relation_dict
    True
