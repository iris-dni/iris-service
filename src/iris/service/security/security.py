from pyramid import security

from iris.service.content.user import User
from iris.service.content.user import SessionUser

from . import acl


def groupfinder(user_id, request):
    """Provides the groups based on the currently logged in user

    The group returned is `u:unauthenticated` if no user_id is provided or
    `u:<user_id>` if the user_id is provided. All user roles are added with
    the prefix 'ur:' (user-role).

    Note: the user_id is not checked against the database.
    """
    groups = []
    user = None
    if user_id == acl.Roles.ApiKeyUser:
        groups.append(acl.Roles.ApiKeyUser)
        return groups
    if user_id is not None:
        user = User.get(user_id)
    if user:
        groups.extend([
            security.Authenticated,
            'u:' + str(user.id),
            ]
        )
        # roles stored on the user are prefixed with 'ur:'
        groups.extend(['ur:' + r.strip() for r in user.roles if r.strip()]
                      or [])
        # set the user on the request to make sure no additional database user
        # request is done in method _user.
        request.user = user
    return groups


def login_user(request, response, user=None):
    """Login a user by updating the settings in the response

    The user object provided must provide the property "id".
    """
    if user is None:
        # Create a session user from the iris session cookie or from a new
        # session cookie.
        user_id = get_session_user_id(request)
        user = SessionUser(user_id)
        response.set_cookie('iris-session', user_id)
    headers = security.remember(request, user.id)
    response.headers.extend(headers)
    # Force the user to be available on the request because it was already
    # cached as not logged in.
    request.user = user


def logout_user(request, response):
    """Logout the currently logged in user
    """
    headers = security.forget(request)
    response.headerlist.extend(headers)
    request.user = None


def session_user(user_id):
    """Provide a session user based on the user id

    If the user_id is the id of a session user a SessionUser instance with
    this id is returned.
    """
    return SessionUser.get(user_id)


def get_session_user_id(request):
    user_id = request.cookies.get('iris-session')
    if user_id:
        return user_id
    return SessionUser().id
