from pyramid import security

from ..security import acl


class BaseAuthFactory(object):

    def __init__(self, request, proxied_object=None):
        self.request = request
        self.context = proxied_object


class AdminServiceAuthFactory(BaseAuthFactory):
    """Allows the admin role the AdminFull permission
    """

    __acl__ = [(security.Allow, acl.Roles.Admin, acl.Permissions.AdminFull)]


class ApiKeyServiceAuthFactory(BaseAuthFactory):
    """Allows access with API key permission only
    """

    __acl__ = [(security.Allow, acl.Roles.ApiKeyUser, acl.Permissions.Edit)]
