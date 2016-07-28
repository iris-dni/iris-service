=============
Swagger Tools
=============


Reduce Dict
===========

View code collets data and needs to return only a subset of the internal data.
To simplify the creation of the response JSON the swagger spec can be used to
extract only the allowed properties.

There is a decorator which can be used to do this job::

    >>> from iris.service.rest.swagger import swagger_reduce_response


Reduce Mapping
--------------

This internal method takes a mapping created from the swagger spec and reduces
a dict to contain only the properties defined in the mapping::

    >>> from iris.service.rest.swagger import reduce_mapping

    >>> data = {
    ...     "name": "v1",
    ...     "title": "t1",
    ...     "info": {
    ...        "load": 1,
    ...        "calls": 345,
    ...     },
    ...     "tags": ["swagger", "pyramid"],
    ...     "obj_list": [
    ...         {
    ...             "p1": "11",
    ...             "p2": "12",
    ...         },
    ...         {
    ...             "p2": "22",
    ...         },
    ...         {
    ...             "p3": "33",
    ...         },
    ...     ],
    ... }

A mapping entry with value `True` is copied as is::

    >>> reduce_mapping(
    ...     {
    ...         "name": True
    ...     },
    ...     data
    ... )
    {'name': 'v1'}

A dict defines the properties inside a dict property::

    >>> reduce_mapping(
    ...     {
    ...         "name": True,
    ...         "info": {
    ...             "calls": True,
    ...         },
    ...     },
    ...     data
    ... )
    {'info': {'calls': 345}, 'name': 'v1'}

Properties with value `True` are copied thru as is. Here the info dict is
copied to the output::

    >>> reduce_mapping(
    ...     {
    ...         "name": True,
    ...         "info": True,
    ...     },
    ...     data
    ... )
    {'info': {'load': 1, 'calls': 345}, 'name': 'v1'}

Arrays::

    >>> pp(reduce_mapping(
    ...     {
    ...         "tags": True,
    ...         "obj_list": [{
    ...             "p1": True,
    ...             "p2": True
    ...         }],
    ...     },
    ...     data
    ... ))
    {
      "obj_list": [
        {
          "p1": "11",
          "p2": "12"
        },
        {
          "p2": "22"
        },
        {}
      ],
      "tags": [
        "swagger",
        "pyramid"
      ]
    }


Build Spec Mapping
------------------

Build a dict which contains the properties defined in a swagger spec::

    >>> sample_spec = {
    ...     'description': 'Response body providing the private user data wrapped in a data property.',
    ...     'properties': {'data': {'allOf': [{'discriminator': 'userType',
    ...                                        'properties': {'dc': {'properties': {'created': {'description': 'ISO8601',
    ...                                                                                         'format': 'dateTime',
    ...                                                                                         'type': 'string'},
    ...                                                                             'modified': {'description': 'ISO8601',
    ...                                                                                          'format': 'dateTime',
    ...                                                                                          'type': 'string'}},
    ...                                                              'readOnly': True,
    ...                                                              'type': 'object'},
    ...                                                       'id': {'readOnly': True,
    ...                                                              'type': 'integer'},
    ...                                                       'state': {'default': 'draft',
    ...                                                                 'readOnly': True,
    ...                                                                 'type': 'string'}},
    ...                                        'type': 'object'},
    ...                                       {'description': 'additional sso information which shows all sso connections of the user.',
    ...                                        'properties': {'sso': {'items': {'properties': {'provider': {'type': 'string'},
    ...                                                                                        'trusted': {'type': 'boolean'}},
    ...                                                                         'type': 'object'},
    ...                                                               'readOnly': True,
    ...                                                               'type': 'array'}},
    ...                                        'type': 'object'},
    ...                                       {'allOf': [{'discriminator': 'userType',
    ...                                                   'properties': {'dc': {'properties': {'created': {'description': 'ISO8601',
    ...                                                                                                    'format': 'dateTime',
    ...                                                                                                    'type': 'string'},
    ...                                                                                        'modified': {'description': 'ISO8601',
    ...                                                                                                     'format': 'dateTime',
    ...                                                                                                     'type': 'string'}},
    ...                                                                         'readOnly': True,
    ...                                                                         'type': 'object'},
    ...                                                                  'id': {'readOnly': True,
    ...                                                                         'type': 'integer'},
    ...                                                                  'state': {'default': 'draft',
    ...                                                                            'readOnly': True,
    ...                                                                            'type': 'string'}},
    ...                                                   'type': 'object'},
    ...                                                  {'properties': {'firstname': {'type': 'string'},
    ...                                                                  'lastname': {'type': 'string'}},
    ...                                                   'type': 'object'}],
    ...                                        'description': 'The public properties of a user.',
    ...                                        'type': 'object'},
    ...                                       {'properties': {'email': {'type': 'string'},
    ...                                                       'roles': {'items': {'type': 'string'},
    ...                                                                 'type': 'array'}},
    ...                                        'type': 'object'}],
    ...                             'type': 'object'}},
    ...     'required': ['data'],
    ...     'type': 'object',
    ... }

    >>> from iris.service.rest.swagger import build_spec_mapping
    >>> pp(build_spec_mapping(sample_spec))
    {
      "data": {
        "dc": {
          "created": true,
          "modified": true
        },
        "email": true,
        "firstname": true,
        "id": true,
        "lastname": true,
        "roles": [
          true
        ],
        "sso": [
          {
            "provider": true,
            "trusted": true
          }
        ],
        "state": true
      }
    }
