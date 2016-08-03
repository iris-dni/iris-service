from pyramid import security

from ..security import acl


class AdminServiceAuthFactory(object):

    def __init__(self, request, proxied_object=None):
        self.request = request
        self.context = proxied_object

    __acl__ = [(security.Allow, acl.Roles.Admin, acl.Permissions.AdminFull)]
