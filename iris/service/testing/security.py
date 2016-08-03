import json
import urllib

from webtest import TestApp

from iris.service.auth.secret import sign_message

from iris.service.security import acl
from iris.service.user import User


LOGIN_URL = '/v1/auth/ssologin'
APIKEY = 'local'

EMAIL = "security@app.local"
USER_DATA = {
    "email": EMAIL,
    "firstname": "Role",
    "lastname": "Checker",
}


def ssologin(browser, sso_data=None):
    if sso_data is None:
        sso_data = USER_DATA
    sso = sign_message(sso_data, APIKEY)
    url = (LOGIN_URL +
           '?' +
           urllib.urlencode({"sso": sso, "apikey": APIKEY})
          )
    response = browser.post_json(url)
    return User.get(response.json['data']['id'])


class RoleChecker(object):
    """Class to check urls with all roles

    An instance of this RoleChecker is passed to the test environment and can
    be used this way::

        >>> check_roles("GET", "/v1/admin/users")  # noqa
        Anonymous                               deny
        Authenticated                           deny
        admin:usermanager                       allow

    It's possible to pass a hook function to `check_roles`. This function is
    executed before each request. The result of the hook will be used for
    string substitution on the url. This is useful when checking DELETE
    endpoints::

        >>> def tmp():
        ...     # do something
        ...     return {"id": "123"}
        >>> check_roles("DELETE", "/api/v1/admin/users/%(id)s", tmp)  # noqa
        Anonymous                               deny
        Authenticated                           deny
        admin:usermanager                       allow
    """

    def __init__(self, app):
        self.app = app
        self.roles = [getattr(acl.Roles, r).split(':', 1)[-1]
                      for r in dir(acl.Roles)
                      if not r.startswith("__")]

    def __call__(self, method, url, hook=None, json_body=None):
        if json_body is not None:
            json_body = json.dumps(json_body)
        self.testapp = TestApp(self.app)
        self.request("Anonymous", url, method, hook, json_body)
        self.login()
        self.request("Authenticated", url, method, hook, json_body)
        for role in self.roles:
            self.assign_role(role)
            self.request(role, url, method, hook, json_body)
        self.remove_user()

    def create_user(self):
        self.user = User(**USER_DATA)
        self.user.store(refresh=True)
        self.user_id = self.user.id

    def remove_user(self):
        self.user = User.get(self.user_id)
        self.user.delete(refresh=True)

    def assign_role(self, role):
        self.user = User.get(self.user_id)
        roles = [role]
        self.user.roles = roles
        self.user.store(refresh=True)

    def login(self):
        self.user = ssologin(self.testapp, {'email': EMAIL})
        self.user_id = self.user.id

    def request(self, role, url, method, hook, json_body):
        subst = {}
        if hook:
            if isinstance(hook, dict):
                hk = hook.get('hook')
                options = hook.get('options', None)
                if options and options.get('pass_request_args', False):
                    subst = hk(self, role, url, method, json_body)
                else:
                    subst = hk()
            else:
                subst = hook()
        kws = {}
        if json_body:
            kws = {
                "content_type": "application/json",
                "body": json_body
            }
        r = self.testapp.request(url % subst,
                                 method=method,
                                 expect_errors=True,
                                 **kws)
        state = r.status_code == 403 and "deny" or r.status  # "allow"
        print "%s%s%s" % (role, " " * (40 - len(role)), state)
