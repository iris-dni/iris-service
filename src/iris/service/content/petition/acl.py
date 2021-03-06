from pyramid import security

from iris.service.security import acl
from iris.service.rest.auth import BaseAuthFactory


class PublicPetitionServiceAuthFactory(BaseAuthFactory):
    """Allows the admin role the get access to the full API
    """

    __acl__ = [
        (security.Allow, acl.Roles.Admin, acl.Permissions.AdminPetition)
    ]


class SupportersTokenServiceAuthFactory(BaseAuthFactory):
    """Allows access with API key permission only
    """

    __acl__ = [
        (security.Allow, acl.Roles.Admin, acl.Permissions.ListSupporters),
        (security.Allow, acl.Roles.ApiKeyUser, acl.Permissions.ListSupporters)
    ]
