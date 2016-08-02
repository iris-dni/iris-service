=====================
Single Sign On - Flow
=====================

.. contents::

Because authentication is only possible via SSO, a login must use external
SSO Providers to authenticate users.

.. uml::

    @startuml
    Title SSO Login

    actor user
    participant "IRIS-Frontend" as frontend
    participant "SSOProvider" as provider
    participant "IRIS-Login-Embed" as iris
    participant "IRIS-Backend" as backend

    frontend -> backend : whoami (session cookie is used)
    backend -> frontend : whoami: no user
    frontend -> user : show login screen with SSO Providers
    user -> frontend : selected SSO Provider
    frontend -> provider : open provider login page
    provider -> iris : load /v1/views/iris-sso-login.js
    activate iris
    alt no irisreturl provided
      iris -> provider : wait for login
      provider -> user : login page
      user -> provider : enter login data
      user -> provider : login
      provider -> provider : reload login page
    else irisreturl provided
      iris -> backend : whoami
      alt not logged in
        backend -> iris : whoami: no user
        iris -> provider : wait for login
        provider -> user : login page
        user -> provider : enter login data
        user -> provider : login
        provider -> provider : reload login page
      else logged in
        backend -> iris : whoami: user data
        iris -> backend : ssotoken
        backend -> iris : token
        iris -> provider : redirect to iris login endpoint with token
        deactivate iris
        provider -> backend : load login endpoint
        backend -> frontend : redirect to irisreturl
      end
    end
    deactivate iris

    @enduml

The login page of the provider must contain the IRIS embed login code and must
provide the SSO data via the SSOConfig global data.

IRIS embed code checks if the user is already logged in via ``irisConfig``.

If an SSO login is provided the login is made on the IRIS domain and the user
is redirected back to the IRIS frontend.
