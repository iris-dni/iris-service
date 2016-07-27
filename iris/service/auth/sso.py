import jsonschema

from iris.service.user import User

from .secret import verify_message, get_message_data

from .ssotoken import SSOToken


def _sso_data(request):
    """Get sso data from the request

    SSO data can be provided using 'sso' or 'token' parameter via
    swagger_data. If one of these parameters is provided 'apikey' must also be
    in swagger_data.

    If the 'token' is provided the token is expanded into the sso data. The
    token is no longer valid after the call to this method.
    """
    sso = request.swagger_data.get('sso')
    token = request.swagger_data.get('token')
    if (sso is None) == (token is None):
        return None
    if token is not None:
        # resolve the token
        data = SSOToken.resolve(token)
        if data is None:
            return None
        sso, apikey = data
    else:
        # the apikey must be provided by the request
        apikey = request.swagger_data.get('apikey')
        if apikey is None:
            return None
    try:
        verify_message(sso, apikey)
    except (ValueError, KeyError):
        return None
    return get_message_data(sso)


def _user(request):
    """The request method to get the user from the current request

    Is used for the request method `request.user`.
    """
    user_id = request.authenticated_userid
    if not user_id:
        return None
    return User.get(user_id)


def get_or_create_sso_user(credentials):
    """Get or create a user based on SSO credentials

    The SSO credentials are a dict which must contain an `email` and optional
    a `nickname`.
    """
    try:
        jsonschema.validate(credentials, SSO_USER_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        return None
    user_properties = {
        'email': credentials['email'],
        'firstname': credentials.get('firstname'),
        'lastname': credentials.get('lastname'),
        'trusted': credentials.get('trusted'),
        'roles': credentials.get('roles'),
    }
    user_properties = {k: v for k, v in user_properties.iteritems() if v}
    user = User.get_by(User.email, user_properties['email'])
    if not user:
        user = User(**user_properties)
    else:
        user = user[0]
    user.store(refresh=True)
    return user


SSO_USER_SCHEMA = {
    'type': 'object',
    'required': ['email'],
    'properties': {
        'email': {
            'type': 'string',
        },
        'firstname': {
            'type': 'string',
        },
        'lastname': {
            'type': 'string',
        },
        'trusted': {
            'type': 'boolean',
        },
        'roles': {
            'type': 'array',
            'items': {
                'type': 'string',
            }
        },
    }
}


def includeme(config):
    config.add_request_method(_sso_data, "sso_data", reify=True)
    config.add_request_method(_user, "user", reify=True)
